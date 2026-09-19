import itertools
import importlib.util
from pathlib import Path
import sys
import zipfile
import numpy as np
import pytest
from iap.grounding.common import feasible
from iap.grounding import ground_ontology, ground_relational, ground_permutation
from iap.resources import teacher_capsule
from iap.tasks import make_world
from iap.contracts import EvidenceError


def test_matching_against_brute_force():
    rng = np.random.default_rng(123)
    for _ in range(30):
        matrix = rng.random((4, 4)) > .4
        expected = any(all(matrix[i, p[i]] for i in range(4)) for p in itertools.permutations(range(4)))
        assert feasible(matrix) == expected
        for i in range(4):
            for j in range(4):
                expected = any(p[i] == j and all(matrix[k, p[k]] for k in range(4)) for p in itertools.permutations(range(4)))
                assert feasible(matrix, (i, j)) == expected


@pytest.mark.parametrize("family,budget", [("relational", 18), ("ontology", 36), ("permutation", 16)])
@pytest.mark.integration
def test_grounding_without_hidden_mapping(family, budget):
    w = make_world(family, 1200000)
    c = teacher_capsule("transformer", relational=family != "permutation")
    fn = {"relational": ground_relational, "ontology": ground_ontology, "permutation": ground_permutation}[family]
    result = fn(c, w.public, w.oracle(budget), budget, seed=1200001)
    p = np.where(result.predicted_roles, result.targets.argmax(1), -1)
    assert w.score(p)["action_accuracy"] >= .95
    assert len(result.records) == budget
    assert len({r.state for r in result.records}) == budget


def test_bad_grammar_and_budget():
    c = teacher_capsule("fly")
    w = make_world("relational", 1)
    with pytest.raises(ValueError):
        ground_ontology(c, w.public, w.oracle(36), 36)
    with pytest.raises(ValueError):
        ground_relational(c, w.public, w.oracle(25), 25)


@pytest.mark.integration
def test_finite_grounder_reference_equivalence(repository, tmp_path):
    archive = repository / "archive/IAP_Gate2F_Ontology_Translation.zip"
    with zipfile.ZipFile(archive) as z:
        z.extractall(tmp_path)
    src = tmp_path / "iap_gate2f_ontology_translation/source"
    sys.path.insert(0, str(src))
    try:
        spec = importlib.util.spec_from_file_location("iap_legacy_f_test", src / "gate2f_experiment.py")
        legacy = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(legacy)
    finally:
        sys.path.pop(0)
    for seed in (1200000, 1300000):
        w = make_world("ontology", seed)
        old = legacy.make_world(seed)
        np.testing.assert_array_equal(old["Y"], w.public.observations)
        np.testing.assert_array_equal(old["tgt"], w.labels)
        g = ground_ontology(teacher_capsule("fly"), w.public, w.oracle(36), 36)
        previous = legacy.ontology_ground(legacy.PACKETS["fly"][1], old, 36)
        assert previous["queries"] == [r.state for r in g.records]
        pred = np.where(g.predicted_roles, g.targets.argmax(1), -1)
        np.testing.assert_array_equal(previous["pred"], pred)
