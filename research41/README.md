# Experiments 41–45

Five bounded follow-ups to the regenerated 36–40 campaign. The older, lost
36–40 run is a report-only reference; these are fresh deterministic inputs.

1. **41:** Broader slope ranges, analytic gate bounds, and capped construction.
2. **42:** Choose an indexed construction gate on eight development cases,
   seal it, then evaluate sixteen held cases.
3. **43:** Fixed 32-step rebuild windows versus windows that double in length.
4. **44:** Loss before, at, or after a join, including a deliberately stopped rebuild.
5. **45:** Transfer the selected gate to doubling windows on fresh inputs,
   including normalized controls.

The frozen plan has 105 unique inputs, 72 construction workers, 306 headline
policy paths, 96 development timing paths and 288 held timing paths. These
are small, bounded samples; modeled mathematical time is distinct from CPU.

## Reproduce

From the repository root, with Python 3 and no third-party packages:

```sh
python3 research41/code/campaign.py run
```

`Freeze.json` checks every campaign source, exact input and protocol hash,
and the unchanged stage-35 Python kernels. Existing verified worker files
are reused. An interrupted worker restarts cold from its input; the code
does not claim exact continuation inside an unfinished action.

The independent auditor checks sparse recurrence, deletion witnesses,
index operations, incomplete construction cursors, scalar partitions,
prices, repairs and horizons. A separate capacity dynamic program checks
the selected packing at every integer time. It never supplies choices to
the policy. A stopped frontier is retained as evidence and never becomes
an active certificate.

## Storage

GitHub holds the sources, frozen inputs, protocol, selection and compact
results. Detailed proofs and audited worker records belong in the Drive
archive linked in `Archive-storage.json` after completion.

Proof objects are stored once by content hash. Optional checkpoints contain
only current state and counts, rather than copies of the growing history.
Algorithm CPU excludes serialization and independent audit work. Every
native solve is cold, and its temporary store must be empty after disposal.

To inspect a worker after restoring the evidence archive:

```python
import sys
sys.path.insert(0, 'research41/code')
from campaign import hydrate
from common import read
worker = hydrate(read('research41/evidence/workers/WORKER_NAME.json.gz'))
```

The archive includes its own manifest. Recovery verification checks both
the downloaded archive hash and each archive member's bytes.
