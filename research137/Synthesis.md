# Sparse admission saves measured time, but full snapshots cost storage

Experiments 137–140 implement the cost-delta path left conditional in 133–136.
Every accepted noncompacting update checks only its declared changed edges.
Every failed proof check, cold solve, full snapshot and terminal recovery is
charged. The original allocation pipeline and its domain limits are preserved;
this continuation has its own larger, explicit schema and source/input freeze.

Each of the two accepted directories completed **78 workers and 1,950 headline
observations** on six held-out synthetic base networks. Across the cost streams
there are 150 distinct model/observation encodings and 175 distinct headline
certificate identities. All 887 invalid-certificate controls, twelve transaction
controls and ten recovery controls pass in each directory. Three designed
capacity/balance/shortage certificates are additional. Every mathematical,
flow/potential/proof, raw-log/checkpoint, decision, byte and control identity
matches the fresh-directory replica. No worker hit its frozen limit.

The table gives median complete fresh-process session wall milliseconds for
25 observations, primary / replica. Each cell summarizes three repetitions;
those repetitions do not increase the number of mathematical base models.

| Nodes / edges | Cold solve + proof | Full recheck + fallback | Buffered delta + fallback | Fsync delta + fallback |
|---|---:|---:|---:|---:|
| 16 / 32 | 201.5 / 183.9 | 174.9 / 178.6 | 179.2 / 185.7 | 212.7 / 185.4 |
| 48 / 96 | 223.7 / 207.1 | 207.6 / 194.4 | 206.3 / 190.8 | 196.7 / 188.8 |
| 128 / 256 | 307.4 / 296.9 | 263.6 / 245.2 | 206.2 / 211.3 | 227.9 / 229.6 |
| 16 / 64 | 232.3 / 192.0 | 197.3 / 186.1 | 207.2 / 180.7 | 208.2 / 184.1 |
| 48 / 576 | 374.0 / 382.7 | 315.3 / 294.1 | 307.7 / 258.8 | 258.0 / 301.0 |
| 128 / 4096 | 1321.4 / 1283.4 | 1010.5 / 903.2 | 815.3 / 813.1 | 786.8 / 836.5 |

On the 4,096-edge case the buffered delta route used 815.2 / 813.1 ms versus
1,321.4 / 1,283.4 ms for cold solving: about **38% / 37% less** complete session
wall time. Against full certificate rechecking (1,010.5 / 903.2 ms), the reduction
was about **19% / 10%**. Kernel CPU also decreased. These complete process totals
include startup, solver import, proof completion, failed probes, journal writes,
full terminal export/recovery and result reporting. Online update-phase timing
is retained separately and is not presented as the whole-session cost.

The larger sparse case also improved in both directories. Small cases remain
mixed and are dominated by roughly 0.18–0.21 second fresh interpreter/import
costs. Measurements vary between runs, particularly on the 576-edge case and
fsync route. Three ordered repetitions per cell, on one machine and filesystem,
do not establish significance, a general crossover or a universal solver ranking.
The fsync label records actual file/directory requests, not tested power-loss
resilience. All routes use the same pinned NetworkX optimizer when solving;
the full residual checker and independently encoded reference audit complement
that shared optimizer rather than constitute two different optimizing algorithms.

The persistent route allows an admitted plan handle and changed cost/value
records. An application requiring a whole allocation or stateless proof every
observation still pays its linear export cost. The savings depend on that stated
output and trusted complete-delta contract; finding omissions in arbitrary raw
models cannot be done by looking at only the supplied changed edges.

There is a storage cost. On the largest model the full-recheck route wrote
361,897 journal bytes; buffered delta wrote **757,586**. After a failed sparse
check it logs the entire model and proof in a fresh recovery snapshot. Its final
checkpoint/replay is also charged. The primary 4 KiB live replay budget did not
bind before those recertifications reset it. Six separate 64-byte controls forced
all 115 accepted patches to compact and independently replayed them successfully.
That budget covers serialized live delta records, not the base, Python heap or
historical disk evidence. No general memory reduction is established.

Across all delta sessions including the binding controls, 805 patches accepted
and 203 failed then recertified; the full-recheck route adds 87 fallback records.
A residual sign failure proves only that the captured potential no longer applies.
It does not prove the plan is wrong or the model infeasible. Separate capacity and
balance examples receive fresh valid optimality certificates; the designed
shortage example receives a genuine checked cut.

Replay rejects edited values, deleted/reordered events, wrong context, false
terminal values, truncated bytes and rollback when a trusted terminal anchor is
provided. A deliberately valid earlier prefix is accepted without that anchor,
showing the boundary. A deliberately omitted real update cannot be inferred from
the owned state; rebinding the old plan to the authoritative changed model then
fails full checking. These limitations are recorded controls, not hidden success
claims. Python state/admission code remains unformalized and in-process trust
is part of the contract.

One earlier complete worker execution failed custody inspection: four saved raw
journals disagreed with their byte counters. It is preserved under rejected-custody/
and is excluded from all findings, timings and replication counts. Both accepted
runs were executed in fresh directories and every retained journal was replayed
against the original inputs. The complete archive includes the rejected bytes,
source/input freeze, both accepted runs and both resource measurement sets.

This is an inspectable implementation and finite deployment comparison of
established sensitivity, flow certification and checkpoint mechanisms. It makes
no new theorem, first-in-literature, cryptographic, fairness or practical service
claim. [Alignment.md](Alignment.md) and [Mathematical-contract.md](Mathematical-contract.md)
state exactly what was completed and what assumptions carry the result.

The next roadmap step is to reduce full-snapshot storage: reconstruct from an
immutable admitted base plus validated cost events and separately certified plan
changes, while charging final export, restart and any trusted-anchor storage.
Freeze byte budgets and restart cadence before evaluation. Then compare with an
actual incremental flow solver; cold NetworkX alone cannot settle that question.
Authenticated/complete source adapters, larger non-cost change streams and
stakeholder-defined service policies are separate future work.
