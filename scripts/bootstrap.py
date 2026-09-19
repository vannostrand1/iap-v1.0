#!/usr/bin/env python3
"""CPU-only local launcher. No external agents, credentials or system Python install."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import venv
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--action", choices=["setup", "smoke", "demo", "test", "confirmation"], default="smoke")
    a = p.parse_args()
    if not (ROOT / "pyproject.toml").is_file() or not (ROOT / "src/iap").is_dir():
        raise SystemExit("Extract the entire ZIP before running; companion files are missing.")
    if not (3, 11) <= sys.version_info[:2] <= (3, 13):
        raise SystemExit("Use an installed Python 3.11, 3.12 or 3.13 for this tested dependency set.")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    logs = ROOT / "logs"
    logs.mkdir(exist_ok=True)
    logpath = logs / f"{a.action}_{stamp}.log"
    envdir = ROOT / ".venv_iap"
    executable = envdir / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    output = ROOT / "runs" / f"{a.action}_{stamp}"
    env = dict(os.environ, PYTHONUNBUFFERED="1", PIP_DISABLE_PIP_VERSION_CHECK="1")

    def call(argv):
        print("Running:", subprocess.list2cmdline([str(x) for x in argv]), flush=True)
        with logpath.open("a", encoding="utf-8") as log:
            proc = subprocess.Popen([str(x) for x in argv], cwd=ROOT, env=env,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    text=True, encoding="utf-8", errors="replace")
            assert proc.stdout is not None
            for line in proc.stdout:
                print(line, end="", flush=True)
                log.write(line)
                log.flush()
            code = proc.wait()
            if code:
                raise subprocess.CalledProcessError(code, argv)

    try:
        if not executable.is_file():
            print("Creating isolated .venv_iap (your Doom environment is untouched).", flush=True)
            venv.EnvBuilder(with_pip=True).create(envdir)
        signature = hashlib.sha256((ROOT / "pyproject.toml").read_bytes() +
                                   (ROOT / "requirements-tested-cpu.txt").read_bytes()).hexdigest()
        statefile = envdir / "iap_setup.json"
        state = json.loads(statefile.read_text()) if statefile.exists() else {}
        if state.get("signature") != signature:
            call([executable, "-m", "pip", "install", "torch==2.10.0", "--index-url", "https://download.pytorch.org/whl/cpu"])
            call([executable, "-m", "pip", "install", "-r", ROOT / "requirements-tested-cpu.txt"])
            call([executable, "-m", "pip", "install", "-e", ROOT])
            statefile.write_text(json.dumps({"signature": signature}), encoding="utf-8")
        call([executable, "-m", "iap", "doctor"])
        if a.action == "setup":
            print("Setup complete. Run RUN_IAP_SMOKE.bat next.")
            return 0
        if a.action == "test":
            call([executable, "-m", "pip", "install", "pytest>=8,<10"])
            output.mkdir(parents=True, exist_ok=True)
            call([executable, "-m", "pytest", "-q", f"--junitxml={output / 'pytest.xml'}"])
        else:
            name = {"smoke": "smoke", "demo": "demo", "confirmation": "fresh_confirmation"}[a.action]
            call([executable, "-m", "iap", "run", "--config", ROOT / f"configs/{name}.json", "--output", output])
        archive = output.with_suffix(".zip")
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
            for f in sorted(output.rglob("*")):
                if f.is_file():
                    z.write(f, f.relative_to(output.parent))
            z.write(logpath, f"{output.name}/launcher.log")
        print(f"\nCompleted. Results: {output}\nUpload archive: {archive}", flush=True)
        return 0
    except KeyboardInterrupt:
        print(f"Interrupted. Log preserved: {logpath}", flush=True)
        return 130
    except Exception as exc:
        print(f"Launcher failed: {exc}\nLog preserved: {logpath}", flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
