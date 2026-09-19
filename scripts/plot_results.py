#!/usr/bin/env python3
"""Plot run means as two separate figures. No uncertainty inferred from one seed."""
import argparse
import csv
from pathlib import Path
import matplotlib.pyplot as plt


def main():
    p = argparse.ArgumentParser()
    p.add_argument("run_directory", type=Path)
    a = p.parse_args()
    with (a.run_directory / "aggregate.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    out = a.run_directory / "plots"
    out.mkdir(exist_ok=True)
    for metric, title in [("action_accuracy", "Action accuracy"), ("sequence_accuracy", "Complete-sequence accuracy")]:
        fig, ax = plt.subplots(figsize=(11, 5.5))
        labels = [r["direction"] + " / " + r["condition"].replace("_", " ") for r in rows]
        ax.bar(range(len(rows)), [100 * float(r[metric]) for r in rows])
        ax.set_xticks(range(len(rows)), labels, rotation=25, ha="right")
        ax.set_ylabel("Percent correct")
        ax.set_ylim(0, 105)
        ax.set_title(title + " — finite-support run means")
        fig.tight_layout()
        fig.savefig(out / f"{metric}.png", dpi=160)
        plt.close(fig)
    print(out)


if __name__ == "__main__":
    main()
