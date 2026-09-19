from dataclasses import fields
import numpy as np
import pytest
from iap.contracts import PublicWorld, QueryOracle, EvidenceError
from iap.tasks import source_support, make_world


def test_truth_boundary():
    assert {x.name for x in fields(PublicWorld)} == {"observations", "chains", "actions"}
    w = make_world("ontology", 1200000)
    assert not hasattr(w.public, "labels")
    assert not hasattr(w.public, "ctx_perm")
    assert len(w.public.chains) == 8
    assert np.sum(w.labels >= 0) == 48
    with pytest.raises(ValueError):
        w.public.observations[0, 0] = 4


@pytest.mark.parametrize("family", ["aligned", "permutation", "relational", "ontology"])
def test_world_determinism(family):
    a, b = make_world(family, 101), make_world(family, 101)
    assert np.array_equal(a.public.observations, b.public.observations)
    assert np.array_equal(a.labels, b.labels)
    assert a.score(a.labels)["sequence_accuracy"] == 1


def test_query_accounting():
    o = QueryOracle(np.array([-1, 3, 0]), 4, 2, "action_or_nuisance")
    assert o.query(0) == -1
    with pytest.raises(EvidenceError):
        o.query(0)
    assert o.query(1) == 3
    assert o.accounting()["queries_used"] == 2
    assert o.accounting()["primitive_trial_equivalent_upper_bound"] == 8
    assert o.accounting()["primitive_trials_actually_executed"] == 0
    with pytest.raises(EvidenceError):
        o.query(2)


@pytest.mark.parametrize("kind,labels,actions", [("binary_reward", [-1, 0], 2), ("binary_reward", [0, 2], 4), ("other", [0], 2)])
def test_invalid_oracle(kind, labels, actions):
    with pytest.raises(ValueError):
        QueryOracle(np.array(labels), actions, 1, kind)


def test_invalid_world_chain():
    with pytest.raises(ValueError):
        PublicWorld(np.zeros((3, 2)), ((0, 1), (1, 2)), 2)
    with pytest.raises(ValueError):
        PublicWorld(np.full((3, 2), np.nan), ((0, 1, 2),), 2)
