#!/usr/bin/env python3
"""Install the built wheel into an isolated target and exercise package resources."""
from pathlib import Path
import os
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    wheels = sorted((ROOT / "dist").glob("inter_agent_protocol-1.0.0-*.whl"))
    if len(wheels) != 1:
        raise SystemExit("Build exactly one v1.0 wheel in dist/ first: python -m build")
    with tempfile.TemporaryDirectory(prefix="iap_wheel_check_") as tmp:
        target = Path(tmp) / "installed"
        subprocess.run([sys.executable, "-m", "pip", "install", "--no-deps", "--target", str(target), str(wheels[0])], check=True)
        env = dict(os.environ, PYTHONPATH=str(target))
        code = "import iap; from pathlib import Path; assert Path(iap.__file__).resolve().is_relative_to(Path(" + repr(str(target)) + ").resolve()); print(iap.__version__)"
        subprocess.run([sys.executable, "-c", code], cwd=tmp, env=env, check=True)
        subprocess.run([sys.executable, "-m", "iap", "doctor"], cwd=tmp, env=env, check=True)
        packet = str(Path(tmp) / "capsule.iapc")
        subprocess.run([sys.executable, "-m", "iap", "packet", "export", "--teacher", "fly", "--framed", "--output", packet], cwd=tmp, env=env, check=True)
        subprocess.run([sys.executable, "-m", "iap", "packet", "inspect", packet], cwd=tmp, env=env, check=True)
        run_dir = Path(tmp) / "smoke"
        subprocess.run([sys.executable, "-m", "iap", "run", "--config", str(ROOT / "configs/smoke.json"), "--output", str(run_dir), "--quiet"], cwd=tmp, env=env, check=True)
        trial = run_dir / "f2t_rep0000"
        subprocess.run([sys.executable, "-m", "iap", "evaluate", str(trial / "grounded_culture.pt"), "--fixture", str(trial / "evaluation_fixture.npz")], cwd=tmp, env=env, check=True)
    print("Wheel isolated-target verification passed.")


if __name__ == "__main__":
    main()
