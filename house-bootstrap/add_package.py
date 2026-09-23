#!/usr/bin/env python3
"""Add or enable catalog rows. Does not install."""
import argparse, json, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
CATALOG = os.path.join(ROOT, "catalog.json")

def load():
    with open(CATALOG) as f:
        return json.load(f)

def save(data):
    with open(CATALOG, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

def find(data, pid):
    for p in data["packages"]:
        if p["id"] == pid:
            return p
    return None

def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    add = sub.add_parser("add")
    add.add_argument("--id", required=True)
    add.add_argument("--kind", required=True, choices=["brew","pip","git","ollama","hf","script"])
    add.add_argument("--spec", required=True)
    add.add_argument("--reason", required=True)
    add.add_argument("--dest", default="")
    add.add_argument("--branch", default="main")
    add.add_argument("--check", default="")
    add.add_argument("--group", default="future")
    add.add_argument("--enable", action="store_true")
    en = sub.add_parser("enable")
    en.add_argument("id")
    dis = sub.add_parser("disable")
    dis.add_argument("id")
    sub.add_parser("list")
    args = ap.parse_args()
    data = load()
    if args.cmd == "list":
        for p in data["packages"]:
            print(f"{p['id']:28} enabled={p.get('enabled')} kind={p['kind']} {p.get('reason','')}")
        return
    if args.cmd in ("enable", "disable"):
        p = find(data, args.id)
        if not p:
            sys.exit(f"unknown id {args.id}")
        p["enabled"] = args.cmd == "enable"
        save(data)
        print(f"{args.id} enabled={p['enabled']}")
        return
    if find(data, args.id):
        sys.exit(f"id already exists: {args.id}")
    row = {
        "id": args.id,
        "kind": args.kind,
        "spec": args.spec,
        "check": args.check,
        "enabled": bool(args.enable),
        "group": args.group,
        "reason": args.reason,
    }
    if args.dest:
        row["dest"] = args.dest
    if args.kind == "git":
        row["branch"] = args.branch
    data["packages"].append(row)
    save(data)
    print(f"added {args.id} enabled={row['enabled']}")

if __name__ == "__main__":
    main()
