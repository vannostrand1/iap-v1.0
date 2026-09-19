"""Strict readers for the historical 97/241-byte formats and a framed envelope.

The packet contains *surrogate neural weights*, not native teacher weights.
The 144-byte atlas is a complete source-side state support ordered by chains.
Neither its bytes nor its structural information are free side information.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import struct
import numpy as np

MAGIC = b"IAPCV2\0"
ENVELOPE_MAGIC = b"IAPENV1\0"
POLICY_BYTES = 97
ATLAS_BYTES = 144
MAX_ENVELOPE_BYTES = 16_384
SHAPES = ((8, 6), (8,), (2, 8), (2,))


class PacketError(ValueError):
    """Malformed, unsupported, or integrity-invalid cultural packet."""


@dataclass(frozen=True)
class PolicyPacket:
    """Quantized 6 -> 8 -> 2 tanh policy surrogate, byte-identical on round trip."""

    raw: bytes

    def __post_init__(self) -> None:
        if not isinstance(self.raw, bytes):
            raise PacketError("Packet input must be immutable bytes")
        if len(self.raw) != POLICY_BYTES or self.raw[:7] != MAGIC:
            raise PacketError("Expected an IAPCV2 97-byte policy packet")
        scales = struct.unpack("<4f", self.raw[7:23])
        if not all(np.isfinite(s) and 0 < s <= 1e6 for s in scales):
            raise PacketError("Quantization scales must be finite and positive (<= 1e6)")

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.raw).hexdigest()

    def arrays(self) -> tuple[np.ndarray, ...]:
        scales = struct.unpack("<4f", self.raw[7:23])
        result = []
        offset = 23
        for shape, scale in zip(SHAPES, scales):
            size = int(np.prod(shape))
            a = np.frombuffer(self.raw, np.int8, count=size, offset=offset)
            result.append(a.astype(np.float32).reshape(shape) * scale)
            offset += size
        return tuple(result)

    def predict(self, observations: np.ndarray) -> np.ndarray:
        x = np.asarray(observations, dtype=np.float32)
        if x.ndim not in (1, 2) or x.shape[-1] != 6 or not np.isfinite(x).all():
            raise PacketError("Policy observations must be finite (..., 6) vectors")
        w1, b1, w2, b2 = self.arrays()
        return np.tanh(x @ w1.T + b1) @ w2.T + b2

    __call__ = predict

    @classmethod
    def quantize(cls, arrays: tuple[np.ndarray, ...]) -> "PolicyPacket":
        if len(arrays) != 4:
            raise PacketError("Expected four tensors: w1, b1, w2, b2")
        scales, tensors = [], []
        for values, shape in zip(arrays, SHAPES):
            a = np.asarray(values, np.float32)
            if a.shape != shape or not np.isfinite(a).all():
                raise PacketError(f"Expected finite tensor of shape {shape}")
            scale = max(float(np.abs(a).max()) / 127.0, 1e-8)
            scales.append(scale)
            tensors.append(np.clip(np.round(a / scale), -127, 127).astype(np.int8))
        return cls(MAGIC + struct.pack("<4f", *scales) + b"".join(t.tobytes() for t in tensors))


@dataclass(frozen=True)
class CultureCapsule:
    """Portable policy, optionally accompanied by the legacy chain atlas."""

    policy: PolicyPacket
    atlas: bytes | None = None

    def __post_init__(self) -> None:
        if self.atlas is not None and (not isinstance(self.atlas, bytes) or len(self.atlas) != ATLAS_BYTES):
            raise PacketError("The legacy atlas must contain exactly 144 int8 bytes")

    @property
    def raw(self) -> bytes:
        return self.policy.raw + (self.atlas or b"")

    @property
    def payload_bytes(self) -> int:
        return len(self.raw)

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.raw).hexdigest()

    def source_states(self) -> np.ndarray:
        if self.atlas is None:
            raise PacketError("Relational grounding requires a source atlas")
        return np.frombuffer(self.atlas, np.int8).reshape(24, 6).astype(np.float32)

    def to_envelope(self) -> bytes:
        """Add format metadata/checksum. Header bytes count toward wire cost."""
        metadata = {
            "schema_version": 1,
            "policy_format": "IAPCV2",
            "atlas_format": "int8-8x3x6-chain-order" if self.atlas is not None else None,
            "payload_bytes": self.payload_bytes,
            "payload_sha256": self.sha256,
        }
        header = json.dumps(metadata, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return ENVELOPE_MAGIC + struct.pack("<I", len(header)) + header + self.raw

    def save(self, path: str | Path, *, framed: bool = False) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(self.to_envelope() if framed else self.raw)

    @classmethod
    def from_bytes(cls, data: bytes) -> "CultureCapsule":
        if not isinstance(data, bytes):
            raise PacketError("Capsule input must be immutable bytes")
        if len(data) > MAX_ENVELOPE_BYTES:
            raise PacketError("Capsule exceeds maximum envelope size")
        if data.startswith(ENVELOPE_MAGIC):
            if len(data) < 12:
                raise PacketError("Truncated envelope")
            header_len = struct.unpack("<I", data[8:12])[0]
            if header_len > 8192 or len(data) < 12 + header_len:
                raise PacketError("Invalid envelope header length")
            try:
                meta = json.loads(data[12:12 + header_len])
            except (ValueError, UnicodeError) as exc:
                raise PacketError("Invalid envelope metadata") from exc
            if not isinstance(meta, dict) or meta.get("schema_version") != 1 or meta.get("policy_format") != "IAPCV2":
                raise PacketError("Unsupported envelope schema/policy")
            payload = data[12 + header_len:]
            if meta.get("payload_bytes") != len(payload) or meta.get("payload_sha256") != hashlib.sha256(payload).hexdigest():
                raise PacketError("Capsule length/checksum mismatch")
            atlas_format = "int8-8x3x6-chain-order" if len(payload) == 241 else None
            if meta.get("atlas_format") != atlas_format:
                raise PacketError("Atlas metadata does not match payload")
            data = payload
        if len(data) not in (POLICY_BYTES, POLICY_BYTES + ATLAS_BYTES):
            raise PacketError("Expected 97-byte policy or 241-byte policy+atlas")
        return cls(PolicyPacket(data[:POLICY_BYTES]), data[POLICY_BYTES:] or None)

    @classmethod
    def load(cls, path: str | Path) -> "CultureCapsule":
        p = Path(path)
        if p.stat().st_size > MAX_ENVELOPE_BYTES:
            raise PacketError("Refusing oversized capsule")
        return cls.from_bytes(p.read_bytes())
