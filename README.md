# Inter-Agent Protocol — IAP v1.0

**Compact behavioral knowledge, empirical grounding, native recipient learning.**

Research implementation by **Richard Anthony Aragon**. Software version **1.0.0**.

IAP separates a teacher's learned behavior from its native model parameters. A
small policy-surrogate packet, optionally accompanied by a source relational
atlas, is grounded against a recipient's local interface and absorbed into the
recipient's own parameters. The exported recipient runs without the packet.

```text
Teacher learns     Distill + quantize       Bounded grounding        Absorb
Fly / MLP /   -->   policy + optional  -->   local observations  -->  recipient
Transformer        relational atlas        + calibration probes     parameters
                                                                    |
                                                       Remove packet; evaluate
```

This repository studies **finite symbolic Convention Relay tasks**. It is not a
universal agent communication standard, a biological fly-learning result, or an
arbitrary ontology-induction system. The ontology grammar and calibration API
remain explicitly specified. See [method](docs/METHOD.md) and
[limitations](docs/LIMITATIONS.md).

## Start here

The source tree is installable and contains its small graph/checkpoint/packet
assets. It does **not** require Doom, Colab, Codex, a GPU, or API credentials.
Python **3.11–3.13** is the supplied launcher/CI target; the measured release
runtime is **Linux, Python 3.13.5, CPU PyTorch 2.10.0**.

### Windows

**Extract the complete ZIP first.** Open the extracted `iap-v1.0` folder and run:

| Launcher | Purpose |
|---|---|
| `RUN_IAP_SMOKE.bat` | Create an isolated environment, install dependencies, run a small mechanical check, package results. |
| `RUN_IAP_DEMO.bat` | One ontology in each transfer direction with three conditions; not confirmation. |
| `RUN_IAP_TESTS.bat` | Run the automated test suite. |
| `RUN_IAP_CONFIRMATION.bat` | Run the larger prospective, fixed-teacher replication configuration. |

An installed Python 3.11, 3.12 or 3.13 is required. The launcher does not install
system Python or change the previous Doom environment. Internet access is needed
for the first dependency installation. Subsequent runs reuse `.venv_iap`.
Progress and errors are logged; completed runs produce timestamped result ZIPs.
The Windows launchers are supplied but **were not executed on Windows in this
release build**. See [Windows instructions](docs/WINDOWS.md).

### Terminal

Run these commands from the extracted repository root, using a virtual environment:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m iap doctor
python -m pytest -q
python -m iap run --config configs/smoke.json --output runs/smoke
python -m iap demo --output runs/demo
```

The `iap` console command and `python -m iap` are equivalent. The measured CPU
versions are recorded in `requirements-tested-cpu.txt`; see
[reproducibility](docs/REPRODUCIBILITY.md) for pinned installation, resume, and
native checkpoint evaluation.

## Implemented components

| Component | v1.0 implementation |
|---|---|
| Models | FlyWire-derived 256-node rate circuit, tanh MLP, small feature-token Transformer; custom PyTorch recipient API. |
| Distillation | Fresh teacher reward-training command; policy-surrogate fitting, int8 quantization and packet export. |
| Packet codecs | Original 97-byte policy and 241-byte policy/atlas capsule; validated, versioned, checksummed envelope. |
| Grounding | Signed-permutation search; relational chain matching; bounded ontology expansion and two-action macro translation. |
| Calibration | Counted query interface, query transcripts, separate public observations and evaluator-only truth. |
| Absorption | Replay-based local fitting; source packet absent from exported student checkpoint and evaluation. |
| Experiments | Explicit JSON configs, active/passive queries, matched controls, historical replay, trial-level resume. |
| Evidence | Original research archives, extracted raw records, provenance hashes, arithmetic audit and new regression results. |

**97 and 241 bytes describe raw semantic payloads**, not total computation,
calibration cost, or framed transport size. The 97-byte packet contains the
weights of a *new policy surrogate*, not native teacher weights. The atlas carries
source observations and their ordering. See the [byte-level format](docs/PACKET_FORMAT.md).

## Run the evidence ladder

```bash
# Ground a source capsule without training a recipient
python -m iap ground --family ontology --teacher transformer --budget 36 --output runs/ground.csv

# Reproduce the archived Gate 2F setup, including original control seed offsets
python -m iap run --config configs/gate2f_historical.json --output runs/historical

# Same ontology seeds, now with matched recipient initializations (different protocol)
python -m iap run --config configs/gate2f_matched.json --output runs/matched

# New world/recipient seeds; same supplied teachers and task family
python -m iap run --config configs/fresh_confirmation.json --output runs/fresh

# Resume only completed, hash-verified trials under an unchanged configuration
python -m iap run --config configs/fresh_confirmation.json --output runs/fresh --resume
```

Additional configs cover aligned transfer, signed-coordinate permutations,
nonlinear relational interfaces, a 5-D stress condition, and passive grounding.
The fresh confirmation configuration has **not been run** as part of this release.
It does not substitute for testing independent teachers or new task families.

Each run preserves its configuration, source and asset hashes, raw results,
query logs, native recipient checkpoints, evaluator-only fixtures, and
per-condition accounting. Completed output is not silently overwritten.
Intervals are conditional paired-bootstrap estimates over world/stream replicas,
not population claims about biological specimens or independent task families.

## Release validation — measured, not inferred

The build includes an actual numerical regression against archived Gate 2F:
**12 world/direction combinations × 3 conditions = 36 recipient training runs**.
The table below is from the new run, not copied into the program as a target.

| Transfer direction | Condition | Runs | Primitive-action accuracy | Complete-sequence success |
|---|---|---:|---:|---:|
| Fly → Transformer | Grounded culture | 6 | **100.00%** | **100.00%** |
| Fly → Transformer | Same queries, no packet | 6 | 56.94% | 4.17% |
| Fly → Transformer | Packet without grounding | 6 | 23.96% | 0.00% |
| Transformer → Fly | Grounded culture | 6 | **99.65%** | **97.92%** |
| Transformer → Fly | Same queries, no packet | 6 | 62.85% | 2.08% |
| Transformer → Fly | Packet without grounding | 6 | 21.18% | 0.00% |

All 12 cultured-recipient final scores matched the archive. Across all 36
conditions, 33 action scores and all 36 sequence scores matched; three Transformer
control action scores differed by one of 48 decisions. Running the **unchanged
original script** for one discrepant world reproduced the new scores under this
runtime. The discrepancy is retained, not hidden or averaged away.

This is a **numerical replay on historical seeds**, not new independent
confirmation. Original controls were paired by ontology but did not always share
initialization; matched-init configs are separately labeled.

Other checks completed during the build:

- **49 automated tests passed**, including grounding, packet validation, native
  checkpoint reload, fixed-buffer invariants, and resume-integrity checks.
- **13 packaged assets and 13 historical archives** passed their hash checks;
  **32 historical summary arithmetic checks** passed.
- A freshly trained MLP teacher reached 100% on the 24-state convention in a
  1,024-decision smoke rebuild; its newly distilled packet reproduced that policy.

See [release validation](docs/RELEASE_VALIDATION.md),
[raw replay rows](validation/gate2f_numeric_replay/results.csv),
[archive comparison](validation/replay_comparison.csv), and
[original historical evidence](evidence/gate2f/README.md).

## Use the API

```python
import numpy as np
import torch
from iap.resources import teacher_capsule
from iap.tasks import make_world
from iap.grounding import ground_ontology
from iap.models import ModelSpec, make_model, save_student
from iap.absorption import absorb

torch.set_num_threads(1)
capsule = teacher_capsule("fly")
world = make_world("ontology", seed=1300000)
grounded = ground_ontology(capsule, world.public, world.oracle(36), budget=36)
spec = ModelSpec("transformer", inputs=8, actions=4, seed=1300010)
student = make_model(spec)
absorb(student, world.public.observations, grounded.targets,
       np.flatnonzero(grounded.predicted_roles), updates=512, seed=1300101)
save_student(student, spec, "student.pt")  # native student only; no culture packet
```

This API example uses a benchmark oracle that returns a correct primitive action
or `nuisance`. Those are **label-style probes**, not single binary reward bits.
The grounder sees the public world and the query API, not a hidden transform key.
See [API contracts](docs/API.md) and [custom recipient example](examples/custom_recipient.py).

## Repository map

```text
src/iap/          Installable core, grounders, models, CLI and small verified assets
configs/          Historical, matched-init, smoke and prospective experiment configs
tests/            Software and numerical contract tests
examples/         Packet inspection and a custom recipient
scripts/          Windows setup, wheel checks, archive replay, integrity and plots
docs/             Method, API, protocol, limitations and publication guidance
evidence/         Original results/protocols and source provenance
archive/          Byte-preserved research ZIPs, including early gate history
validation/       Checks and actual reruns completed while building v1.0
upstream/         Original provenance records and third-party license notices
.github/          Linux/Windows CI workflow and issue templates
```

The core unifies the Convention Relay implementations of Gates 2C–2F. Earlier
Gate 0/1 methods remain preserved research archives, not misleadingly advertised
as the same end-to-end algorithm. The Doom negative result remains part of the
history; not every earlier gate succeeded. See [history](docs/HISTORY.md) and
[documented API changes](docs/API_CHANGES.md).

## Publication and licensing status

This is a research software release, **not a claim of peer review, established
novelty over all distillation work, or unrestricted communication between arbitrary
agents**. Packet-free evaluation is also a property of ordinary distillation; the
research question here concerns bounded mismatched interfaces and ontologies.

**The repository-wide license is deliberately pending the author's decision.**
Upstream notices and graph provenance are preserved; no broad license was assigned
to somebody else's assets. Review [LICENSE](LICENSE),
[third-party notices](THIRD_PARTY_NOTICES.md), and
[data provenance](docs/DATA_PROVENANCE.md) before public distribution.

`CITATION.cff` describes this software, not a nonexistent paper or DOI. No remote
GitHub repository or package-index release was created. The
[GitHub publishing guide](docs/PUBLISH_TO_GITHUB.md) explains the final local Git
steps, and the [publication checklist](docs/PUBLICATION_CHECKLIST.md) records the
remaining empirical and release decisions.
