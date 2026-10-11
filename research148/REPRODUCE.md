# Recover and audit experiments 148–151

The complete repository archive is
`archives/experiments-148-151-capacity-needs.tar.xz`. Archive-storage.json binds
its SHA256/length/member count and Archive-manifest.json binds each member's
bytes, SHA256 and mode. Publication-seal.json binds the top-level sources,
reports, manifests, workflow and explicitly amended predecessor navigation.
The archive contains complete primary and replica directories, plus reports;
neither journals nor proof history are omitted. Older archives remain unchanged.

Verify a clean checkout using only the Python standard library:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 research148/delivery/verify_publication.py
```

This checks every member, source freeze, worker transcript, transaction replay,
optimal/cut proof, false proof control and primary/replica logical identity. It
does not rerun external solvers or make third-party wheels part of the archive.
The complete producer audit does require the pinned environment below.

To restore accepted runs, verify first, then extract into a fresh directory:

```sh
mkdir restored-148
tar -xJf archives/experiments-148-151-capacity-needs.tar.xz -C restored-148
python3.12 -m venv allocation-148-venv
allocation-148-venv/bin/pip install -r research148/Requirements.txt
OPENBLAS_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 allocation-148-venv/bin/python restored-148/primary/code/audit.py
```

Accepted binary custody uses CPython 3.12.14 on x86_64 Linux, NetworkX 3.4.2
and OR-Tools 9.14.6206, with exact native module/shared-library hashes in the
source freeze. Installing a different platform wheel can fail the exact-byte
environment check even when its arithmetic agrees. A newly declared environment
would be a separate execution, not an exact-binary replica of this one.

For a new run, copy `restored-148/primary` into a fresh execution directory, remove
only that copied directory's outputs, Sessions*.json, Controls.json, Audit.json
and Logical.json, retaining the original freeze and all frozen input/source
bytes. Then run its code/campaign.py and code/audit.py using the pinned Python.
Never delete or overwrite accepted archive evidence to rerun it. Run another
fresh directory for the replica, then use code/summarize.py to compare them.
The frozen campaign executes sequential isolated workers; it retains each failure.

Complete times include fresh process startup and full custody checks. Query
times exclude startup/hash/output work and must remain separately identified.
Journal writes are flushed without fsync and do not certify power-loss recovery.
The delivery package refuses missing/incomplete roots before replacing any
existing archive; package safety controls are recorded separately from headline.

Preserved README/seal snapshots and Navigation-amendment.json document the only
changes to predecessors: current navigation and dependent seal hashes. All
prior scientific freezes, archived proofs, controls and measurements are intact.
