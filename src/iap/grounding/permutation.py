"""Gate 2D exhaustive signed-coordinate grounder (92,160 hypotheses)."""
from __future__ import annotations
import itertools
import numpy as np
from ..contracts import CalibrationAPI, EvidenceError, GroundingResult, PublicWorld, QueryRecord, Progress, quiet
from ..packets import CultureCapsule


def ground_permutation(capsule: CultureCapsule, world: PublicWorld, oracle: CalibrationAPI,
                       budget: int = 16, *, seed: int = 0, active: bool = True,
                       progress: Progress = quiet) -> GroundingResult:
    if world.observations.shape != (24, 6) or world.actions != 2:
        raise ValueError("Signed-permutation grounding requires 24 six-channel states and two actions")
    if not isinstance(budget, int) or not 0 <= budget <= 24:
        raise ValueError("Invalid calibration budget")
    perms = np.array(list(itertools.permutations(range(6))), np.int64)
    signs = np.array(list(itertools.product([-1., 1.], repeat=6)), np.float32)
    invperm, invsign = np.repeat(perms, len(signs), 0), np.tile(signs, (len(perms), 1))
    n = len(invperm)
    qtable = np.empty((n, 24, 2), np.float32)
    for start in range(0, n, 2048):
        stop = min(start + 2048, n)
        vals = np.take(world.observations, invperm[start:stop], axis=1)
        vals = np.transpose(vals, (1, 0, 2)) * invsign[start:stop, None, :]
        qtable[start:stop] = capsule.policy(vals.reshape(-1, 6)).reshape(stop - start, 24, 2)
    predicted = qtable.argmax(2).astype(np.int8)
    survivors = np.ones((n, 2), bool)
    rng = np.random.default_rng(seed)
    passive_order = np.random.default_rng(seed).permutation(24)
    records: list[QueryRecord] = []
    for step in range(budget):
        oi, swap = np.nonzero(survivors)
        if not len(oi):
            raise EvidenceError("No signed-permutation interpretation survives")
        if len(oi) > 20_000:
            choose = rng.choice(len(oi), 20_000, replace=False)
            oi, swap = oi[choose], swap[choose]
        frac = (predicted[oi] ^ swap[:, None]).mean(0)
        score = .5 - np.abs(frac - .5)
        for rec in records:
            score[rec.state] = -1
        state = int(np.argmax(score)) if active else int(passive_order[step])
        observed = int(oracle.query(state))
        if observed not in (0, 1):
            raise EvidenceError("Invalid binary calibration response")
        records.append(QueryRecord(state, observed, "binary_reward"))
        survivors &= (predicted[:, state, None] ^ np.array([0, 1], np.int8)[None, :]) == observed
        progress({"event": "grounding_query", "family": "permutation", "queries": len(records), "state": state})
    oi, swap = np.nonzero(survivors)
    if not len(oi):
        raise EvidenceError("No surviving signed-permutation hypotheses")
    count = len(oi)
    if len(oi) > 4096:
        choose = rng.choice(len(oi), 4096, replace=False)
        oi, swap = oi[choose], swap[choose]
    q = qtable[oi].copy()
    flipped = swap == 1
    q[flipped] = q[flipped][:, :, ::-1]
    return GroundingResult(q.mean(0), np.ones(24, bool), tuple(records),
                           {"hypotheses_evaluated": n * 2, "survivors": count,
                            "ensemble_size": len(oi), "active": active})
