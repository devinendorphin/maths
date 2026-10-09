# Recover and reproduce experiments 101–110

The compact checkout contains readable reports and own source. Full raw results and proof evidence live in `archives/experiments-101-110-original-300-workers.tar.xz`. Obtain it at the commit carrying this report, check the byte length and SHA-256 in `Archive-storage.json`, extract into an empty directory, then check all entries in `research101/Archive-members.json`. The manifest itself is covered by the outer archive hash. Outer storage/remote-verification receipts are sidecars, not self-referential archive members.

The archive contains all frozen campaign files, the small CP executable and adapted source, native VIPR binary/source, proof/formula/input files, compact witnesses and full original/replication result records. It excludes Python caches, duplicate `Results-progress.json` and the large external SDK installations. Thus it is complete experiment evidence, not a fully offline execution environment.

For a same-environment replay, keep Python 3.12, NumPy, the recorded GNU C++/GMP runtime, PySCIPOpt deployment and pinned official VeriPB v2 deployment available at the paths in `Dependency-setup.json`, `VeriPB2-source.json` and `External-dependencies.json`. The latter hashes 107 runtime files. The campaign fails if their identities differ. See `Environment.json` for observed platform/package details. The existing environment also has the large Lean SDK, but this batch does not invoke it.

For a fresh directory, copy exactly the files named in `Freeze.json`, that manifest and `code/audit.py` into an empty directory. Do not copy existing results or evidence. Then run:

```sh
python3 code/campaign.py
python3 code/audit.py
```

The campaign produces 300 worker records; the audit independently enumerates small models, rechecks distinct VIPR/VeriPB proofs and rejects false-bound controls. To audit retained evidence alone, execute `python3 code/audit.py` from a restored copy with the recorded external SDK available. The auditor is post-freeze validation code, separately hashed in each audit receipt.

To aggregate an original and fresh run, execute from the original restored root:

```sh
python3 tools/summarize.py /absolute/path/to/fresh/research101
```

This preserves full fresh result records under `replication/`, checks logical equality and writes the timing table. Do not use the original archive directory for rerunning the producer.

## Rebuilding external deployments

Changing installation paths, Python ABI or compiled artifacts constitutes a new deployment. Preserve the original frozen evidence, record the new paths and hashes, and create a new freeze before running; do not silently bypass the existing hash checks. Binary hashes generally change across hosts even when source commits match.

The session setup script `tools/setup_dependencies.py` is tied to `/workspace`, deploys outside Git, pins PySCIPOpt 6.0.0, pybind11 2.13.6 and Cython 0.29.37, and downloads the CP source plus the older VeriPB mirror. The older mirror is development history only. It is insufficient for the format2 headline proofs. NumPy and setuptools are required separately; their observed versions are recorded in `Environment.json`.

Use `VeriPB2-source.json` for the official **version2** source archive, fixed commit, URL, size and SHA-256. Extract it outside the checkout. With that source directory as the working directory and the pinned dependency directory on `PYTHONPATH`, the session attempted `python3 setup.py build_ext --inplace` with a 180-second parent-command timeout, then copied the completed extensions listed in `VeriPB2-recovery.json` from `build/lib.*` into the source package. Remaining `.py` modules were left unchanged. Run `python3 setup.py egg_info` to generate package metadata; the source archive declares starting version 2.3.0. Upstream setup additionally requires `setuptools-git-versioning<2`. Building needs C++17, Python development headers, GMP/GMPXX and zlib headers/libraries. No proof-checking rule patches are needed. `tools/run_veripb.py` propagates the checker exit code, and the campaign also requires explicit success output. A full build or a different recovered extension set is a different timing deployment and must receive its own identity record.

For CP, download the pinned official supplement in `Dependency-setup.json`, check its archive hash, then use `tools/adapt_cp.py` after pointing a new deployment receipt to the source folder. That script makes the disclosed patch and runs `g++ -O2 -std=c++20`. `code/external.py` retains the producer proof and adds explicit auxiliary solution values for the checked proof. Both paths are archived. The tiny included executable is x86-64; source rebuilding must be disclosed if its identity changes.

The PySCIPOpt 6.0.0 wheel contains SCIP 10.0.0 and ordinary solving/reoptimization but no exact-solving support. A separately compiled exact SCIP installation would be a new experiment, rather than a way to retroactively change the capability result. Ordinary solver proposals in this batch are certified by duplicated native exact work.

Build-time caps and failed development prototypes are retained in the corresponding receipts. The completed campaign and independent audits are the accepted results. CPU measurements cover warm per-worker execution and required checker children; deployment, common imports, audit and packaging are outside that statistic.
