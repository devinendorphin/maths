# Reproduce experiments 101–110

Use Python 3.12+, Linux x86-64 and GMP/C++ runtime libraries for the inherited VIPR binary. Use an isolated virtual environment outside the repository:

```sh
python3 -m venv /workspace/maths-toolchains/scip-venv
/workspace/maths-toolchains/scip-venv/bin/python -m pip install -r /workspace/maths/research101/requirements.txt
```

Pinned PySCIPOpt 6.0.0 and NumPy 2.5.3 were used. Capabilities.json records SCIP 10.0.0 and the unavailable exact-mode gate. This binary wheel has ordinary solve support only; never describe this batch as exact-mode SCIP. No secrets or external services are needed after installation. No new Lean build is required.

Verify the SHA-256 and byte count of `archives/experiments-101-110-complete.tar.xz` against Archive-storage.json. Extract into a new directory, never over original evidence. Verify all member lengths and SHA-256 values in that receipt. It contains headline/, replication/ and aborted-attempt/ roots; the aborted attempt is not a completed dataset.

For a new campaign, create an empty directory and copy only files listed by headline/Freeze.json plus Freeze.json from headline/. Preserve executable file modes of the VIPR checker. From the fresh directory:

```sh
PYTHONDONTWRITEBYTECODE=1 /workspace/maths-toolchains/scip-venv/bin/python code/campaign.py > Run.log 2>&1
PYTHONDONTWRITEBYTECODE=1 python3 code/audit.py
```

The campaign verifies all frozen hashes and aborts unexpected failures. Require Execution.json complete with 273 workers across 101–110, and Audit.json passed with 1,716 answer checks, 144 invalid DP rejections, 42 valid VIPR checks and 42 weakened-bound rejections. The expected exact-mode error in Run.log is a recorded capability limitation, not a failed required worker. Experiment 107 intentionally records eight resource-cap incompletes and checked fallback completions.

To re-audit retained headline or replication evidence, run code/audit.py in that extracted root; it rewrites Audit.json there. Compare fresh Results.json after removing only top-level `cpu` and `wall` from each worker. All other fields matched the two recorded runs. Timing and duplicate source copies remain in the archive; no sampling of evidence was used.
