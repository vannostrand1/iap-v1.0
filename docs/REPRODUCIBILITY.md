# Reproducibility

## Install and verify

Use a virtual environment with Python 3.11–3.13. The release validation runtime
is Linux / Python 3.13.5 with NumPy 2.3.5, SciPy 1.17.0 and CPU PyTorch 2.10.0.
The Windows launcher and GitHub matrix are supplied but were not executed on a
Windows host during this build. No claim of cross-platform bitwise determinism.

```bash
python -m venv .venv
# Activate using your platform's standard activation command.
python -m pip install -e ".[dev]"
python -m iap doctor
python -m pytest -q
python -m iap audit --repository . --output validation/evidence_audit.json
```

`requirements-tested-cpu.txt` pins the measured numerical versions. On Windows,
the included launcher installs CPU Torch from the official CPU wheel index,
then those requirements. A pre-existing project venv can be reused manually;
the launcher uses its own `.venv_iap` and does not alter the Doom environment.

## Run families

```bash
python -m iap run --config configs/smoke.json --output runs/smoke
python -m iap demo --output runs/demo
python -m iap run --config configs/gate2f_historical.json --output runs/historical
python -m iap run --config configs/fresh_confirmation.json --output runs/fresh
```

The smoke is 64 updates per recipient/condition and need not learn perfectly.
The demo uses one world per direction with 512/1,024 updates. Neither is an
independent scientific confirmation. Configuration `purpose` fields state
whether a run is a regression, ablation or prospective replication.

Completed trials resume only with unchanged configuration/source/packet hashes:

```bash
python -m iap run --config configs/gate2f_historical.json --output runs/historical --resume
```

Interrupted partial trials restart from their deterministic seeds. This is
**trial-level resume**, not exact optimizer-step resume. Each completed trial's
files are hash-checked before reuse. Never merge old/new configs into one result.

## Recheck a learned student without culture

```bash
python -m iap evaluate runs/demo/f2t_rep0000/grounded_culture.pt --fixture runs/demo/f2t_rep0000/evaluation_fixture.npz
```

This command accepts no packet argument and reads no teacher checkpoint. The
fixture is evaluator-only truth, not training input. `iap summarize RUN_DIR`
recomputes aggregate means and paired intervals from the run's raw rows.

## Rebuild teacher-side knowledge

```bash
python -m iap distill --teacher transformer --updates 2500 --output runs/redistilled.iapx
python -m iap train-teacher --kind mlp --decisions 4096 --output runs/new_teacher
```

A new teacher need not reproduce a historical checkpoint byte-for-byte. Report
its actual competence before claiming it can teach. A config's `packet_paths`
can map `fly`, `mlp` or `transformer` to an explicit local capsule path (relative
to your working directory). The manifest records these packet hashes and refuses
resume after a packet changes.

## Historical source and arithmetic

`iap audit` validates all archived ZIP bytes and recomputes Gate 2E/2F transfer
means and Gate 2F paired mean deltas. Historical bootstrap intervals are retained,
not asserted independently re-created by that arithmetic check. The active
numerical replay and its comparison live under `validation/`.

No original record is overwritten. Historical and rerun results remain separate.
The source distribution/wheel contain the live package; the full repository ZIP
additionally contains archives, evidence and validation artifacts.
