"""Recipient backends. These architectures are not parameter/compute matched.

InternalFly is the archived normalized tanh rate circuit, not a spiking fly
simulation. Its dynamic state is reset for each observation. Only log_gain is
trainable; the signed graph, input projection and motor readout remain fixed.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
import hashlib
from pathlib import Path
import numpy as np
from scipy import sparse
import torch
from torch import nn
from .resources import asset


class InternalFly(nn.Module):
    def __init__(self, graph_path: str | Path, seed: int = 0, inputs: int = 6,
                 actions: int = 2, n: int = 256, steps: int = 6):
        super().__init__()
        if not 1 <= inputs <= 256 or not 2 <= actions <= 16 or n != 256 or steps < 1:
            raise ValueError("Unsupported internal-fly dimensions")
        graph = sparse.load_npz(graph_path).tocsr()[:n, :n].copy()
        if graph.shape != (n, n) or not np.isfinite(graph.data).all():
            raise ValueError("Graph must contain a finite 256x256 subgraph")
        graph.sum_duplicates()
        graph.eliminate_zeros()
        row, col = graph.nonzero()
        base = graph.data.astype(np.float32)
        norm = np.asarray(abs(graph).sum(1)).ravel().astype(np.float32)
        base = base / np.maximum(1., norm[row]) * .9
        rng = np.random.default_rng(seed)
        permutation = rng.permutation(n)
        sensory = permutation[:min(n // 3, inputs * 8)]
        motor = permutation[n // 2:n // 2 + actions * 8].reshape(actions, 8)
        drive = np.zeros((inputs, n), np.float32)
        for k, node in enumerate(sensory):
            drive[k % inputs, node] = 3.
        decode = np.zeros((n, actions), np.float32)
        for a, nodes in enumerate(motor):
            decode[nodes, a] = 4. / len(nodes)
        self.n, self.steps, self.actions, self.inputs = n, steps, actions, inputs
        self.register_buffer("edge_flat", torch.from_numpy((row * n + col).astype(np.int64)))
        self.register_buffer("base", torch.from_numpy(base))
        self.register_buffer("drive", torch.from_numpy(drive))
        self.register_buffer("decode", torch.from_numpy(decode))
        self.log_gain = nn.Parameter(torch.zeros(len(base)))

    def weights(self) -> torch.Tensor:
        values = self.base * torch.exp(self.log_gain.clamp(-3., 3.))
        return torch.zeros(self.n * self.n, device=values.device, dtype=values.dtype).scatter(0, self.edge_flat, values).reshape(self.n, self.n)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if x.ndim == 1:
            x = x[None, :]
        if x.ndim != 2 or x.shape[1] != self.inputs:
            raise ValueError("Fly input dimension mismatch")
        w = self.weights()
        current = x @ self.drive
        h = torch.zeros((len(x), self.n), device=x.device, dtype=x.dtype)
        for _ in range(self.steps):
            h = .5 * h + .5 * torch.tanh(h @ w.T + current)
        return h @ self.decode

    def project(self) -> None:
        with torch.no_grad():
            self.log_gain.clamp_(-3., 3.)


class MLP(nn.Module):
    def __init__(self, inputs: int = 6, actions: int = 2, width: int = 32):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(inputs, width), nn.Tanh(), nn.Linear(width, width), nn.Tanh(), nn.Linear(width, actions))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if x.ndim == 1:
            x = x[None, :]
        return self.net(x)

    def project(self) -> None:
        return None


class FeatureTransformer(nn.Module):
    def __init__(self, inputs: int = 6, actions: int = 2, d: int = 24, heads: int = 4):
        super().__init__()
        self.feature = nn.Parameter(torch.randn(inputs, d) * .05)
        self.val = nn.Linear(1, d, bias=False)
        self.cls = nn.Parameter(torch.randn(1, 1, d) * .05)
        layer = nn.TransformerEncoderLayer(d_model=d, nhead=heads, dim_feedforward=48,
                                          dropout=0., activation="gelu", batch_first=True, norm_first=True)
        # Disable an unused nested-tensor optimization explicitly; dense numerics unchanged.
        self.enc = nn.TransformerEncoder(layer, num_layers=1, enable_nested_tensor=False)
        self.out = nn.Linear(d, actions)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if x.ndim == 1:
            x = x[None, :]
        tok = self.feature[None, :, :] + self.val(x[:, :, None])
        return self.out(self.enc(torch.cat([self.cls.expand(x.shape[0], -1, -1), tok], 1))[:, 0])

    def project(self) -> None:
        return None


@dataclass(frozen=True)
class ModelSpec:
    kind: str
    inputs: int
    actions: int
    seed: int
    fly_seed: int = 7102

    def __post_init__(self) -> None:
        if self.kind not in {"fly", "mlp", "transformer"}:
            raise ValueError("Unknown model architecture")
        if not 1 <= self.inputs <= 256 or not 2 <= self.actions <= 16:
            raise ValueError("Unsupported model shape")
        if self.fly_seed not in {7101, 7102, 7103}:
            raise ValueError("Fly seed must identify one of the three supplied assignments")
        if self.seed < 0:
            raise ValueError("Seed must be nonnegative")


def make_model(spec: ModelSpec) -> nn.Module:
    with torch.random.fork_rng(devices=[]):
        torch.manual_seed(spec.seed)
        if spec.kind == "mlp":
            return MLP(spec.inputs, spec.actions)
        if spec.kind == "transformer":
            return FeatureTransformer(spec.inputs, spec.actions)
        graph_id = {7101: 211, 7102: 223, 7103: 239}[spec.fly_seed]
        return InternalFly(asset(f"graphs/graph_{graph_id}.npz"), spec.fly_seed, spec.inputs, spec.actions)


def predict(model: nn.Module, observations: np.ndarray) -> np.ndarray:
    model.eval()
    with torch.no_grad():
        return model(torch.as_tensor(np.array(observations, dtype=np.float32, copy=True))).cpu().numpy()


def state_fingerprint(model: nn.Module, *, buffers_only: bool = False) -> str:
    h = hashlib.sha256()
    values = dict(model.named_buffers()) if buffers_only else model.state_dict()
    for key, value in values.items():
        h.update(key.encode("utf-8"))
        h.update(value.detach().cpu().numpy().tobytes())
    return h.hexdigest()


def save_student(model: nn.Module, spec: ModelSpec, path: str | Path) -> None:
    """Only model specification and native state; no packet / grounding object."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"format": "iap-student-v1", "model_spec": asdict(spec),
                "state_dict": {k: v.detach().cpu() for k, v in model.state_dict().items()}}, p)


def load_student(path: str | Path) -> tuple[nn.Module, ModelSpec]:
    """Restricted Torch loading. Only load trusted local research checkpoints."""
    p = Path(path)
    if p.stat().st_size > 32_000_000:
        raise ValueError("Student checkpoint exceeds this benchmark's size limit")
    obj = torch.load(p, map_location="cpu", weights_only=True)
    if not isinstance(obj, dict) or set(obj) != {"format", "model_spec", "state_dict"} or obj["format"] != "iap-student-v1":
        raise ValueError("Unknown checkpoint format")
    spec = ModelSpec(**obj["model_spec"])
    model = make_model(spec)
    model.load_state_dict(obj["state_dict"], strict=True)
    if any(not torch.isfinite(v).all() for v in model.state_dict().values()):
        raise ValueError("Non-finite checkpoint state")
    return model, spec


def load_teacher(kind: str) -> nn.Module:
    spec = ModelSpec(kind, 6, 2, seed=0, fly_seed=7101)
    model = make_model(spec)
    state = torch.load(asset(f"teachers/{kind}_teacher_state.pt"), map_location="cpu", weights_only=True)
    model.load_state_dict(state, strict=True)
    return model
