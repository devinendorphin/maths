# Complete evidence and specialist dependencies, 152–155

The complete archive is
`archives/experiments-152-155-specialist-incremental.tar.xz`, with primary,
replica and reports roots. It contains full inputs, worker proofs/journals,
native before/patched/after flow/excess snapshots, feasible preflight witnesses,
timings/resources, controls, source/build receipts and the small compiled adapter.
Manifest/receipt/seal bind all bytes, modes and member counts. The external C++
SDK is reproducible by its official release hash and is not copied into this
archive. No accepted proof or raw journal is replaced by a summary.

Dependency-free verification from a clean checkout:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 research152/delivery/verify_publication.py
```

This checks every archive member and frozen source/adapter hash, replays all
transactions, exact optimal/cut proofs and native-state arithmetic, and compares
complete logical/raw identities. It requires no SDK, native execution or Python
solver package. The CI workflow also verifies all prior published evidence.

To execute the producer audit or a new session, obtain the official SDK:

<https://github.com/google/or-tools/releases/download/v9.14/or-tools_amd64_ubuntu-22.04_cpp_v9.14.6206.tar.gz>

Verify SHA256
`127a82bbbf304d26721bb9b41ecce2d66f21c757204ab5aa2cc37eaa6ffb7eb6`
before extraction. The accepted environment used CPython 3.12.14, NetworkX
3.4.2, Ubuntu 24.04/glibc 2.39 and the pinned Ubuntu 22.04 C++ SDK. Build.json
records g++ 13.3, the adapter build command and library hashes. Freeze.json
records the actual 90 mapped SDK library hashes and the adapter SHA256. The
same SDK serves Simple and Generic; a Python wheel is not interchangeable.

Extract only after verification, install the pinned Python requirement in a
virtual environment, and set MATHS152_SDK to the extracted SDK directory and
LD_LIBRARY_PATH to its lib directory **before** launching Python. The retained
adapter has the original SDK rpath; the loader override permits another directory
with identical pinned library bytes. environment.py normalizes library paths
against MATHS152_SDK and verifies actual mapped modules. Absolute original build
paths in Build.json are provenance, not a requirement to reproduce that directory.
Installing different binary bytes/platform versions requires a separately
declared execution, not an exact-binary replica of the accepted freeze.

Run an extracted accepted primary/code/audit.py with the pinned interpreter to
repeat the complete producer audit. To rerun the campaign, copy an accepted
execution directory to a new location, remove only that copied directory's
outputs, Sessions*.json, Controls.json, Audit.json and Logical.json, retaining
all frozen input/source/build/adapter bytes. Then run its code/campaign.py and
code/audit.py. Run a second fresh directory and compare via code/summarize.py.
Never overwrite or delete accepted archived evidence to make room for a rerun.

Build reproduction uses code/build.py with the SDK variable, but exact source
paths/rpath/compiler configuration can affect the resulting binary hash. This
stage separately checked a repeated build with identical command/paths for
byte equality. Use the preserved compiled adapter for strict frozen execution,
or declare a new build/environment rather than modifying the old freeze.

Timing medians include complete startup, native/source checks, adapters,
feasibility preflight, proof completion/admission and full journals. Query/phase
times exclude other complete-session costs; repair and native phase labels do
not denote the same mathematical work. Flush does not establish fsync durability.
Package controls reject missing/incomplete roots before replacing an archive.

Navigation snapshots preserve all prior seals/README bytes. The 148 delivery
verifier now resolves its original receipt endpoints from sealed snapshots when
navigation advances. Its exact original helper is preserved; the old archive,
scientific source freeze, models/proofs and original receipt are unchanged.
