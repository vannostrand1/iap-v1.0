"""Command line; long-running actions always emit progress unless --quiet."""
from __future__ import annotations
import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys
import traceback
import numpy as np
from . import __version__
from .packets import CultureCapsule
from .reporting import write_json, read_json, write_csv, summarize_run, sha256
from .resources import verify_assets, teacher_capsule


def emit(event):
    print(json.dumps(event, sort_keys=True, allow_nan=False), flush=True)


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="iap", description="IAP v1.0 bounded cross-architecture cultural transmission")
    p.add_argument("--version", action="version", version=__version__)
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor", help="Verify included assets and print runtime versions")
    run = sub.add_parser("run", help="Execute an explicit, validated JSON configuration")
    run.add_argument("--config", required=True, type=Path)
    run.add_argument("--output", required=True, type=Path)
    run.add_argument("--resume", action="store_true")
    run.add_argument("--quiet", action="store_true")
    demo = sub.add_parser("demo", help="One ontology, both directions, three controls; not confirmation")
    demo.add_argument("--output", type=Path, default=Path("runs/demo"))
    demo.add_argument("--quiet", action="store_true")
    ground = sub.add_parser("ground", help="Ground a packaged teacher without training recipients")
    ground.add_argument("--family", choices=["permutation", "relational", "ontology"], default="ontology")
    ground.add_argument("--teacher", choices=["fly", "mlp", "transformer"], default="transformer")
    ground.add_argument("--budget", type=int, default=36)
    ground.add_argument("--seed", type=int, default=1800000)
    ground.add_argument("--replicates", type=int, default=1)
    ground.add_argument("--outdim", type=int, default=8)
    ground.add_argument("--passive", action="store_true")
    ground.add_argument("--output", type=Path, required=True)
    packet = sub.add_parser("packet", help="Inspect or export byte-level cultural packets")
    ps = packet.add_subparsers(dest="packet_command", required=True)
    inspect = ps.add_parser("inspect")
    inspect.add_argument("path", type=Path)
    export = ps.add_parser("export")
    export.add_argument("--teacher", choices=["fly", "mlp", "transformer"], required=True)
    export.add_argument("--policy-only", action="store_true")
    export.add_argument("--framed", action="store_true")
    export.add_argument("--output", required=True, type=Path)
    distill = sub.add_parser("distill", help="Re-distill one supplied native teacher checkpoint")
    distill.add_argument("--teacher", choices=["fly", "mlp", "transformer"], required=True)
    distill.add_argument("--updates", type=int, default=2500)
    distill.add_argument("--seed", type=int, default=44)
    distill.add_argument("--output", type=Path, required=True)
    teacher = sub.add_parser("train-teacher", help="Reward-train a fresh canonical teacher, then distill")
    teacher.add_argument("--kind", choices=["fly", "mlp", "transformer"], default="mlp")
    teacher.add_argument("--seed", type=int, default=6101)
    teacher.add_argument("--decisions", type=int, default=4096)
    teacher.add_argument("--packet-updates", type=int, default=2500)
    teacher.add_argument("--output", required=True, type=Path)
    evaluate = sub.add_parser("evaluate", help="Evaluate a standalone native student; no packet argument")
    evaluate.add_argument("checkpoint", type=Path)
    evaluate.add_argument("--fixture", required=True, type=Path)
    summarize = sub.add_parser("summarize", help="Recompute run aggregate and conditional paired intervals")
    summarize.add_argument("run_directory", type=Path)
    audit = sub.add_parser("audit", help="Verify historical archives and recompute E/F summary arithmetic")
    audit.add_argument("--repository", type=Path, default=Path("."))
    audit.add_argument("--output", type=Path)
    return p


def execute(args) -> int:
    if args.command == "doctor":
        from .experiments import machine_report
        emit({"version": __version__, "assets": verify_assets(), "runtime": machine_report()})
    elif args.command in {"run", "demo"}:
        from .experiments import ExperimentConfig, run
        from .contracts import quiet
        config = (ExperimentConfig.load(args.config) if args.command == "run" else
                  ExperimentConfig(name="iap-v1-demo", updates={"f2t": 512, "t2f": 1024}))
        run(config, args.output, resume=getattr(args, "resume", False), progress=quiet if args.quiet else emit)
        emit({"event": "output_ready", "directory": str(args.output), "scientific_confirmation": False})
    elif args.command == "packet":
        if args.packet_command == "inspect":
            cap = CultureCapsule.load(args.path)
        else:
            cap = teacher_capsule(args.teacher, relational=not args.policy_only)
            cap.save(args.output, framed=args.framed)
        emit({"policy_bytes": len(cap.policy.raw), "atlas_bytes": len(cap.atlas or b""),
              "payload_bytes": cap.payload_bytes, "envelope_wire_bytes": len(cap.to_envelope()), "sha256": cap.sha256})
    elif args.command == "ground":
        from .tasks import make_world
        from .experiments import ground
        if args.replicates < 1:
            raise ValueError("Replicates must be positive")
        cap = teacher_capsule(args.teacher, relational=args.family != "permutation")
        rows, logs = [], []
        for rep in range(args.replicates):
            world = make_world(args.family, args.seed + rep, args.outdim)
            oracle = world.oracle(args.budget)
            result = ground(cap, world.public, oracle, args.family, args.budget,
                            args.seed + rep + 1, not args.passive, emit)
            prediction = np.where(result.predicted_roles, result.targets.argmax(1), -1)
            rows.append({"teacher": args.teacher, "family": args.family, "rep": rep, "world_seed": args.seed + rep,
                         **world.score(prediction), **oracle.accounting()})
            logs.append({"rep": rep, "records": [asdict(r) for r in result.records], "diagnostics": result.diagnostics})
        if args.output.exists():
            raise FileExistsError("Refusing to overwrite an existing grounding result")
        write_csv(args.output, rows)
        write_json(args.output.with_suffix(".queries.json"), logs)
        emit({"event": "grounding_complete", "rows": len(rows), "output": str(args.output)})
    elif args.command in {"distill", "train-teacher"}:
        import torch
        from .models import load_teacher, make_model, ModelSpec, save_student
        from .distillation import distill, train_teacher
        torch.set_num_threads(1)
        if args.command == "distill":
            model = load_teacher(args.teacher)
            cap, result = distill(model, updates=args.updates, seed=args.seed, progress=emit)
            if args.output.exists():
                raise FileExistsError("Refusing to overwrite an existing packet")
            cap.save(args.output)
            write_json(args.output.with_suffix(".json"), result)
        else:
            if args.output.exists() and any(args.output.iterdir()):
                raise FileExistsError("Teacher output directory is nonempty")
            args.output.mkdir(parents=True, exist_ok=True)
            spec = ModelSpec(args.kind, 6, 2, args.seed, 7101)
            model = make_model(spec)
            lr = .03 if args.kind == "fly" else (.003 if args.kind == "transformer" else .01)
            learned = train_teacher(model, decisions=args.decisions, seed=args.seed, learning_rate=lr, progress=emit)
            cap, packed = distill(model, updates=args.packet_updates, seed=args.seed + 1, progress=emit)
            cap.save(args.output / "culture.iapx")
            save_student(model, spec, args.output / "teacher.pt")
            result = {"teacher": learned, "distillation": packed, "model_spec": asdict(spec)}
            write_json(args.output / "report.json", result)
        emit(result)
    elif args.command == "evaluate":
        from .models import load_student, predict
        from .tasks import BenchmarkWorld
        from .contracts import PublicWorld
        model, spec = load_student(args.checkpoint)
        with np.load(args.fixture, allow_pickle=False) as z:
            x, labels = z["observations"], z["labels"]
            order, lengths = z["state_order"], z["chain_lengths"]
            pos, chains = 0, []
            for length in lengths:
                chains.append(tuple(order[pos:pos + int(length)].tolist()))
                pos += int(length)
        world = BenchmarkWorld(PublicWorld(x, tuple(chains), spec.actions), labels, {})
        metrics = world.score(predict(model, x).argmax(1))
        metrics.pop("role_accuracy", None)
        emit({"model_spec": asdict(spec), "packet_used": False, **metrics})
    elif args.command == "summarize":
        result = summarize_run(args.run_directory)
        emit(result)
    elif args.command == "audit":
        from .audit import audit_evidence
        result = audit_evidence(args.repository)
        if args.output:
            write_json(args.output, result)
        emit(result)
        return 0 if result["status"] == "passed" else 1
    return 0


def main(argv=None) -> int:
    args = parser().parse_args(argv)
    try:
        return execute(args)
    except KeyboardInterrupt:
        print("Interrupted. Completed trials can be resumed with the unchanged configuration.", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"IAP error: {type(exc).__name__}: {exc}", file=sys.stderr)
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
