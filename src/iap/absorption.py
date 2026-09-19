"""Reward-free target absorption, separate from grounding and evaluation.

The learner sees observations and grounded surrogate targets only. ``updates``
counts optimizer steps / replay insertions, not distinct states or total batch
examples. All three costs are reported.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
from .contracts import Progress, quiet
from .models import InternalFly, state_fingerprint


@dataclass
class AbsorptionReport:
    updates: int = 0
    exposure_draws: int = 0
    batch_examples: int = 0
    unique_states_exposed: int = 0
    losses: list[dict] = field(default_factory=list)
    checkpoints: dict = field(default_factory=dict)
    initial_state_sha256: str = ""
    final_state_sha256: str = ""
    fixed_buffers_unchanged: bool = True
    changed_state_keys: list[str] = field(default_factory=list)
    environmental_rewards: int = 0


def absorb(model: nn.Module, observations: np.ndarray, targets: np.ndarray,
           indices: np.ndarray | None = None, *, updates: int = 512, seed: int = 0,
           learning_rate: float | None = None, batch_size: int = 32,
           checkpoints: tuple[int, ...] = (0, 64, 128, 256, 512, 1024),
           evaluator: Callable[[nn.Module], dict] | None = None,
           progress: Progress = quiet) -> AbsorptionReport:
    x, q = np.asarray(observations, np.float32), np.asarray(targets, np.float32)
    if x.ndim != 2 or q.ndim != 2 or len(x) != len(q) or not np.isfinite(x).all() or not np.isfinite(q).all():
        raise ValueError("Observations and targets must be aligned finite matrices")
    if updates < 0 or batch_size < 1:
        raise ValueError("Invalid absorption budget/batch size")
    indices = np.arange(len(x)) if indices is None else np.asarray(indices, np.int64)
    if indices.ndim != 1 or len(indices) == 0 or np.any((indices < 0) | (indices >= len(x))):
        raise ValueError("No usable training states or invalid state indices")
    if len(set(indices.tolist())) != len(indices):
        raise ValueError("Training-state index support must not contain duplicates")
    lr = learning_rate if learning_rate is not None else (.03 if isinstance(model, InternalFly) else .01)
    if not np.isfinite(lr) or lr <= 0:
        raise ValueError("Learning rate must be finite and positive")
    rng = np.random.default_rng(seed)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    replay: list[int] = []
    before = {k: v.detach().clone() for k, v in model.state_dict().items()}
    buffers_sha = state_fingerprint(model, buffers_only=True)
    report = AbsorptionReport(initial_state_sha256=state_fingerprint(model))
    checks = set(checkpoints) | {0, updates}
    if evaluator is not None:
        report.checkpoints[0] = evaluator(model)
    for step in range(1, updates + 1):
        idx = int(rng.choice(indices))
        replay.append(idx)
        selected = rng.integers(len(replay), size=min(batch_size, len(replay)))
        ids = np.asarray([replay[j] for j in selected], np.int64)
        model.train()
        values = model(torch.tensor(x[ids]))
        if values.shape != q[ids].shape:
            raise ValueError("Model output dimension does not match culture targets")
        loss = F.mse_loss(values, torch.tensor(q[ids]))
        if not torch.isfinite(loss):
            raise FloatingPointError("Non-finite absorption loss")
        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1., error_if_nonfinite=True)
        optimizer.step()
        if hasattr(model, "project"):
            model.project()
        report.updates += 1
        report.exposure_draws += 1
        report.batch_examples += len(ids)
        if step in checks:
            report.losses.append({"update": step, "mse": float(loss.detach())})
            if evaluator is not None:
                report.checkpoints[step] = evaluator(model)
            progress({"event": "absorption_checkpoint", "update": step, "loss": float(loss.detach())})
    report.unique_states_exposed = len(set(replay))
    report.final_state_sha256 = state_fingerprint(model)
    report.fixed_buffers_unchanged = buffers_sha == state_fingerprint(model, buffers_only=True)
    report.changed_state_keys = [k for k, v in model.state_dict().items() if not torch.equal(before[k], v)]
    if isinstance(model, InternalFly):
        if not report.fixed_buffers_unchanged or set(report.changed_state_keys) - {"log_gain"}:
            raise RuntimeError("Fly absorption modified state outside existing-edge log_gain")
    return report
