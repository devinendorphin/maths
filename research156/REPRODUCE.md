# Custody and reproduction

The delivery archive preserves primary and replica headline roots, excluded
development evidence and reports. Every full Worker.json, Evidence.jsonl,
Accounting.json interval ledger, stdout/stderr and parent session is retained.
The source freeze was made after development and before any headline worker.
Inputs and every file under vendor/ are byte-identical to 152; the adapter binary
is unchanged. Old-custody.json binds all 1,256 predecessor files, not just archives.
No ancestor file or root README is modified by this continuation.

The approved 10,171,800-byte archive is published as ordered 512,000-byte
transport pieces (the last piece is shorter) to avoid the stalled large upload.
Archive-parts.json binds every piece and the unchanged whole-archive checksum.
The verifier reads the pieces directly. To reconstruct the original file outside
the checkout, without overwriting an existing file:

```sh
python3 research156/delivery/archive_parts.py /tmp/experiments-156-159-cost-accounting.tar.xz
```

Reconstruction must produce SHA-256
`0c562482902af5968bc5bee2f5f6a2bc2aa31ff8efd2e88511e206788af23e2a`.
Scientific source, all raw evidence, freeze and archive bytes are unchanged.
Current delivery helpers and this transport receipt are sealed separately from
the delivery version already contained inside the approved archive.

rejected/primary-1 and rejected/development-source-1 preserve the initial failed
custody execution and its source/development. Rejected-execution.json identifies
the two incomplete journals. They are hashed as rejected artifacts and excluded
from accepted certificate and timing totals. The accepted recording path and
fresh freeze are described in [the findings](Synthesis.md).

After checkout, dependency-free verification is:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 research156/delivery/verify_publication.py
PYTHONDONTWRITEBYTECODE=1 python3 research152/delivery/verify_publication.py
PYTHONDONTWRITEBYTECODE=1 python3 scripts/verify_compact.py
git diff --exit-code
```

Full scientific reruns require the pinned Python 3.12.14, NetworkX 3.4.2 and
official OR-Tools v9.14.6206 C++ SDK from the preserved Build.json and
[152 build instructions](../research152/REPRODUCE.md). Use the retained exact
bridge.so. For a relocated SDK set MATHS152_SDK to its absolute root and
LD_LIBRARY_PATH to its lib directory; mapped library hashes must still match.
SDK libraries and virtual environments are not archived or uploaded.

For each fresh copy of research156, with no outputs directory:

```sh
PYTHONDONTWRITEBYTECODE=1 /path/to/pinned/python code/campaign.py
PYTHONDONTWRITEBYTECODE=1 /path/to/pinned/python code/audit_accounting.py
```

Do not alter Freeze.json to make a mismatch pass. Moving to other native/Python
versions is a new, explicitly frozen experiment. The standard-library delivery
verifier does not execute the adapter or require the SDK.

For development replay remove only development-outputs and the generated
Development-sessions/Audit/Logical/Accounting-summary files in a fresh copy,
then run campaign.py --development and audit_accounting.py --development.
Development is excluded from headline timings. Clock calibration and adversarial
controls are independently rerunnable with controls_accounting.py.

Accounting.json is written after the worker ledger ends; the enclosing parent
clock includes that output. Parent-minus-ledger time is intentionally an explicit
envelope gap covering receipt serialization, bootstrap, shutdown and scheduling,
rather than an invented self-timing receipt. The archive and manifest, scientific
replication and exact interval closure are separate checks. Neither timestamps nor
native records constitute external hardware attestation.
