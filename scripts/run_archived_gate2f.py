#!/usr/bin/env python3
"""Run the unchanged archived Gate 2F script in a temporary extracted directory."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["ground", "transfer"], default="ground")
    ap.add_argument("--teacher", choices=["fly", "transformer"], default="transformer")
    ap.add_argument("--direction", choices=["f2t", "t2f"], default="f2t")
    ap.add_argument("--budget", type=int, default=36)
    ap.add_argument("--reps", type=int, default=1)
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--steps", type=int)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    if args.reps < 1 or args.start < 0 or args.budget < 0:
        ap.error("Invalid budget/replicate settings")
    output = args.output.resolve()
    if output.exists():
        raise SystemExit("Refusing to replace an existing result")
    output.parent.mkdir(parents=True, exist_ok=True)
    archive = ROOT / "archive/IAP_Gate2F_Ontology_Translation.zip"
    sources = json.loads((ROOT / "evidence/SOURCES.json").read_text())["sources"]
    expected = next(x["sha256"] for x in sources if x["gate"] == "2f")
    if hashlib.sha256(archive.read_bytes()).hexdigest() != expected:
        raise SystemExit("Historical archive failed checksum verification")
    with tempfile.TemporaryDirectory(prefix="iap_legacy_") as tmp:
        base = Path(tmp).resolve()
        with zipfile.ZipFile(archive) as z:
            for entry in z.infolist():
                if not (base / entry.filename).resolve().is_relative_to(base):
                    raise SystemExit("Unsafe archive path")
            z.extractall(base)
        script = base / "iap_gate2f_ontology_translation/source/gate2f_experiment.py"
        cmd = [sys.executable, str(script), "--mode", args.mode, "--teacher", args.teacher,
               "--direction", args.direction, "--budget", str(args.budget), "--reps", str(args.reps),
               "--start", str(args.start), "--out", str(output)]
        if args.steps is not None:
            cmd += ["--steps", str(args.steps)]
        subprocess.run(cmd, check=True)
    print("Original-source run complete:", output)


if __name__ == "__main__":
    main()
