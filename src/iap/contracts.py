"""Explicit learner/grounder/evaluator information boundaries.

PublicWorld contains no target labels or hidden correspondence. QueryOracle is
an *oracle-style calibration API*, not an unassisted live environment. Its
answers, unique states, and upper-bound primitive-trial equivalents are logged.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Protocol
import numpy as np


class EvidenceError(RuntimeError):
    """No interpretation in the declared family explains observed evidence."""


@dataclass(frozen=True)
class PublicWorld:
    observations: np.ndarray
    chains: tuple[tuple[int, ...], ...]
    actions: int

    def __post_init__(self) -> None:
        x = np.array(self.observations, dtype=np.float32, copy=True)
        if x.ndim != 2 or x.shape[0] == 0 or not np.isfinite(x).all():
            raise ValueError("World observations must be a nonempty finite matrix")
        if self.actions < 2:
            raise ValueError("At least two primitive actions required")
        chains = tuple(tuple(int(i) for i in ch) for ch in self.chains)
        ids = [i for ch in chains for i in ch]
        if any(len(ch) == 0 for ch in chains) or sorted(ids) != list(range(len(x))):
            raise ValueError("Chains must partition the observed state support exactly once")
        x.flags.writeable = False
        object.__setattr__(self, "observations", x)
        object.__setattr__(self, "chains", chains)

    @property
    def state_count(self) -> int:
        return len(self.observations)


@dataclass(frozen=True)
class QueryRecord:
    state: int
    label: int
    kind: str


class CalibrationAPI(Protocol):
    def query(self, state: int) -> int: ...


class QueryOracle:
    """Privileged simulator adapter. Do not pass the simulator to the grounder.

    binary_reward: execute primitive 0; deterministic +/- reward identifies the
    binary preferred action. action_or_nuisance: reveal a 5-category label.
    The latter's four-trial equivalent is an assumption, not executed gameplay.
    """
    def __init__(self, labels: np.ndarray, actions: int, budget: int, kind: str):
        if not isinstance(budget, int) or budget < 0:
            raise ValueError("Budget must be a nonnegative integer")
        if kind not in {"binary_reward", "action_or_nuisance"}:
            raise ValueError("Unknown calibration kind")
        labels = np.array(labels, dtype=np.int64, copy=True)
        if labels.ndim != 1 or len(labels) == 0 or np.any((labels < -1) | (labels >= actions)):
            raise ValueError("Invalid oracle labels")
        if kind == "binary_reward" and (actions != 2 or np.any(labels < 0)):
            raise ValueError("Binary-reward mode requires two actions and no nuisance labels")
        self.__labels = labels
        self.actions = actions
        self.budget = budget
        self.kind = kind
        self.records: list[QueryRecord] = []

    def query(self, state: int) -> int:
        if len(self.records) >= self.budget:
            raise EvidenceError("Calibration budget exhausted")
        if not isinstance(state, (int, np.integer)) or not 0 <= state < len(self.__labels):
            raise ValueError("Query state is out of bounds")
        if any(r.state == state for r in self.records):
            raise EvidenceError("Duplicate query would double-count a revealed label")
        label = int(self.__labels[state])
        self.records.append(QueryRecord(int(state), label, self.kind))
        return label

    def accounting(self) -> dict:
        n = len(self.records)
        return {
            "query_kind": self.kind,
            "queries_used": n,
            "unique_queried_states": len({r.state for r in self.records}),
            "action_labels_revealed": sum(r.label >= 0 for r in self.records),
            "nuisance_labels_revealed": sum(r.label < 0 for r in self.records),
            "primitive_trial_equivalent_upper_bound": n * (1 if self.kind == "binary_reward" else self.actions),
            "primitive_trials_actually_executed": 0,
        }


@dataclass
class GroundingResult:
    targets: np.ndarray
    predicted_roles: np.ndarray
    records: tuple[QueryRecord, ...]
    diagnostics: dict = field(default_factory=dict)


Progress = Callable[[dict], None]


def quiet(event: dict) -> None:
    return None
