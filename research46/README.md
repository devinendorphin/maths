# Experiments 46–50

Start with the [roadmap](Roadmap.md) and, after completion, [findings](Synthesis.md).
These are five finite follow-ups to [41–45](../research41/Synthesis.md).

The frozen plan has 110 distinct input records, including eight matched
item/seed groups in experiment 46. It has 444 headline policy paths, 216
development timing paths and 360 held timing paths. All gates and renewal
thresholds are chosen on development inputs before any held computation.

From the repository root, with Python 3 and no third-party dependencies:

```sh
python3 research46/code/campaign.py run
python3 research46/tools/verify_compact.py
```

Sources, inputs, protocol and roadmap are sealed in `Freeze.json`. The exact
unchanged stage-35 kernels already present in this compact repository are
verified by SHA-256 before execution. No older large archive is needed to
run these new experiments. Optional `MATHS_BASELINE` selects an exact copy
of those kernels; `MATHS_RESEARCH_ROOT` selects an output root with its freeze.

`Selection-47.json` and `Selection-48.json` preserve the development choices,
candidate timings and hashes of their training records. `Path-results.json`
holds compact records; zero counters are omitted. `Audit-summary.json` and
`Summary.json` report counts and derived comparisons.

Detailed construction proofs, scalar proofs, repair events, accounting and
worker audits are content-addressed compressed objects in the Drive archive
linked from `Archive-storage.json`. Git ignores generated evidence, run logs
and archive files. Completed verified workers can be reused; an interrupted
worker restarts cold from its input. No within-action continuation is claimed.

The independent auditor checks every integer-time answer with a separate
capacity DP. It also checks complete and capped proof construction, native
store disposal, covers, prices, repairs, horizons, input gates and decisions
to stop renewal. Those audit-only answers cannot guide the policy.

A renewal threshold checks the construction work already paid before the
next rebuild. It is **not a guaranteed total-cost bound**: an allowed build
can exceed it. Capped constructions never become active certificates, and
their work and subsequent fallback are charged to CPU.

After restoring an archive, verify its complete member manifest:

```sh
python3 research46/tools/verify_archive.py /path/to/Temporal-proof-experiments-46-50.tar.xz --sha256 HASH_FROM_RECEIPT
```

To inspect a detailed worker:

```python
import sys
sys.path.insert(0, 'research46/code')
from storage import hydrate
from common import read
worker = hydrate(read('research46/evidence/workers/WORKER_NAME.json.gz'))
```
