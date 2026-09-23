#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
HOUSE_ROOT="${HOUSE_ROOT:-$HOME/adam-house}"
export HOUSE_ROOT
python3 - "$ROOT/catalog.json" <<'PY'
import json, os, sys, subprocess
data = json.load(open(sys.argv[1]))
print(f"HOUSE_ROOT={os.environ.get('HOUSE_ROOT')}")
print(f"{'id':28} {'group':10} {'on':3} {'present'}")
for pkg in data["packages"]:
    cmd = os.path.expandvars(pkg.get("check") or "false")
    present = subprocess.call(["bash","-lc", cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0
    print(f"{pkg['id']:28} {pkg.get('group',''):10} {str(pkg.get('enabled')):3} {present}")
PY
