"""Auditable experiment runner for the four supported mismatch families.

Historical evidence stays immutable. New runs get their own configuration,
source hash, state hashes, query transcripts, native recipient checkpoints and
budget counters. A run completing is not the same as a scientific gate passing.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import sys
import time
import numpy as np
import torch
from . import __version__
from .absorption import absorb
from .contracts import GroundingResult, Progress, quiet
from .grounding import ground_ontology, ground_permutation, ground_relational
from .models import ModelSpec, make_model, predict, save_student, load_student, state_fingerprint
from .packets import CultureCapsule
from .reporting import write_json, read_json, write_csv, sha256, summarize_rows
from .resources import teacher_capsule, verify_assets
from .tasks import make_world

DIRECTIONS = {"f2t": ("fly", "transformer"), "t2f": ("transformer", "fly"),
              "f2m": ("fly", "mlp"), "m2f": ("mlp", "fly")}
CONDITIONS = {"grounded_culture", "query_only_no_packet", "ungrounded_identity", "wrong_culture"}


@dataclass(frozen=True)
class ExperimentConfig:
    name: str = "iap-v1-smoke"
    purpose: str = "engineering smoke; not a new confirmation"
    family: str = "ontology"
    directions: tuple[str, ...] = ("f2t", "t2f")
    replicates: int = 1
    start_rep: int = 0
    seed_base: int = 1_200_000
    direction_stride: int = 100_000
    queries: int = 36
    outdim: int = 8
    updates: dict[str, int] = field(default_factory=lambda: {"f2t": 64, "t2f": 64})
    conditions: tuple[str, ...] = ("grounded_culture", "query_only_no_packet", "ungrounded_identity")
    pairing: str = "matched_initialization"
    active_grounding: bool = True
    threads: int = 1
    packet_paths: dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        if any(k not in {"fly", "mlp", "transformer"} or not isinstance(v, str) for k, v in self.packet_paths.items()):
            raise ValueError("packet_paths must map teacher kinds to local paths")
        if self.family not in {"aligned", "permutation", "relational", "ontology"}:
            raise ValueError("Unknown world family")
        if not self.directions or any(d not in DIRECTIONS for d in self.directions) or len(set(self.directions)) != len(self.directions):
            raise ValueError("Invalid/duplicate directions")
        if not self.conditions or any(c not in CONDITIONS for c in self.conditions) or len(set(self.conditions)) != len(self.conditions):
            raise ValueError("Invalid/duplicate conditions")
        if self.replicates < 1 or self.start_rep < 0 or self.seed_base < 0 or self.direction_stride < 1:
            raise ValueError("Invalid seed/replicate configuration")
        if self.pairing not in {"matched_initialization", "historical_offsets"}:
            raise ValueError("Unknown pairing mode")
        if self.queries < 0 or self.outdim < 1 or self.threads < 1:
            raise ValueError("Invalid query/dimension/thread setting")
        if self.family == "aligned" and self.queries != 0:
            raise ValueError("Aligned family uses no calibration")
        if "query_only_no_packet" in self.conditions and self.queries == 0:
            raise ValueError("Query-only control requires at least one query; remove it for aligned experiments")
        if set(self.updates) != set(self.directions) or any(not isinstance(v, int) or v < 0 for v in self.updates.values()):
            raise ValueError("Supply a nonnegative integer update budget for every direction")

    @classmethod
    def load(cls, path: str | Path):
        obj = read_json(path)
        if not isinstance(obj, dict):
            raise ValueError("Configuration must be a JSON object")
        for key in ("directions", "conditions"):
            if key in obj:
                obj[key] = tuple(obj[key])
        return cls(**obj)

    @property
    def sha256(self):
        return hashlib.sha256(json.dumps(asdict(self), sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def source_hash() -> str:
    root = Path(__file__).parent
    h = hashlib.sha256()
    for path in sorted(root.rglob("*.py")):
        h.update(str(path.relative_to(root)).replace("\\", "/").encode())
        h.update(path.read_bytes())
    return h.hexdigest()


def machine_report() -> dict:
    return {"python": sys.version, "platform": platform.system(), "machine": platform.machine(),
            "packages": {name: importlib.metadata.version(name) for name in ("numpy", "scipy", "torch")},
            "device": "cpu", "torch_threads": torch.get_num_threads(),
            "privacy": "no username, hostname, environment variables, or absolute user paths recorded"}


def ground(capsule, world, oracle, family, queries, seed=0, active=True, progress=quiet):
    if family == "aligned":
        return GroundingResult(capsule.policy(world.observations), np.ones(world.state_count, bool), (), {"family": "aligned"})
    fn = {"permutation": ground_permutation, "relational": ground_relational, "ontology": ground_ontology}[family]
    return fn(capsule, world, oracle, queries, seed=seed, active=active, progress=progress)


def identity_targets(capsule: CultureCapsule, public) -> np.ndarray:
    if public.actions == 2:
        # Intentionally invalid alignment: first six channels, zero-pad if fewer.
        x = np.zeros((public.state_count, 6), np.float32)
        width = min(public.observations.shape[1], 6)
        x[:, :width] = public.observations[:, :width]
        return capsule.policy(x)
    source_pred = capsule.policy(capsule.source_states()).argmax(1).reshape(8, 3)
    target = np.full((public.state_count, 4), -1., np.float32)
    for i, chain in enumerate(public.chains):
        for pos, gid in enumerate(chain):
            stage = min(2, int(3 * pos / len(chain)))
            target[gid, int(source_pred[i, stage])] = 1
    return target


def run_trial(config: ExperimentConfig, direction: str, rep: int, output: Path, progress: Progress) -> list[dict]:
    teacher_kind, recipient_kind = DIRECTIONS[direction]
    offset = 0 if direction in {"t2f", "m2f"} else config.direction_stride
    seed = config.seed_base + offset + rep
    world = make_world(config.family, seed, config.outdim)
    public = world.public
    capsule = (CultureCapsule.load(config.packet_paths[teacher_kind]) if teacher_kind in config.packet_paths
               else teacher_capsule(teacher_kind, relational=config.family in {"relational", "ontology"}))
    oracle = world.oracle(config.queries)
    start = time.perf_counter()
    grounded = ground(capsule, public, oracle, config.family, config.queries, seed + 1, config.active_grounding, progress)
    ground_seconds = time.perf_counter() - start
    ground_pred = grounded.targets.argmax(1)
    ground_pred[~grounded.predicted_roles] = -1
    ground_score = world.score(ground_pred)
    ground_dir = output
    ground_dir.mkdir(parents=True, exist_ok=True)
    write_json(ground_dir / "grounding.json", {
        "teacher": teacher_kind, "source_payload_sha256": capsule.sha256,
        "policy_payload_bytes": len(capsule.policy.raw), "atlas_payload_bytes": len(capsule.atlas or b""),
        "total_payload_bytes": capsule.payload_bytes, "envelope_wire_bytes": len(capsule.to_envelope()),
        "oracle": oracle.accounting(), "records": [asdict(r) for r in grounded.records],
        "grounding_metrics": ground_score, "diagnostics": grounded.diagnostics,
        "wall_seconds": ground_seconds,
    })
    # Evaluator-only fixture. It is never supplied to grounding or absorption.
    np.savez_compressed(ground_dir / "evaluation_fixture.npz", observations=public.observations,
                        labels=world.labels, chain_lengths=np.array([len(c) for c in public.chains]),
                        state_order=np.array([i for c in public.chains for i in c]))
    write_json(ground_dir / "truth_for_audit_only.json", world.hidden_metadata)
    rows = []
    offsets = {"grounded_culture": (10, 101), "query_only_no_packet": (1010, 201),
               "ungrounded_identity": (2010, 301), "wrong_culture": (3010, 401)}
    for condition in config.conditions:
        progress({"event": "condition_start", "direction": direction, "rep": rep, "condition": condition})
        if config.pairing == "historical_offsets":
            model_offset, train_offset = offsets[condition]
        else:
            model_offset, train_offset = 10, 101
        spec = ModelSpec(recipient_kind, public.observations.shape[1], public.actions,
                         seed + model_offset, 7102 if rep % 2 == 0 else 7103)
        model = make_model(spec)
        if condition in {"grounded_culture", "wrong_culture"}:
            targets = grounded.targets.copy()
            indices = np.flatnonzero(grounded.predicted_roles)
            if condition == "wrong_culture":
                targets = np.roll(targets, 1, axis=1)
        elif condition == "query_only_no_packet":
            targets = np.zeros_like(grounded.targets)
            indices = np.array([r.state for r in grounded.records if r.label >= 0], np.int64)
            for record in grounded.records:
                if record.label >= 0:
                    targets[record.state] = -1
                    targets[record.state, record.label] = 1
        else:
            targets = identity_targets(capsule, public)
            indices = np.arange(public.state_count)
        evaluator = lambda m: {k: v for k, v in world.score(predict(m, public.observations).argmax(1)).items() if k != "role_accuracy"}
        t0 = time.perf_counter()
        report = absorb(model, public.observations, targets, indices, updates=config.updates[direction],
                        seed=seed + train_offset, evaluator=evaluator, progress=progress)
        final = evaluator(model)
        path = ground_dir / f"{condition}.pt"
        save_student(model, spec, path)
        reloaded, _ = load_student(path)
        if not np.array_equal(predict(model, public.observations), predict(reloaded, public.observations)):
            raise RuntimeError("Packet-free checkpoint reload does not reproduce predictions")
        report_dict = asdict(report)
        report_dict.update({"model_spec": asdict(spec), "checkpoint_sha256": sha256(path),
                            "packet_access_during_evaluation": False, "reload_logits_equal": True,
                            "learning_rate": .03 if recipient_kind == "fly" else .01,
                            "optimizer": "Adam", "batch_size_max": 32,
                            "pairing": config.pairing})
        write_json(ground_dir / f"{condition}.json", report_dict)
        row = {"direction": direction, "rep": rep, "world_seed": seed, "condition": condition,
               "recipient": recipient_kind, "fly_assignment": spec.fly_seed if recipient_kind == "fly" else None,
               "updates": report.updates, "exposure_draws": report.exposure_draws,
               "unique_states_exposed": report.unique_states_exposed, "batch_examples": report.batch_examples,
               "calibration_queries_used": len(grounded.records) if condition != "ungrounded_identity" else 0,
               "source_payload_bytes": capsule.payload_bytes if condition != "query_only_no_packet" else 0,
               "environmental_rewards_during_absorption": 0, **final,
               "ground_action_accuracy": ground_score["action_accuracy"],
               "ground_sequence_accuracy": ground_score["sequence_accuracy"],
               "fixed_buffers_unchanged": report.fixed_buffers_unchanged,
               "wall_seconds": time.perf_counter() - t0,
               "initial_state_sha256": report.initial_state_sha256,
               "final_state_sha256": report.final_state_sha256}
        rows.append(row)
        progress({"event": "condition_done", "direction": direction, "rep": rep, "condition": condition, **final})
    files = {str(p.relative_to(ground_dir)).replace("\\", "/"): sha256(p) for p in sorted(ground_dir.iterdir()) if p.is_file() and p.name != "completion.json"}
    write_json(ground_dir / "completion.json", {"config_sha256": config.sha256, "source_sha256": source_hash(), "rows": rows, "files": files})
    return rows


def run(config: ExperimentConfig, output: str | Path, *, resume: bool = False, progress: Progress = quiet) -> dict:
    root = Path(output)
    if root.exists() and any(root.iterdir()) and not resume:
        raise FileExistsError("Output directory is nonempty; choose a new path or use --resume")
    root.mkdir(parents=True, exist_ok=True)
    manifest_path = root / "run_manifest.json"
    code_hash = source_hash()
    packet_hashes = {kind: CultureCapsule.load(path).sha256 for kind, path in config.packet_paths.items()}
    if resume and manifest_path.exists():
        old = read_json(manifest_path)
        if old.get("config_sha256") != config.sha256 or old.get("source_sha256") != code_hash or old.get("external_packet_sha256", {}) != packet_hashes:
            raise ValueError("Resume refused: configuration or source changed")
    elif resume and any(root.iterdir()):
        raise ValueError("Cannot resume an unrecognized output directory")
    torch.set_num_threads(config.threads)
    assets = verify_assets()
    manifest = {"version": __version__, "status": "running", "config": asdict(config),
                "config_sha256": config.sha256, "source_sha256": code_hash, "external_packet_sha256": packet_hashes,
                "machine": machine_report(), "assets_verified": assets["asset_count"],
                "started_utc": datetime.now(timezone.utc).isoformat(),
                "scope": "finite-support research benchmark; not a scientific pass/fail verdict"}
    write_json(manifest_path, manifest)
    rows = []
    try:
        for direction in config.directions:
            for rep in range(config.start_rep, config.start_rep + config.replicates):
                trial_dir = root / f"{direction}_rep{rep:04d}"
                done = trial_dir / "completion.json"
                if resume and done.exists():
                    result = read_json(done)
                    if result["config_sha256"] != config.sha256 or result["source_sha256"] != code_hash:
                        raise ValueError("Completed-trial configuration/source mismatch")
                    for name, expected in result["files"].items():
                        p = (trial_dir / name).resolve()
                        if not p.is_relative_to(trial_dir.resolve()) or not p.is_file() or sha256(p) != expected:
                            raise ValueError("Completed-trial file failed integrity verification")
                    rows += result["rows"]
                    progress({"event": "resume_skip", "direction": direction, "rep": rep})
                else:
                    progress({"event": "trial_start", "direction": direction, "rep": rep})
                    rows += run_trial(config, direction, rep, trial_dir, progress)
                write_csv(root / "results.csv", rows)
        aggregates, deltas = summarize_rows(rows)
        write_csv(root / "aggregate.csv", aggregates)
        write_csv(root / "paired_deltas.csv", deltas)
        manifest["status"] = "completed"
        manifest["result_rows"] = len(rows)
        manifest["result_sha256"] = sha256(root / "results.csv")
        manifest["finished_utc"] = datetime.now(timezone.utc).isoformat()
        write_json(manifest_path, manifest)
        progress({"event": "run_completed", "rows": len(rows)})
        return {"rows": rows, "aggregate": aggregates, "paired_deltas": deltas}
    except BaseException as exc:
        manifest["status"] = "interrupted" if isinstance(exc, KeyboardInterrupt) else "failed"
        manifest["error_type"] = type(exc).__name__
        write_json(manifest_path, manifest)
        raise
