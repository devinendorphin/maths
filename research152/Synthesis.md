# Specialist incremental state: executed and replicated, 152–155

The larger allocation inquiry now has an actual specialist incremental baseline.
A thin credited C++ adapter retains OR-Tools GenericMinCostFlow's graph,
optimizer and residual flow through cost/capacity/need/lower-bound changes and
shortages. The audit checks literal native states rather than inferring reuse
from repeated calls. Upstream Solve resets prices; no retained-price or
network-simplex-tree claim is made.

Each of two fresh directories completed 72 workers and 3,528 certified
observations: six fresh transport/cyclic networks, six routes, two repetitions,
and 49 observations per session. Each audit matched 294 model outcomes, admitted
627 distinct proofs, rejected 1,254 false-certificate controls and passed 42
transaction/native-state controls. All frozen inputs, proofs, controls, action
counters, actual native snapshots and full raw-journal bytes reproduce exactly.
Timing/RSS are not claimed identical. Disjoint development adds 2,052 excluded
observations, including 48 exhaustively enumerated tiny models. Repeating the
adapter build with the identical command produced identical binary bytes.

There were 1,008 cut observations and 144 recoveries from cuts per directory,
168 upper reductions below the preceding admitted flow and 108 lower increases
above it. No worker failed, no native nonoptimal status occurred, and no repair
budget was reached. The separately labelled simulated-status control exercises
charged native fallback and next-query rebuild; it is not an observed solver
failure. Genuine infeasible states produce checked cuts and skip native Solve.

Both native baselines execute the same pinned official C++ SDK. Generic cold
rebuilds per query; Generic warm/guard retain one graph and optimizer per session,
including shortages. In each directory cold Generic constructs 588 objects;
each warm route constructs 12. Both use identical external feasibility preflight
and exact certificate completion. Unguarded warm makes 420 solves, guarded warm
310: the full guard admits 110 of its 588 queries. The separate guarded repair
route admits 112 more, giving 222 guard admissions across the directory.

Complete-session medians below are milliseconds over two fresh processes. They
include startup, identical source/native hashing, transactional/ctypes copies,
feasibility preflight, optimization, exact proof completion/admission, full state
and proof journals, and final output. This is a synthetic finite comparison.

| Run / family | Nodes / arcs | Simple cold | Generic cold | Generic warm | Guard + Generic | Flow repair | Guard + repair |
|---|---:|---:|---:|---:|---:|---:|---:|
| Primary transport | 32 / 48 | 297.2 | 296.7 | 299.5 | 318.3 | 282.0 | 275.4 |
| Replica transport | 32 / 48 | 275.5 | 306.5 | 295.0 | 308.7 | 255.4 | 280.8 |
| Primary transport | 64 / 96 | 294.1 | 312.7 | 327.9 | 344.2 | 324.4 | 332.4 |
| Replica transport | 64 / 96 | 302.5 | 370.2 | 316.6 | 316.5 | 311.6 | 303.4 |
| Primary transport | 128 / 192 | 396.2 | 463.4 | 451.0 | 481.5 | 483.8 | 462.4 |
| Replica transport | 128 / 192 | 402.2 | 496.1 | 486.3 | 493.7 | 459.9 | 473.7 |
| Primary cyclic | 32 / 192 | 363.8 | 378.4 | 388.3 | 398.2 | 372.4 | 382.8 |
| Replica cyclic | 32 / 192 | 345.0 | 409.3 | 381.2 | 412.0 | 373.3 | 388.3 |
| Primary cyclic | 64 / 384 | 471.6 | 543.5 | 551.7 | 615.0 | 594.0 | 669.9 |
| Replica cyclic | 64 / 384 | 462.3 | 532.4 | 548.7 | 564.0 | 625.9 | 619.8 |
| Primary cyclic | 128 / 768 | 768.6 | 862.1 | 845.0 | 933.3 | 1799.3 | 1659.4 |
| Replica cyclic | 128 / 768 | 732.6 | 812.3 | 819.5 | 971.3 | 1687.1 | 1712.7 |

On the largest cyclic network, Generic warm uses about 51–53% less complete
time than inherited primal cancellation. Cold specialist solving also removes
much of that cost, so that gain cannot be assigned to retained state alone.
Warm versus matched Generic cold is mixed: 845.0 vs 862.1 ms in primary,
819.5 vs 812.3 in replica. Simple cold remains faster at 768.6/732.6 ms. The
finite evidence establishes inspected state reuse and correctness, not a
consistent end-to-end warmth advantage or a general production solver rank.

Query-only sums on that network are 497.6/466.6 ms for Simple cold,
544.8/511.7 for Generic cold, 516.6/503.6 for Generic warm,
599.0/639.2 for guard + Generic and 1525.1/1415.6 for primal repair. They exclude
startup, frozen/native hashing and journal/output serialization. Guard + Generic
uses more query time than unguarded Generic in every cell, despite fewer solves.
Two repetitions cannot support significance estimates for small timing gaps.

The instrumented Generic warm phases total 241.1/236.0 ms of those
516.6/503.6 query sums: native construction/patch/optimization 83.6/80.7,
feasibility production 39.2/38.1, proof completion/admission 118.3/117.2.
The arithmetic remainder is about 275.5/267.6 ms, or 53% of query time.
It contains other Python transaction/digest/copy/snapshot bookkeeping and timer
gaps; it is **not** a separately measured component or all proof time. Repair's
optimizer phase includes its internal potential/cancellation work and cannot
be directly equated to native kernel work. These nonexhaustive phase timers
identify the next accounting question; they do not justify assigning all
remaining cost to a convenient explanation.

Remaining imbalance is recomputed from actual physical native flow after lower
transformation/capacity clipping. A checked feasible witness precedes every
Generic Solve with the internal cold feasibility check disabled. Lower-bound
guard admission can leave an admitted physical plan different from the unsolved
native hint; the audit keeps them explicit and verifies subsequent updates from
the real hint. [The contract](Mathematical-contract.md) and [credited sources](Sources.md)
give those implementation boundaries.

The [next roadmap](Roadmap.md) closes this bounded specialist-comparison question
and targets exhaustive cost attribution before optimizing the bridge or evidence
format. Wider literature priority review, topology changes, retained prices/tree,
authenticated updates and real consenting application work remain open. No
real allocation, policy validation, fairness, consent or deployment is claimed.

The [complete archive](REPRODUCE.md) preserves both runs, raw proofs/state/witness
history and all controls. Prior scientific archives and freezes remain intact;
a separately documented delivery-only navigation fix lets the prior verifier
check its original receipt endpoints from byte-preserved sealed snapshots.
