# Recover, inspect and repeat

First run `python3 research133/code/verify_publication.py` from the repository.
Archive-storage.json records the compressed archive bytes/SHA-256; Archive-manifest
records each member's bytes/SHA-256/mode. The verifier checks every member before
any execution. Large dependency environments and downloaded wheels are outside
Git. Archive roots are primary/, replica/ and reports/; complete upstream primary
source snapshots are included in the run roots.

Extract only into a **new directory** outside the checkout. Use Python's
`tarfile.extractall(..., filter='data')` after verification; the verifier also
rejects absolute/traversal paths and non-file members. Do not remove earlier run
directories or overwrite their evidence. The preserved run roots already contain
outputs and cannot be reused as empty campaign destinations.

The measured Python build is in Freeze.json. The shared reference is NetworkX
3.4.2. Its wheel is 1,723,263 bytes, SHA-256
`df5d4365b724cf81b8c6a7312509d0c22386097011ad1abe274afd5e9d3bbc5f`.
Create a venv outside Git if the retained one is unavailable, download that exact
wheel with `pip download --no-deps networkx==3.4.2`, verify the hash, and install
the local wheel with `pip install --no-index --no-deps <wheel>`. Keep TLS and
checksum verification enabled. The official network-simplex source/module hash
is `df6b9eb686568feffb28f3b6389a6eb4fd05a53aec43fa89c67b42f17c4856bd`.
The retained interpreter is `/workspace/maths-toolchains/allocation-venv/bin/python`.

Verify `networkx.__version__`, `sys.version` and the installed
`networkx.algorithms.flow.networksimplex.__file__` hash against Freeze.json before
each new deployment. Exact historical dependency-context identities require the
frozen build; a different deployment needs a new recorded context and must not
claim identical historical hashes. The standard-library checker can inspect the
mathematical certificates without a solver; its implementation is not formalized.

To re-audit retained evidence (these commands write new audit outputs into the
extracted copy, preserving the archive):

```
PYTHONDONTWRITEBYTECODE=1 /workspace/maths-toolchains/allocation-venv/bin/python <extracted>/primary/code/audit.py
PYTHONDONTWRITEBYTECODE=1 /workspace/maths-toolchains/allocation-venv/bin/python <extracted>/primary/code/maintenance_controls.py <extracted>/primary <extracted>/primary/Maintenance-controls.json
```

Expected audit: 232 workers, 2,099 queries, 227 distinct proofs (145 optimal,
82 cuts), 1,488 rejected invalid controls and 25,610 enumerated assignments.
The same applies to replica/. Supplemental output has eight policy-case groups,
one same-flow/new-potential case, and one group covering 64 conditional patches
(25 accepted/39 recaptured), plus stale-version/dependency rejection.

For a new complete execution, create two empty directories and copy the frozen
files named by Freeze.json, Freeze.json itself, the two supplemental sources and
Maintenance-freeze.json into each. Verify their hashes. Copy only sources/config,
**not** existing outputs, Sessions files or audits. Run each new directory's
`code/campaign.py`, then `code/audit.py` and `code/maintenance_controls.py`.
Call `code/replicate.py <new-primary> <new-replica> <report>` and compare the
supplemental Maintenance-controls JSONs for exact equality. Campaign execution
is sequential and takes roughly 12 seconds per directory on the recorded machine;
that is a local observation, not a guarantee. Each worker enforces its 30s/256MiB
limit; incomplete work must remain visible.

The historical replication explicitly excludes only timing/kernel-resource
fields listed in Replication.json. Session CPU includes Python startup and final
reporting; no worker has children. Whole worker maxRSS is measured. Cache bytes
are serialized proof bytes, not object-heap estimates. I/O is buffered without
fsync. Full installation timing was not recorded. Source hashes are checked at
startup; a shared dependency installation is not an independent reinstall.

No services or secrets are required. Use the existing checkout and HTTPS Git
proxy; do not create a worktree unless explicitly requested. Older publication
checks remain `research131/code/verify_publication.py`,
`research121/code/verify_publication.py`, `research111/repairs/code/verify_publication.py`
and `scripts/verify_compact.py`. The original charter and preceding mathematical
evidence remain sealed and unchanged.
