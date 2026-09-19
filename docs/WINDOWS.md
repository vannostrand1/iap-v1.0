# Windows: no Colab or Codex required

1. Extract the entire repository ZIP into a writable directory.
2. Double-click `RUN_IAP_SMOKE.bat`.
3. For a complete small demonstration, use `RUN_IAP_DEMO.bat`.

Python 3.11, 3.12 or 3.13 must already be installed. The launcher does not install
Python system-wide. It creates/reuses `.venv_iap`, installs declared CPU packages,
verifies assets, emits progress, and writes a timestamped result directory plus
an upload ZIP. `RUN_IAP_TESTS.bat` runs the software test suite. No ViZDoom,
Numba, WADs, visual-perception dependencies, GPU, API key or external agent is used.

If Windows tries to open a BAT from inside a compressed folder, the launcher
stops with an instruction to extract all files. Do not copy just the BAT file.
The directory must contain `pyproject.toml`, `scripts/`, `src/` and `configs/`.

Setup needs internet access to download dependencies. Experiments themselves
are local and offline. Long numerical regressions are optional; the default
smoke is intentionally small. Failure tracebacks are written to the local setup
log; a failed run is not reported as a successful scientific result.

For manual setup:

```powershell
py -3.12 -m venv .venv_iap
.\.venv_iap\Scripts\python.exe -m pip install -e .
.\.venv_iap\Scripts\python.exe -m iap run --config configs/smoke.json --output runs/manual_smoke
```

The v1 launchers are provided and syntactically reviewed. They were not executed
on a Windows host in this release build. The supplied GitHub Actions workflow
will test Windows when the repository is hosted and CI runs.
