"""Gate 2F: bounded chain expansions + unknown two-primitive action macros.

The generic grammar remains authored, not autonomously discovered. Vote weights
are feasible-edge / pattern marginals, not a normalized posterior over all full
ontology assignments. Only the CalibrationAPI can supply labels.
"""
from __future__ import annotations
from functools import lru_cache
import itertools
import numpy as np
from ..contracts import CalibrationAPI, EvidenceError, GroundingResult, PublicWorld, QueryRecord, Progress, quiet
from ..packets import CultureCapsule
from .common import feasible, validate

# This is the declared generic macro family, not the hidden world's codebook.
CODEBOOKS = tuple((tuple(p[:2]), tuple(p[2:])) for p in itertools.permutations(range(4)))


@lru_cache(maxsize=4096)
def candidate_patterns(codebook: int, length: int, source_actions: tuple[int, ...]) -> np.ndarray:
    if codebook not in range(24) or len(source_actions) != 3 or any(a not in (0, 1) for a in source_actions):
        raise ValueError("Invalid macro codebook or source chain")
    cb, output = CODEBOOKS[codebook], []
    for pre in (0, 1):
        for post in (0, 1):
            for lens in itertools.product((2, 3), repeat=3):
                if pre + post + sum(lens) != length:
                    continue
                variants = []
                for stage, n in enumerate(lens):
                    a, b = cb[source_actions[stage]]
                    variants.append([[a, b]] if n == 2 else [[-1, a, b], [a, -1, b], [a, b, -1]])
                for sequence in itertools.product(*variants):
                    output.append([-1] * pre + list(sequence[0]) + list(sequence[1]) + list(sequence[2]) + [-1] * post)
    result = np.unique(np.asarray(output, dtype=np.int8), axis=0) if output else np.empty((0, length), np.int8)
    result.flags.writeable = False
    return result


def ground_ontology(capsule: CultureCapsule, world: PublicWorld, oracle: CalibrationAPI,
                    budget: int = 36, *, active: bool = True, seed: int = 0,
                    progress: Progress = quiet) -> GroundingResult:
    validate(capsule, world, budget, ontology=True)
    source_pred = capsule.policy(capsule.source_states()).argmax(1).reshape(8, 3)
    pats, masks = {}, {}
    for cb in range(24):
        for i, chain in enumerate(world.chains):
            for j in range(8):
                p = candidate_patterns(cb, len(chain), tuple(int(x) for x in source_pred[j]))
                pats[cb, i, j] = p
                masks[cb, i, j] = np.ones(len(p), bool)
    records: list[QueryRecord] = []
    queried: set[int] = set()
    passive_order = np.random.default_rng(seed).permutation(world.state_count)
    lookup = {gid: (i, k) for i, chain in enumerate(world.chains) for k, gid in enumerate(chain)}

    def votes():
        viable = []
        for cb in range(24):
            comp = np.array([[masks[cb, i, j].any() for j in range(8)] for i in range(8)], bool)
            if feasible(comp):
                viable.append((cb, comp))
        if not viable:
            raise EvidenceError("Ontology hypothesis set became empty; cannot silently fall back")
        counts = [np.zeros((len(ch), 5), np.float64) for ch in world.chains]
        for cb, comp in viable:
            for i, ch in enumerate(world.chains):
                for j in range(8):
                    if not comp[i, j] or not feasible(comp, (i, j)):
                        continue
                    pp = pats[cb, i, j][masks[cb, i, j]]
                    if not len(pp):
                        continue
                    local = np.zeros((len(ch), 5))
                    for label in range(-1, 4):
                        local[:, label + 1] = (pp == label).mean(0)
                    counts[i] += local
        return counts, viable

    for step in range(budget):
        counts, _ = votes()
        best, bestscore = None, -1.
        if active:
            for i, chain in enumerate(world.chains):
                for pos, gid in enumerate(chain):
                    if gid in queried:
                        continue
                    c = counts[i][pos]
                    if c.sum() == 0:
                        continue
                    p = c / c.sum()
                    entropy = -np.sum(p[p > 0] * np.log(p[p > 0] + 1e-12))
                    score = entropy * (1 + .1 * (1 - p[0]))
                    if score > bestscore:
                        bestscore, best = score, (i, pos, gid)
        else:
            gid = int(passive_order[step])
            i, pos = lookup[gid]
            best = i, pos, gid
        if best is None:
            break
        i, pos, gid = best
        observed = int(oracle.query(gid))
        if observed not in range(-1, 4):
            raise EvidenceError("Ontology calibration label outside nuisance/0..3")
        records.append(QueryRecord(gid, observed, "action_or_nuisance"))
        queried.add(gid)
        for cb in range(24):
            for j in range(8):
                masks[cb, i, j] &= pats[cb, i, j][:, pos] == observed
        progress({"event": "grounding_query", "family": "ontology", "queries": len(records), "state": gid})
    counts, viable = votes()
    probabilities = np.zeros((world.state_count, 5))
    for i, chain in enumerate(world.chains):
        probabilities[list(chain)] = counts[i] / np.maximum(counts[i].sum(1, keepdims=True), 1e-12)
    prediction = probabilities.argmax(1) - 1
    targets = np.zeros((world.state_count, 4), np.float32)
    actionable = prediction >= 0
    targets[actionable] = -1
    targets[np.flatnonzero(actionable), prediction[actionable]] = 1
    return GroundingResult(targets, actionable, tuple(records),
                           {"viable_codebooks": len(viable), "family": "bounded-two-step-macros",
                            "active": active, "pattern_cache_entries": candidate_patterns.cache_info().currsize})
