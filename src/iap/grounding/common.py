from __future__ import annotations
import numpy as np
from ..contracts import PublicWorld
from ..packets import CultureCapsule


def feasible(compatibility: np.ndarray, fixed: tuple[int, int] | None = None) -> bool:
    """Whether a square compatibility graph admits a perfect matching."""
    c = np.asarray(compatibility, dtype=bool).copy()
    if c.ndim != 2 or c.shape[0] != c.shape[1]:
        raise ValueError("Compatibility matrix must be square")
    n = len(c)
    if fixed is not None:
        i, j = fixed
        if not (0 <= i < n and 0 <= j < n):
            raise ValueError("Fixed matching edge out of bounds")
        if not c[i, j]:
            return False
        c[i, :] = False
        c[i, j] = True
        for other in range(n):
            if other != i:
                c[other, j] = False
    matching = [-1] * n

    def augment(i: int, seen: list[bool]) -> bool:
        for j in range(n):
            if c[i, j] and not seen[j]:
                seen[j] = True
                if matching[j] < 0 or augment(matching[j], seen):
                    matching[j] = i
                    return True
        return False

    return all(augment(i, [False] * n) for i in range(n))


def validate(capsule: CultureCapsule, world: PublicWorld, budget: int, *, ontology: bool) -> None:
    if not isinstance(budget, int) or budget < 0 or budget > world.state_count:
        raise ValueError("Query budget must be between zero and the number of distinct states")
    if len(world.chains) != 8 or world.actions != (4 if ontology else 2):
        raise ValueError("Unsupported chain count or action count for this bounded grammar")
    if ontology and any(not 6 <= len(ch) <= 11 for ch in world.chains):
        raise ValueError("Ontology grammar requires chain lengths between 6 and 11")
    if not ontology and any(len(ch) != 3 for ch in world.chains):
        raise ValueError("Relational grammar requires eight three-state chains")
    capsule.source_states()
