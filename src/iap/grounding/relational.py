"""Gate 2E: matching of ordered chains without inverting sensor coordinates."""
from __future__ import annotations
import numpy as np
from ..contracts import CalibrationAPI, EvidenceError, GroundingResult, PublicWorld, QueryRecord, Progress, quiet
from ..packets import CultureCapsule
from .common import feasible, validate


def ground_relational(capsule: CultureCapsule, world: PublicWorld, oracle: CalibrationAPI,
                      budget: int = 18, *, active: bool = True, seed: int = 0,
                      progress: Progress = quiet) -> GroundingResult:
    validate(capsule, world, budget, ontology=False)
    source_q = capsule.policy(capsule.source_states()).astype(np.float32)
    source_pred = source_q.argmax(1).reshape(8, 3)
    comps = [np.ones((8, 8), bool), np.ones((8, 8), bool)]
    records: list[QueryRecord] = []
    rng = np.random.default_rng(seed)
    order = rng.permutation(world.state_count)
    lookup = {gid: (i, j) for i, chain in enumerate(world.chains) for j, gid in enumerate(chain)}

    def viable_edges():
        edges = []
        for swap in (0, 1):
            if feasible(comps[swap]):
                for i in range(8):
                    for j in range(8):
                        if comps[swap][i, j] and feasible(comps[swap], (i, j)):
                            edges.append((swap, i, j))
        if not edges:
            raise EvidenceError("No relational interpretation survives calibration")
        return edges

    for step in range(budget):
        edges = viable_edges()
        totals, counts = np.zeros((8, 3)), np.zeros((8, 3))
        for swap, i, j in edges:
            totals[i] += source_pred[j] ^ swap
            counts[i] += 1
        frac = np.divide(totals, counts, out=np.full_like(totals, .5), where=counts > 0)
        disagreement = .5 - np.abs(frac - .5)
        for record in records:
            i, s = lookup[record.state]
            disagreement[i, s] = -1
        if active:
            i, s = divmod(int(np.argmax(disagreement)), 3)
            state = world.chains[i][s]
        else:
            state = int(order[step])
            i, s = lookup[state]
        observed = int(oracle.query(state))
        if observed not in (0, 1):
            raise EvidenceError("Binary relational calibration returned an invalid action")
        records.append(QueryRecord(state, observed, "binary_reward"))
        for swap in (0, 1):
            for j in range(8):
                if comps[swap][i, j] and ((int(source_pred[j, s]) ^ swap) != observed):
                    comps[swap][i, j] = False
        progress({"event": "grounding_query", "family": "relational", "queries": len(records), "state": state})
    edges = viable_edges()
    qout = np.zeros((world.state_count, 2), np.float32)
    counts = np.zeros(world.state_count, np.float32)
    for swap, i, j in edges:
        for stage, gid in enumerate(world.chains[i]):
            q = source_q[j * 3 + stage]
            qout[gid] += q[::-1] if swap else q
            counts[gid] += 1
    qout /= np.maximum(counts[:, None], 1)
    return GroundingResult(qout, np.ones(world.state_count, bool), tuple(records),
                           {"viable_action_swaps": len({x[0] for x in edges}), "viable_matching_edges": len(edges),
                            "family": "eight-three-node-chains", "active": active})
