# Replay and reproduce experiments 141–144

The complete archive is archives/experiments-141-144-recovery.tar.xz. Its receipt
and every-member manifest are Archive-storage.json and Archive-manifest.json.
It retains both full directories: frozen source/inputs, raw historical logs,
active recovery files, all worker/session records, controls and audits. Reports
and delivery scripts are also retained. The external virtualenv and bytecode
are excluded; exact environment/module identities and inherited optimizer source
are recorded. No failed headline storage worker occurred.

Verify custody and replay every mathematical observation with standard Python:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 research141/code/verify_publication.py
```

Extract into a new destination without replacing preserved evidence:

```sh
mkdir /tmp/allocation-recovery-evidence
tar -xJf archives/experiments-141-144-recovery.tar.xz -C /tmp/allocation-recovery-evidence
```

For a new measurement, copy the frozen files listed in primary/Freeze.json and
Freeze.json itself into another empty root; do not copy outputs or summaries.
Use Python 3.12.14 and NetworkX 3.4.2, checking the installed optimizer SHA against
the freeze. Run code/campaign.py, then code/audit.py with that interpreter.
Repeat in a second empty root. Summarize with code/summarize.py using those two
paths. It requires exact equality of meaningful output identities and preserves
both resource sets. New measurements need not equal the recorded timing values.

Inputs.json is supplied, not regenerated or retuned from held-out timings. The
separate development receipt is explicitly excluded from headline counts. The
upstream code and license retained with research145 apply to the same pinned
optimizer; research137 also preserves its source. Source freezes and historical
archives of all preceding experiments are unchanged.
