# Replay and reproduce experiments 145–147

The complete archive is archives/experiments-145-147-dynamic-allocation.tar.xz.
Archive-storage.json and Archive-manifest.json bind every member, including both
accepted runs and the two rejected record-ownership runs. Accepted roots are
primary and replica; excluded roots are rejected-record-ownership/primary and
rejected-record-ownership/replica. The first primary audit failure is documented
in Rejected-record-ownership.md and Rejected-execution.json. No rejected record
contributes to the accepted counts or Summary.json.

Verify all file identities, replay every accepted concrete certificate and
check preservation of the rejected mismatch with standard Python:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 research145/code/verify_publication.py
```

Extract without overwriting preceding evidence:

```sh
mkdir /tmp/allocation-dynamic-evidence
tar -xJf archives/experiments-145-147-dynamic-allocation.tar.xz -C /tmp/allocation-dynamic-evidence
```

For a new measurement, copy only accepted primary/Freeze.json and its listed
frozen files into an empty root. Use Python 3.12.14 with NetworkX 3.4.2. Check
the installed networksimplex module hash against the freeze; its complete source
and BSD-3-Clause license are supplied. Run code/campaign.py then code/audit.py
using that interpreter, repeat in a second empty root, and run code/summarize.py
with the two root paths. Preserve failures and exact inputs; do not replace the
recorded campaign to obtain nicer measurements.

The measurement audit reexecutes the adapter controls with the pinned dependency
and separately reconstructs residual/cut arithmetic and cold reference graphs.
The standard-library publication verifier replays all certificates and binds
those complete audit/control receipts; it does not rebenchmark NetworkX or
independently reimplement the adapter. General development checks and 75 mixed
pilot observations are excluded from headline counts. Performance samples vary
by environment; objective/certificate/evidence identities should reproduce.

The worker freezes were created before each headline execution. Later reporting,
packaging and publication verifiers are separately covered by the delivery seal.
The optimizer state lives in process memory; this stage does not persist/restart
the retained spanning tree or promise power-loss recovery.
