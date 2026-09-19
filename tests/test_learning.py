from dataclasses import asdict
import numpy as np
import torch
import pytest
from iap.models import ModelSpec, make_model, predict, load_teacher, save_student, load_student
from iap.absorption import absorb
from iap.resources import teacher_capsule
from iap.tasks import source_support
from iap.distillation import distill


@pytest.mark.parametrize("kind", ["fly", "mlp", "transformer"])
def test_teacher_checkpoints(kind):
    x, y = source_support()
    model = load_teacher(kind)
    assert np.array_equal(predict(model, x).argmax(1), y)


@pytest.mark.parametrize("kind", ["fly", "mlp", "transformer"])
def test_absorption_and_standalone_checkpoint(kind, tmp_path):
    x, _ = source_support()
    cap = teacher_capsule("transformer")
    spec = ModelSpec(kind, 6, 2, 101, 7102)
    model = make_model(spec)
    report = absorb(model, x, cap.policy(x), updates=8, seed=201)
    assert report.environmental_rewards == 0
    assert report.updates == report.exposure_draws == 8
    assert report.batch_examples == 36
    assert report.unique_states_exposed <= 8
    assert report.initial_state_sha256 != report.final_state_sha256
    if kind == "fly":
        assert report.changed_state_keys == ["log_gain"]
        assert report.fixed_buffers_unchanged
    path = tmp_path / "student.pt"
    save_student(model, spec, path)
    payload = torch.load(path, weights_only=True)
    assert set(payload) == {"format", "model_spec", "state_dict"}
    assert not any("packet" in key or "teacher" in key for key in payload["state_dict"])
    restored, restored_spec = load_student(path)
    assert restored_spec == spec
    np.testing.assert_array_equal(predict(model, x), predict(restored, x))


def test_invalid_absorption():
    spec = ModelSpec("mlp", 6, 2, 1)
    model = make_model(spec)
    x, _ = source_support()
    with pytest.raises(ValueError):
        absorb(model, x, np.zeros((24, 2)), np.array([], int), updates=1)
    with pytest.raises(ValueError):
        absorb(model, x, np.full((24, 2), np.nan), updates=1)


def test_bounded_teacher_distillation():
    # This checks the route, not convergence in only five updates.
    cap, report = distill(load_teacher("mlp"), updates=5)
    assert cap.payload_bytes == 241
    assert report["distillation_updates"] == 5
