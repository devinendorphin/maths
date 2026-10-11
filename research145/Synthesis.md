# The larger changing-allocation inquiry has started

Experiments 145–147 move beyond the closed storage question and actually retain
optimizer state across allocation updates. A transparent adapter keeps NetworkX
3.4.2's primal network-simplex tree and flow across cost changes. The three routes
are fresh public-API solving, the retained basis, and sparse certificate admission
with retained-basis fallback. Every returned plan or shortage has an exact
concrete-model optimality or cut certificate.

Each accepted directory completed **54 workers and 1,350 observations** on nine
fresh streams: six cost-only and three mixed. The audits cover 225 distinct models,
270 distinct proofs, 540 invalid-certificate controls and 16 adapter controls.
There are 36 independently checked cut observations per directory. Meaningful
fields and raw evidence identities reproduce exactly in a second empty directory.
Separate residual/cut arithmetic and fresh reference graph encoding agree with
the answers; the optimizer installation remains shared.

The first execution failed audit because an initial in-memory proof record was
mutated after raw serialization. Both rejected 54-worker directories are
preserved completely and excluded. The repaired source was newly frozen, the
record-ownership regression passed, and both accepted campaigns were fully
rerun. [The failure account](Rejected-record-ownership.md) and
[exact mismatch receipt](Rejected-execution.json) make this visible.

Complete fresh-session means include startup, source checks, graph work, proof
completion/admission, hashing, logging and results. Each mean has two samples.

| Network / stream | Route | Primary / replica mean wall, ms |
|---|---|---:|
| 256 nodes, 512 edges / costs | cold | 419.2 / 387.4 |
| same | retained basis | 314.3 / 306.0 |
| same | guard + retained basis | 206.1 / 186.6 |
| 256 nodes, 16,384 edges / costs | cold | 6,837.7 / 6,378.2 |
| same | retained basis | 5,141.2 / 4,996.4 |
| same | guard + retained basis | 1,794.2 / 1,688.1 |
| 128 nodes, 256 edges / mixed | cold | 272.8 / 257.4 |
| same | retained basis | 255.0 / 237.5 |
| same | guard + retained basis | 204.5 / 196.8 |

On the largest cost-only case the retained basis reduced complete time by
22–25% against cold solving. Adding certificate admission reduced it by about
74% against cold. These savings combine avoided solving, proof completion,
admission and full-proof logging; they are not solver-kernel timings. Full
wall ranges, CPU, peak RSS, pivot counts and evidence bytes for every cell are
in Summary.json. Pivot counts measure only the adapter. The cold route's recorded
zero is a sentinel for **not instrumented**, not a measured absence of pivots.
Smaller and mixed cases have narrower margins.

The cost-only state reuse is real: arrays/tree survive updates, cost changes
reach the solver even when certificate admission succeeds, and the next failed
residual test resumes that same primal basis. Tree-potential recomputation and
all fallback work are charged. Retained and cold routes may choose different
tie-equivalent plans; their status and exact objective agree.

The mixed streams expose the current boundary. Reduced capacity and increased
balanced needs invalidate the fixed basis and trigger explicit resets. Removing
all outgoing capacity of one positive-supply node produces a checked shortage
cut; a further cost update remains infeasible. Restoring capacity returns to a
checked feasible optimum. There is no warm capacity/balance maintenance claim.

This is a first result in the larger research program, not a general changing-
allocation solution or a state-of-the-art comparison. It uses synthetic
transportation networks and an adapted private Python implementation. It makes
no fairness, stakeholder consent, deployment or novelty-priority claim. Known
prior algorithms and the upstream BSD license are credited in [the protocol](Protocol.md).

The next larger work is [checked maintenance across changing needs](Roadmap.md):
extend state reuse beyond costs, compare against a specialist implementation on
broader families, and connect exact shortages/service constraints to explicit
human policy inputs. The storage subquestion is closed; this larger inquiry is
now underway with executed, replicated evidence.
