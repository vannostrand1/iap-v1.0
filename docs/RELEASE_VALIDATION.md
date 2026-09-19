# IAP v1.0 — release validation

Validation date: **19 September 2026**. Scope: Linux CPU execution in the release
build runtime. This report separates software checks, historical arithmetic,
numerical replay, and independent scientific confirmation.

## Runtime

Python 3.13.5; NumPy 2.3.5; SciPy 1.17.0; PyTorch 2.10.0+cpu; pytest 9.0.2.
Experiment commands explicitly use one Torch thread. No Doom engine, external
API, Codex session, or remote GPU was used. Dependencies were already installed.
See `validation/doctor.json` for the machine-readable runtime without personal
machine identifiers.

## Executed checks

| Check | Result | Evidence |
|---|---|---|
| Automated tests | 49 passed | `validation/pytest.xml`, `validation/pytest.log` |
| Packaged resources | 13/13 hashes valid | `validation/doctor.json` |
| Historical archives | 13/13 hashes valid | `validation/evidence_audit.json` |
| E/F historical summary arithmetic | 32/32 checks passed | `validation/evidence_audit.json` |
| Historical Gate 2F numerical replay | All 36 condition runs completed | `validation/gate2f_numeric_replay/` |
| Matched-init smoke | Six condition runs completed; not a performance gate | `validation/matched_smoke/` |
| Native recipient round trips | Reloaded logits exactly matched before save in the runner | Per-trial `completion.json` and checkpoints |
| Custom recipient example | Executed | `validation/custom_recipient.log` |
| Fresh MLP teacher + distillation smoke | 100% task accuracy and packet agreement | `validation/teacher_rebuild_smoke/report.json` |
| Python byte compilation | Passed for package, tests, scripts, examples | Build execution |

Historical arithmetic recomputes aggregate means and paired mean differences.
It does not independently recreate every historical confidence interval. A test
suite passing is not a scientific gate passing.

## Numerical replay, not fresh confirmation

The replay used `configs/gate2f_historical.json`, the same teacher assets/world
seeds as the archive, and the original condition-specific initialization and
sampling offsets. Each direction contains six worlds and three conditions.

| Direction / condition | New action % | Archived action % | New sequence % | Archived sequence % |
|---|---:|---:|---:|---:|
| Fly→Transformer / culture | 100.0000 | 100.0000 | 100.0000 | 100.0000 |
| Fly→Transformer / queries only | 56.9444 | 57.2917 | 4.1667 | 4.1667 |
| Fly→Transformer / ungrounded | 23.9583 | 24.6528 | 0.0000 | 0.0000 |
| Transformer→Fly / culture | 99.6528 | 99.6528 | 97.9167 | 97.9167 |
| Transformer→Fly / queries only | 62.8472 | 62.8472 | 2.0833 | 2.0833 |
| Transformer→Fly / ungrounded | 21.1806 | 21.1806 | 0.0000 | 0.0000 |

All 12 cultured-recipient final action/sequence outcomes match. Across all 36
condition runs, **33 action scores and all 36 sequence scores match**. The three
nonmatching action scores are Transformer controls, each differing by exactly
one of 48 primitive decisions. Their raw differences are preserved in
`validation/replay_comparison.csv` and `.json`.

For Fly→Transformer world 3, the **unchanged archived source** was also executed.
It returned the same new scores as the v1.0 port for all three conditions,
including its two discrepant controls. This supports runtime-dependent numerical
variation rather than a port-only effect for that checked world. It does not
establish the exact numerical cause or check the other discrepant world.
See `validation/original_source_f2t_rep3.csv`.

The replay was interrupted by the execution environment's per-call time limit
and resumed using complete-trial hashes. All 36 trials finished; interrupted
partial trials were restarted. This validates trial-level continuation, not
optimizer-step continuation.

## MLP rebuild smoke

The command `iap train-teacher --kind mlp --decisions 1024 --packet-updates 512`
trained a fresh MLP from chosen-action rewards on the canonical finite task,
then built a new surrogate packet. That single rebuild reached 100% teacher task
accuracy and 100% quantized-packet teacher agreement. It validates the rebuild
path; it is not a multi-seed teacher-training study or a new transfer result.

## Checks not claimed

- Windows execution and the remote GitHub Actions matrix were **not run** here.
- The `build` frontend and Ruff were unavailable; a dependency-install attempt
  failed because network name resolution was unavailable. Wheel/sdist building
  uses the installed setuptools backend instead. The workflow includes these
  tools for later CI, but lint and remote-CI success are not asserted.
- Fresh confirmation, independent teacher seeds, new task families, timing
  comparisons, bandwidth-matched lookup-table baselines, and real reward-only
  calibration have not been completed by this release build.
- Full historical Gates 0–2E were not all retrained. Their artifacts are preserved,
  hash-checked, and distinguished from this release's measured reruns.
- No public repository, license grant, DOI, paper submission, or package-index
  publication was performed.

## Installation and distribution

Editable installation is tested with the installed build backend. Wheel and source-distribution builds both passed. An isolated-target wheel
installation passed import, all asset hashes, packet export, a six-condition
engineering smoke, and native checkpoint evaluation. Its dependencies were
shared with the measured runtime; this was not a second independent environment.
See `validation/distribution_checks.json` and `validation/wheel_check.log`. The full repository ZIP includes
history, raw evidence, tests and validation. The wheel contains the runnable
package, small assets and license/provenance notices, not the complete archive.

`RELEASE_MANIFEST.json` lists repository payload hashes. `scripts/verify_release.py`
checks them without third-party packages. Checksums detect modification; an
unsigned checksum manifest is not proof of authorship or trusted provenance.
