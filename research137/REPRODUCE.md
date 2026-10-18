# Verify and reproduce experiments 137–139

From the repository root:

```
python3 research137/code/verify_publication.py
```

This checks frozen sources/inputs, every archived member, full mathematical
result identity, recorded independent replays, and formal outcomes. It verifies
stored evidence; it does not perform a fresh Lean compilation.

Copy every file listed by research137/Freeze.json, preserving repository-relative
paths, and Freeze.json itself into a NEW repository-shaped directory. Only two
inherited executable files are needed: research133/code/producer.py and checker.py.
From the copied root, using the Python standard library:

```
PYTHONDONTWRITEBYTECODE=1 python3 research137/code/run.py <new-results-directory>
PYTHONDONTWRITEBYTECODE=1 python3 research137/code/replay.py research137/Inputs.json <new-results-directory>/Results.json <new-results-directory>/Replay.json
```

Destinations must be new; scripts refuse to overwrite evidence. Inputs.json is
frozen and the deterministic generator refuses to replace it. Serialized replay
imports only audit.py, never an optimizer/producer. Expected Results.json:
567,235 bytes, SHA-256
`f2373b658182d5287e51b163efa7448a39741fafc75c1af396452165746562f6`.

Install official Lean 4.24.0 outside Git. Lean-setup.json pins its release URL,
archive size/SHA-256 and binary SHA-256. Verify the archive, then extract using
`tar --no-same-owner --zstd -xf ...`. No Mathlib is required. Run:

```
python3 research137/code/formal_check.py <lean-binary> <new-formal-build-directory>
```

The harness compiles Flow.lean, checks Spec.lean, and REQUIRES the two deliberately
false statements in RejectedStatement.lean to fail. Successful proofs cannot
contain sorryAx or compiler warnings. Expected axioms are propext,
Classical.choice and Quot.sound. The harness sets the source checkout root as
Lean's working directory. Reproducible .olean build files are excluded from Git.

This host's getpid() disagrees with numeric /proc PID directories. Only if that
prevents Lean finding its executable, compile the supplied compatibility shim:

```
gcc -shared -fPIC research137/code/proc_path.c -o <outside-repo>/proc_path.so -ldl
python3 research137/code/formal_check.py <lean-binary> <new-formal-build-directory> --preload <outside-repo>/proc_path.so
```

It redirects executable-path readlink calls to /proc/self/exe, leaving the
official Lean binary and proof/kernel logic unchanged. Different compiler builds
may change the shim binary hash; record the resulting deployment context.
Both recorded builds use the same verified software installation.

Before extracting the archive, run the publication verifier, then use Python
`tarfile.extractall(..., filter='data')` into a NEW directory. The verifier rejects
absolute/traversal paths, links, devices, duplicates and unmanifested members.
The archive includes full primary/replica result files, raw formal logs and frozen
sources, but not the Lean distribution. Restoration.md distinguishes recovered
logical outputs from the lost original local Git object and archive.

The general sharp single-edge path theorem remains written mathematics. Lean
covers certificate soundness, complete-delta sign preservation/global optimality,
and the objective-update identity. Preserve that distinction in summaries.
