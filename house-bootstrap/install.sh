#!/usr/bin/env bash
# House named-install. Idempotent. Catalog driven.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
CATALOG="${ROOT}/catalog.json"
LOG="${ROOT}/install.log"
HOUSE_ROOT="${HOUSE_ROOT:-$HOME/adam-house}"
DRY=0
ONLY=""

export HOUSE_ROOT

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY=1; shift ;;
    --only) ONLY="${2:-}"; shift 2 ;;
    --house-root) HOUSE_ROOT="${2:-}"; export HOUSE_ROOT; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

need() { command -v "$1" >/dev/null 2>&1 || { echo "missing $1"; exit 1; }; }
need python3

python3 - "$CATALOG" "$ONLY" "$DRY" <<'PY'
import json, os, sys, subprocess, shlex
catalog_path, only, dry = sys.argv[1], sys.argv[2], sys.argv[3] == "1"
house = os.environ.get("HOUSE_ROOT", os.path.expanduser("~/adam-house"))
os.environ["HOUSE_ROOT"] = house
data = json.load(open(catalog_path))

def expand(s):
    return os.path.expandvars(s or "")

def check(pkg):
    cmd = expand(pkg.get("check") or "")
    if not cmd:
        return False
    return subprocess.call(["bash","-lc", cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

def do(cmd):
    print(cmd, flush=True)
    if dry:
        return 0
    return subprocess.call(["bash","-lc", cmd])

os.makedirs(house, exist_ok=True)
os.makedirs(os.path.join(house, "src"), exist_ok=True)
os.makedirs(os.path.join(house, "vessels"), exist_ok=True)
os.makedirs(os.path.join(house, "venv"), exist_ok=True)

venv = os.path.join(house, "venv")
pip = os.path.join(venv, "bin", "pip")
if not dry and not os.path.exists(pip):
    subprocess.check_call([sys.executable, "-m", "venv", venv])

n_ok = n_skip = n_fail = 0
for pkg in data["packages"]:
    if only and pkg["id"] != only:
        continue
    if not pkg.get("enabled", False):
        print(f"SKIP {pkg['id']} disabled future/optional")
        n_skip += 1
        continue
    if check(pkg):
        print(f"OK   {pkg['id']} already present")
        n_ok += 1
        continue
    kind = pkg["kind"]
    spec = pkg["spec"]
    rc = 0
    if kind == "brew":
        rc = do(f"brew install {shlex.quote(spec)}")
    elif kind == "script" and pkg["id"] == "homebrew":
        rc = do('/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"')
    elif kind == "script" and pkg["id"] == "ollama":
        rc = do("curl -fsSL https://ollama.com/install.sh | sh")
    elif kind == "ollama":
        rc = do(f"ollama pull {shlex.quote(spec)}")
    elif kind == "pip":
        rc = do(f"{shlex.quote(pip)} install {shlex.quote(spec)}")
    elif kind == "git":
        dest = expand(pkg["dest"])
        branch = pkg.get("branch", "main")
        if os.path.isdir(os.path.join(dest, ".git")):
            rc = do(f"git -C {shlex.quote(dest)} fetch --all && git -C {shlex.quote(dest)} checkout {shlex.quote(branch)} && git -C {shlex.quote(dest)} pull --ff-only")
        else:
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            rc = do(f"git clone --branch {shlex.quote(branch)} {shlex.quote(spec)} {shlex.quote(dest)}")
    elif kind == "hf":
        print(f"REFUSE {pkg['id']} Hugging Face jobs stay manual named fetches")
        n_skip += 1
        continue
    else:
        print(f"FAIL {pkg['id']} unknown kind {kind}")
        n_fail += 1
        continue
    if rc == 0:
        print(f"DONE {pkg['id']}")
        n_ok += 1
    else:
        print(f"FAIL {pkg['id']} rc={rc}")
        n_fail += 1

print(f"summary ok={n_ok} skip={n_skip} fail={n_fail}")
sys.exit(1 if n_fail else 0)
PY
