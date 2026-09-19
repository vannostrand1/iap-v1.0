"""Finite Convention Relay simulators; hidden truth stays on this side.

The benchmark exhaustively evaluates the same finite support used for exposure.
A 'sequence' metric is the conjunction of independent stage decisions. It does
not demonstrate long-horizon planning, action-dependent dynamics, or memory.
"""
from __future__ import annotations
from dataclasses import dataclass
import itertools
import math
import numpy as np
from .contracts import PublicWorld, QueryOracle

CODEBOOKS = tuple((tuple(p[:2]), tuple(p[2:])) for p in itertools.permutations(range(4)))


def convention(context: int, stage: int) -> int:
    if context not in range(8) or stage not in range(3):
        raise ValueError("Context/stage outside Convention Relay support")
    b = [(context >> 2) & 1, (context >> 1) & 1, context & 1]
    if stage == 0:
        return b[0] ^ b[1] ^ b[2]
    if stage == 1:
        return b[0] ^ b[2]
    return int(sum(b) >= 2)


def source_support() -> tuple[np.ndarray, np.ndarray]:
    states, labels = [], []
    for ctx in range(8):
        bits = np.array([(ctx >> 2) & 1, (ctx >> 1) & 1, ctx & 1], np.float32) * 2 - 1
        for stage in range(3):
            onehot = np.zeros(3, np.float32)
            onehot[stage] = 1
            states.append(np.r_[bits, onehot])
            labels.append(convention(ctx, stage))
    return np.stack(states).astype(np.float32), np.array(labels, np.int64)


@dataclass(frozen=True)
class BenchmarkWorld:
    public: PublicWorld
    labels: np.ndarray
    hidden_metadata: dict

    def oracle(self, budget: int) -> QueryOracle:
        kind = "action_or_nuisance" if self.public.actions == 4 else "binary_reward"
        return QueryOracle(self.labels, self.public.actions, budget, kind)

    def score(self, predictions: np.ndarray) -> dict:
        p = np.asarray(predictions)
        if p.shape != self.labels.shape:
            raise ValueError("Prediction length does not match benchmark")
        decision = self.labels >= 0
        sequence = []
        for ch in self.public.chains:
            ids = [i for i in ch if decision[i]]
            sequence.append(bool(np.all(p[ids] == self.labels[ids])))
        return {"action_accuracy": float(np.mean(p[decision] == self.labels[decision])),
                "sequence_accuracy": float(np.mean(sequence)),
                "role_accuracy": float(np.mean((p >= 0) == decision))}


def aligned_world() -> BenchmarkWorld:
    x, labels = source_support()
    return BenchmarkWorld(PublicWorld(x, tuple(tuple(range(i * 3, i * 3 + 3)) for i in range(8)), 2), labels, {})


def permutation_world(seed: int) -> BenchmarkWorld:
    x, labels = source_support()
    r = np.random.default_rng(seed)
    perm = r.permutation(6)
    signs = r.choice(np.array([-1., 1.], dtype=np.float32), size=6)
    swap = int(r.integers(2))
    return BenchmarkWorld(PublicWorld(x[:, perm] * signs[None, :], aligned_world().public.chains, 2),
                          labels ^ swap, {"perm": perm.tolist(), "signs": signs.tolist(), "swap": swap})


def relational_world(seed: int, outdim: int = 8) -> BenchmarkWorld:
    if outdim < 1:
        raise ValueError("outdim must be positive")
    states, labels = source_support()
    r = np.random.default_rng(seed)
    ctx_perm = r.permutation(8)
    swap = int(r.integers(2))
    idx = np.array([ctx_perm[i] * 3 + s for i in range(8) for s in range(3)], dtype=int)
    x = states[idx]
    a = r.normal(size=(outdim, 6)).astype(np.float32) / np.sqrt(6)
    b = r.normal(size=(outdim, 6)).astype(np.float32) / np.sqrt(6)
    bias = r.uniform(-.4, .4, outdim).astype(np.float32)
    z, w = x @ a.T + bias, x @ b.T
    y = (np.tanh(1.15 * z) + .12 * w ** 3 / (1 + w ** 2)).astype(np.float32)
    y = (y - y.mean(0, keepdims=True)) / (y.std(0, keepdims=True) + 1e-4)
    return BenchmarkWorld(PublicWorld(y, aligned_world().public.chains, 2), labels[idx] ^ swap,
                          {"context_permutation": ctx_perm.tolist(), "action_swap": swap})


def ontology_world(seed: int, outdim: int = 8) -> BenchmarkWorld:
    if outdim < 1:
        raise ValueError("outdim must be positive")
    states, actions = source_support()
    r = np.random.default_rng(seed)
    ctx_perm = r.permutation(8)
    cb_idx = int(r.integers(len(CODEBOOKS)))
    cb = CODEBOOKS[cb_idx]
    chains, outcomes, raw = [], [], []
    a = r.normal(size=(outdim, 14)).astype(np.float32) / np.sqrt(14)
    b = r.normal(size=(outdim, 14)).astype(np.float32) / np.sqrt(14)
    bias = r.uniform(-.4, .4, outdim).astype(np.float32)
    for source_ctx in ctx_perm:
        seq, desc = [], []
        pre, suf = int(r.integers(2)), int(r.integers(2))
        seq += [-1] * pre
        desc += [(None, "nuisance")] * pre
        for stage in range(3):
            macro = cb[int(actions[source_ctx * 3 + stage])]
            length = int(r.integers(2, 4))
            if length == 2:
                vals = [macro[0], macro[1]]
                roles = [(stage, "macro0"), (stage, "macro1")]
            else:
                nuisance = int(r.integers(3))
                vals, roles, k = [], [], 0
                for pos in range(3):
                    if pos == nuisance:
                        vals.append(-1)
                        roles.append((None, "nuisance"))
                    else:
                        vals.append(macro[k])
                        roles.append((stage, f"macro{k}"))
                        k += 1
            seq += vals
            desc += roles
        seq += [-1] * suf
        desc += [(None, "nuisance")] * suf
        ids, length = [], len(seq)
        for pos, (outcome, (stage, role)) in enumerate(zip(seq, desc)):
            if stage is None:
                src = np.zeros(6, np.float32)
                rolevec = np.array([0, 0, 0, 1], np.float32)
            else:
                src = states[source_ctx * 3 + stage]
                rolevec = np.array([float(role == "macro0"), float(role == "macro1"), stage / 2, 0], np.float32)
            position = np.array([2 * pos / max(1, length - 1) - 1, math.sin((pos + 1) * .7)], np.float32)
            noise = np.array([1 if outcome < 0 else -1, r.normal(0, .25)], np.float32)
            z = np.r_[src, rolevec, position, noise].astype(np.float32)
            raw.append(np.tanh(1.1 * (z @ a.T + bias)) + .13 * (z @ b.T) ** 3 / (1 + (z @ b.T) ** 2))
            outcomes.append(outcome)
            ids.append(len(outcomes) - 1)
        chains.append(tuple(ids))
    y = np.stack(raw).astype(np.float32)
    y = (y - y.mean(0, keepdims=True)) / (y.std(0, keepdims=True) + 1e-4)
    return BenchmarkWorld(PublicWorld(y, tuple(chains), 4), np.asarray(outcomes, int),
                          {"context_permutation": ctx_perm.tolist(), "codebook": cb_idx})


def make_world(family: str, seed: int, outdim: int = 8) -> BenchmarkWorld:
    if family == "aligned":
        return aligned_world()
    if family == "permutation":
        return permutation_world(seed)
    if family == "relational":
        return relational_world(seed, outdim)
    if family == "ontology":
        return ontology_world(seed, outdim)
    raise ValueError(f"Unknown world family: {family}")
