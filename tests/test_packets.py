import json
import struct
import numpy as np
import pytest
from iap.packets import CultureCapsule, PolicyPacket, PacketError, ENVELOPE_MAGIC
from iap.resources import teacher_capsule, verify_assets
from iap.tasks import source_support


@pytest.mark.parametrize("name", ["fly", "mlp", "transformer"])
def test_teacher_packets_roundtrip(name):
    c = teacher_capsule(name)
    assert len(c.policy.raw) == 97 and c.payload_bytes == 241
    assert CultureCapsule.from_bytes(c.raw).raw == c.raw
    assert CultureCapsule.from_bytes(c.to_envelope()).raw == c.raw
    assert len(c.to_envelope()) > c.payload_bytes
    x, y = source_support()
    assert np.array_equal(x, c.source_states())
    assert np.array_equal(c.policy(x).argmax(1), y)


@pytest.mark.parametrize("data", [b"", b"x" * 97, b"IAPCV2\0" + b"\0" * 90, b"IAPENV1\0", b"x" * 20000])
def test_invalid_packets(data):
    with pytest.raises(PacketError):
        CultureCapsule.from_bytes(data)


def test_corrupt_framing_and_scale():
    c = teacher_capsule("fly")
    raw = bytearray(c.to_envelope())
    raw[-1] ^= 1
    with pytest.raises(PacketError):
        CultureCapsule.from_bytes(bytes(raw))
    raw = bytearray(c.policy.raw)
    raw[7:11] = struct.pack("<f", float("nan"))
    with pytest.raises(PacketError):
        PolicyPacket(bytes(raw))


def test_policy_only_no_atlas():
    c = teacher_capsule("fly", relational=False)
    assert c.payload_bytes == 97
    with pytest.raises(PacketError):
        c.source_states()


@pytest.mark.parametrize("x", [np.zeros((2, 5)), np.full((2, 6), np.nan), np.zeros((1, 1, 6))])
def test_bad_observation(x):
    with pytest.raises(PacketError):
        teacher_capsule("fly").policy(x)


def test_quantization():
    rng = np.random.default_rng(2)
    arrays = tuple(rng.normal(size=shape).astype(np.float32) for shape in ((8, 6), (8,), (2, 8), (2,)))
    p = PolicyPacket.quantize(arrays)
    for a, b in zip(arrays, p.arrays()):
        assert np.max(np.abs(a - b)) <= np.max(np.abs(a)) / 127 + 1e-6
    with pytest.raises(PacketError):
        PolicyPacket.quantize((np.zeros((2, 2)),) * 4)


def test_assets():
    assert verify_assets()["asset_count"] >= 12
    assert len({teacher_capsule(x).sha256 for x in ("fly", "mlp", "transformer")}) == 3
