# Contributing

Use Python 3.11–3.13 and a virtual environment. Install with
`python -m pip install -e ".[dev]"`; run `python -m pytest -q` and
`python -m ruff check src tests scripts examples`.

Keep imported evidence and source archives immutable. Algorithm changes belong
in a new version/configuration; they must not replace an old run under its
original label. Add a test for every packet, boundary or reproducibility fix.

Before claiming a scientific improvement, report the exact teacher and packet
hashes, world/recipient seeds, input support, query type, queried labels,
optimizer steps, examples processed, initial-state hashes, and all controls.
State whether the tested worlds, teachers or task families were used during
development. Negative and partial results belong in the evidence record.

Do not label a same-world seed rerun as an independent task-family validation.
Do not equate an oracle label probe with one scalar reward interaction, or
count batch draws as unique observations. Preserve upstream notices and settle
licensing before accepting contributions under a repository-wide license.
