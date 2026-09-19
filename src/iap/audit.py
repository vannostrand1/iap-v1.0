"""Recompute archived CSV means/effects. This is not a retraining claim."""
from __future__ import annotations
from collections import defaultdict
from pathlib import Path
import numpy as np
from .reporting import read_csv, read_json, sha256, write_json


def audit_evidence(repository: str | Path) -> dict:
    root = Path(repository)
    sources = read_json(root / "evidence/SOURCES.json")["sources"]
    archive_checks = []
    for source in sources:
        path = root / source["file"]
        valid = path.is_file() and sha256(path) == source["sha256"] and path.stat().st_size == source["bytes"]
        archive_checks.append({"file": source["file"], "sha256_matches": valid})
    checks = []
    for gate in ("2e", "2f"):
        folder = root / f"evidence/gate{gate}/results"
        rows = read_csv(folder / f"gate{gate}_transfer_raw.csv")
        aggs = read_csv(folder / f"gate{gate}_transfer_aggregate.csv")
        keys = [(r["direction"], r["condition"], r["rep"]) for r in rows]
        if len(set(keys)) != len(keys):
            raise ValueError(f"Duplicate historical rows in Gate {gate}")
        raw_metrics = ("final_action", "final_sequence")
        agg_metrics = raw_metrics if gate == "2f" else ("mean_final_action", "mean_final_sequence")
        # Gate 2E raw columns use final_action/final_sequence in the supplied archive.
        if raw_metrics[0] not in rows[0]:
            raw_metrics = ("final_action_acc", "final_sequence_acc")
        for aggregate in aggs:
            group = [r for r in rows if r["direction"] == aggregate["direction"] and r["condition"] == aggregate["condition"]]
            if not group:
                raise ValueError("Aggregate has no matching raw rows")
            for raw_key, agg_key in zip(raw_metrics, agg_metrics):
                computed = float(np.mean([float(r[raw_key]) for r in group]))
                recorded = float(aggregate[agg_key])
                checks.append({"gate": gate, "direction": aggregate["direction"], "condition": aggregate["condition"],
                               "metric": raw_key, "n": len(group), "recorded": recorded, "recomputed": computed,
                               "matches": bool(np.isclose(computed, recorded, atol=1e-12, rtol=0))})
        if gate == "2f":
            paired = read_csv(folder / "gate2f_paired_deltas.csv")
            for row in paired:
                control_name = row["comparison"].split("-minus-", 1)[1]
                good = {r["rep"]: float(r[row["metric"]]) for r in rows if r["direction"] == row["direction"] and r["condition"] == "grounded_culture"}
                bad = {r["rep"]: float(r[row["metric"]]) for r in rows if r["direction"] == row["direction"] and r["condition"] == control_name}
                if set(good) != set(bad):
                    raise ValueError("Missing historical control pairs")
                calculated = float(np.mean([good[k] - bad[k] for k in sorted(good)]))
                checks.append({"gate": gate, "direction": row["direction"], "comparison": row["comparison"],
                               "metric": row["metric"], "recorded": float(row["mean_delta"]), "recomputed": calculated,
                               "matches": bool(np.isclose(calculated, float(row["mean_delta"]), atol=1e-12, rtol=0))})
    passed = all(c["sha256_matches"] for c in archive_checks) and all(c["matches"] for c in checks)
    return {"status": "passed" if passed else "failed", "scope": "archive integrity and raw-to-summary arithmetic, not fresh model training",
            "archives": archive_checks, "numeric_checks": checks,
            "limitations": ["Historical confidence intervals retained, not asserted independently reproduced by this check",
                            "Pairing is by ontology/stream; original control model seeds may differ",
                            "No conclusion about held-out task-family generalization"]}
