"""Machine-readable reports and explicitly paired, conditional bootstrap estimates."""
from __future__ import annotations
import csv
import hashlib
import json
from pathlib import Path
from collections import defaultdict
import numpy as np


def jsonable(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    raise TypeError(type(value).__name__)


def write_json(path: str | Path, value) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    temporary = p.with_suffix(p.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True, default=jsonable, allow_nan=False) + "\n", encoding="utf-8")
    temporary.replace(p)


def read_json(path: str | Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def sha256(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_csv(path: str | Path, rows: list[dict]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with p.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: str | Path) -> list[dict]:
    with Path(path).open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def paired_bootstrap(a, b, *, seed: int = 20260919, resamples: int = 10000) -> dict:
    a, b = np.asarray(a, float), np.asarray(b, float)
    if a.shape != b.shape or a.ndim != 1 or len(a) == 0 or not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError("Paired finite, equally sized nonempty vectors required")
    if resamples < 1:
        raise ValueError("resamples must be positive")
    delta = a - b
    if len(delta) == 1:
        return {"n_pairs": 1, "mean_delta": float(delta.mean()), "ci95_low": None, "ci95_high": None,
                "status": "insufficient replication for interval"}
    rng = np.random.default_rng(seed)
    means = np.empty(resamples)
    for start in range(0, resamples, 1000):
        n = min(1000, resamples - start)
        means[start:start + n] = delta[rng.integers(len(delta), size=(n, len(delta)))].mean(1)
    lo, hi = np.quantile(means, [.025, .975])
    return {"n_pairs": len(delta), "mean_delta": float(delta.mean()), "ci95_low": float(lo), "ci95_high": float(hi),
            "status": "conditional paired bootstrap; worlds/streams, not independent teachers or specimens"}


def summarize_rows(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    groups = defaultdict(list)
    seen = set()
    for row in rows:
        key = row["direction"], int(row["rep"]), row["condition"]
        if key in seen:
            raise ValueError(f"Duplicate run key: {key}")
        seen.add(key)
        groups[row["direction"], row["condition"]].append(row)
    aggregated = []
    for (direction, condition), group in sorted(groups.items()):
        aggregated.append({"direction": direction, "condition": condition, "n": len(group),
                           "action_accuracy": float(np.mean([float(x["action_accuracy"]) for x in group])),
                           "sequence_accuracy": float(np.mean([float(x["sequence_accuracy"]) for x in group])),
                           "perfect_recipients": sum(float(x["action_accuracy"]) == 1 and float(x["sequence_accuracy"]) == 1 for x in group)})
    deltas = []
    for direction in sorted({key[0] for key in groups}):
        culture = {int(r["rep"]): r for r in groups.get((direction, "grounded_culture"), [])}
        if not culture:
            continue
        for d, condition in sorted(groups):
            if d != direction or condition == "grounded_culture":
                continue
            control = {int(r["rep"]): r for r in groups[d, condition]}
            if set(control) != set(culture):
                raise ValueError("Incomplete pairs; refusing silently matched-subset estimates")
            keys = sorted(culture)
            for metric in ("action_accuracy", "sequence_accuracy"):
                result = paired_bootstrap([float(culture[k][metric]) for k in keys], [float(control[k][metric]) for k in keys])
                deltas.append({"direction": d, "comparison": f"grounded_culture-minus-{condition}", "metric": metric, **result})
    return aggregated, deltas


def summarize_run(run_directory: str | Path) -> dict:
    root = Path(run_directory)
    rows = read_csv(root / "results.csv")
    aggregates, deltas = summarize_rows(rows)
    write_csv(root / "aggregate.csv", aggregates)
    write_csv(root / "paired_deltas.csv", deltas)
    return {"rows": len(rows), "aggregates": aggregates, "paired_deltas": deltas}
