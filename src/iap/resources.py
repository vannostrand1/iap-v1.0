"""Package-relative data access with checksum verification; no downloads."""
from __future__ import annotations

import hashlib
from importlib.resources import files
import json
from pathlib import Path
from .packets import CultureCapsule, PolicyPacket


def root() -> Path:
    return Path(str(files("iap.assets")))


def manifest() -> dict:
    return json.loads((root() / "MANIFEST.json").read_text(encoding="utf-8"))


def asset(relative: str, *, verify: bool = True) -> Path:
    p = (root() / relative).resolve()
    if not p.is_relative_to(root().resolve()):
        raise ValueError("Asset path escapes the package")
    if verify:
        entries = {e["path"]: e for e in manifest()["assets"]}
        if relative not in entries:
            raise ValueError(f"Unregistered asset: {relative}")
        expected = entries[relative]
        if not p.is_file() or p.stat().st_size != expected["bytes"] or hashlib.sha256(p.read_bytes()).hexdigest() != expected["sha256"]:
            raise ValueError(f"Asset checksum mismatch: {relative}")
    return p


def verify_assets() -> dict:
    checked = []
    for entry in manifest()["assets"]:
        asset(entry["path"])
        checked.append(entry["path"])
    return {"status": "passed", "asset_count": len(checked), "assets": checked}


def teacher_capsule(teacher: str, *, relational: bool = True) -> CultureCapsule:
    if teacher not in {"fly", "mlp", "transformer"}:
        raise ValueError(f"Unknown teacher: {teacher}")
    policy = PolicyPacket(asset(f"packets/{teacher}_teacher_97b.iap").read_bytes())
    atlas = asset("packets/source_relational_atlas_144b.bin").read_bytes() if relational else None
    return CultureCapsule(policy, atlas)
