"""Teacher-side compression and an optional reward-trained teacher rebuild.

No native checkpoint is loaded by transfer recipients. The 97-byte format is
itself a quantized small neural network. Calibration and teacher-side training
costs are not part of that byte count.
"""
from __future__ import annotations
from collections import deque
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
from .packets import CultureCapsule, PolicyPacket
from .tasks import source_support
from .models import predict
from .contracts import Progress, quiet


class TinyPolicy(nn.Module):
    def __init__(self):
        super().__init__()
        self.l1, self.l2 = nn.Linear(6, 8), nn.Linear(8, 2)

    def forward(self, x):
        return self.l2(torch.tanh(self.l1(x)))


def distill(teacher: nn.Module, *, updates: int = 2500, seed: int = 44,
            progress: Progress = quiet) -> tuple[CultureCapsule, dict]:
    if updates < 1:
        raise ValueError("Distillation updates must be positive")
    states, labels = source_support()
    q = predict(teacher, states).astype(np.float32)
    q = q - q.mean(1, keepdims=True)
    q /= max(float(np.max(np.abs(q))), 1e-6)
    with torch.random.fork_rng(devices=[]):
        torch.manual_seed(seed)
        small = TinyPolicy()
    optimizer = torch.optim.Adam(small.parameters(), lr=.03)
    x, y = torch.tensor(states), torch.tensor(q)
    for step in range(updates):
        loss = F.mse_loss(small(x), y)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        if (step + 1) % 500 == 0 or step + 1 == updates:
            progress({"event": "distillation", "update": step + 1, "loss": float(loss.detach())})
    arrays = tuple(p.detach().cpu().numpy() for p in [small.l1.weight, small.l1.bias, small.l2.weight, small.l2.bias])
    policy = PolicyPacket.quantize(arrays)
    capsule = CultureCapsule(policy, states.astype(np.int8).tobytes())
    qpacket = policy(states)
    return capsule, {"distillation_updates": updates, "source_states": 24,
                     "teacher_action_accuracy": float(np.mean(q.argmax(1) == labels)),
                     "packet_teacher_agreement": float(np.mean(qpacket.argmax(1) == q.argmax(1))),
                     "packet_action_accuracy": float(np.mean(qpacket.argmax(1) == labels)),
                     "policy_bytes": len(policy.raw), "capsule_bytes": capsule.payload_bytes,
                     "framed_bytes": len(capsule.to_envelope())}


def train_teacher(model: nn.Module, *, decisions: int = 4096, seed: int = 6101,
                  learning_rate: float = .01, progress: Progress = quiet) -> dict:
    """Archived chosen-action regression with three-decision delayed bookkeeping.

    Samples the 24 states independently; the delay is not a test of recurrent
    memory or temporal credit discovery. Pending rewards are drained at end.
    """
    if decisions < 1 or learning_rate <= 0:
        raise ValueError("Invalid teacher training budget/rate")
    states, labels = source_support()
    rng, rr = np.random.default_rng(seed), np.random.default_rng(seed + 1)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    replay, pending = deque(maxlen=256), deque()
    updates = 0

    def update():
        nonlocal updates
        batch = [replay[j] for j in rr.integers(len(replay), size=min(32, len(replay)))]
        x = torch.tensor(np.stack([b[0] for b in batch]))
        a = torch.tensor([b[1] for b in batch])
        reward = torch.tensor([b[2] for b in batch])
        value = model(x).gather(1, a[:, None]).flatten()
        loss = F.mse_loss(value, reward)
        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1., error_if_nonfinite=True)
        optimizer.step()
        if hasattr(model, "project"):
            model.project()
        updates += 1

    for step in range(decisions):
        idx = int(rng.integers(24))
        with torch.no_grad():
            values = model(torch.tensor(states[idx])).flatten()
            a = int(rng.integers(2)) if rng.random() < .25 else int(values.argmax())
        reward = 1. if a == labels[idx] else -1.
        pending.append((states[idx].copy(), a, reward))
        if len(pending) > 3:
            replay.append(pending.popleft())
            update()
        if (step + 1) % 512 == 0:
            progress({"event": "teacher_learning", "decisions": step + 1})
    while pending:
        replay.append(pending.popleft())
        update()
    pred = predict(model, states).argmax(1)
    return {"decisions": decisions, "optimizer_updates": updates,
            "action_accuracy": float(np.mean(pred == labels)),
            "sequence_accuracy": float(np.all((pred == labels).reshape(8, 3), axis=1).mean())}
