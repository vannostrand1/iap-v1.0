from dataclasses import replace
import json
import subprocess
import sys
import pytest
from iap.reporting import paired_bootstrap, summarize_rows, read_json
from iap.experiments import ExperimentConfig, run
from iap.audit import audit_evidence


def test_bootstrap_known_effect():
    stats = paired_bootstrap([1, 1, 1], [0, 0, 0])
    assert stats["mean_delta"] == stats["ci95_low"] == stats["ci95_high"] == 1
    assert paired_bootstrap([1], [0])["ci95_low"] is None
    with pytest.raises(ValueError):
        paired_bootstrap([1], [0, 1])


def test_missing_and_duplicate_pairs_rejected():
    a = dict(direction="f2t", rep=0, condition="grounded_culture", action_accuracy=1, sequence_accuracy=1)
    b = dict(a, condition="query_only_no_packet", rep=1)
    with pytest.raises(ValueError):
        summarize_rows([a, a])
    with pytest.raises(ValueError):
        summarize_rows([a, b])


def test_evidence_arithmetic(repository):
    audit = audit_evidence(repository)
    assert audit["status"] == "passed"
    assert len(audit["numeric_checks"]) == 32


@pytest.mark.parametrize("overrides", [{"replicates": 0}, {"pairing": "unknown"}, {"family": "unknown"}, {"queries": -1}, {"updates": {"f2t": 1}}])
def test_config_rejects_bad_values(overrides):
    with pytest.raises(ValueError):
        ExperimentConfig(**overrides)


@pytest.mark.integration
def test_runner_resume_and_matching(tmp_path):
    cfg = ExperimentConfig(name="test", directions=("f2t",), updates={"f2t": 2})
    root = tmp_path / "run"
    results = run(cfg, root)
    assert len(results["rows"]) == 3
    assert len({r["initial_state_sha256"] for r in results["rows"]}) == 1
    assert read_json(root / "run_manifest.json")["status"] == "completed"
    for row in results["rows"]:
        assert row["environmental_rewards_during_absorption"] == 0
    again = run(cfg, root, resume=True)
    assert results["rows"] == again["rows"]
    with pytest.raises(FileExistsError):
        run(cfg, root)
    with pytest.raises(ValueError):
        run(replace(cfg, queries=35), root, resume=True)
    completion = root / "f2t_rep0000/grounding.json"
    completion.write_text("{}")
    with pytest.raises(ValueError):
        run(cfg, root, resume=True)


def test_cli_version():
    p = subprocess.run([sys.executable, "-m", "iap", "--version"], text=True, capture_output=True)
    assert p.returncode == 0
    assert p.stdout.strip() == "1.0.0"
