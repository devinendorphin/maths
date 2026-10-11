# Frozen specialist incremental comparison, 152–155

152 implements and validates a thin adapter to credited, unmodified OR-Tools
9.14 GenericMinCostFlow. 153 freezes and executes matched longer mixed sessions.
154 independently audits and replicates mathematical and native-state evidence.
155 determines the next boundary. No new minimum-cost-flow algorithm is claimed.

Fixed topology, integer lower/upper bounds, costs and balances use the existing
exact checker domain, restricted here to absolute node supplies at most 1,000,000
so the native bridge has explicitly bounded integer arithmetic. At most 256
nodes and 16,384 arcs, bounds 0..10,000 and costs of absolute value <=1,000,000
fit signed 64-bit aggregate arithmetic in this domain. Updates use the unchanged
148 transaction interface. Complete authentic packets remain a caller assumption.

Six fresh streams have transport/cyclic families, each at 32/64/128 nodes, with
48 changes: two complete cycles of costs, capacity reductions/increases, balanced
need increases, lower-bound changes, forced shortages and restoration. Cyclic
networks contain reverse, parallel and self-loop arcs. Six routes run twice per
stream in fresh sequential processes: 72 workers, 3,528 observations per directory.
The held-out seeds and routes are fixed after disjoint development passes.

Routes are SDK SimpleMinCostFlow cold, Generic cold, Generic warm, full certificate
guard with Generic warm fallback, inherited primal repair and guarded primal
repair. Simple and Generic use the same downloaded C++ SDK/shared libraries,
not a Python wheel with a different binary. Cold Generic and warm Generic use
the identical adapter/preflight, isolating construction and retained state.
Every route pays ctypes/NetworkX module startup and identical frozen/native hash
checks. Importing both is deliberate for this matched accounting contract.

Generic retains its graph, optimizer object and transformed residual flow y.
Each update scans all arcs; SetArcCapacity clips y to new (upper-lower), and
SetArcUnitCost sets current costs. Physical hint x is new lower + retained y,
not necessarily the old admitted physical plan. Recompute remaining node excess
as new supply minus current physical outflow plus inflow, then SetNodeSupply
with that excess. Snapshot actual Flow/Supply before patch, after patch and
after Solve, with counters and an internal graph/optimizer pointer-stability
check. Absolute pointer values are never logged. Solve resets potentials
upstream; this is residual/primal state reuse, not retained-price or tree reuse.

The source's internal feasibility check rebuilds a forward-capacity max-flow
from initial excess, which is not the residual repair problem after a warm
update. Therefore it is disabled only behind an external preflight. Before
every Generic Solve, exact residual max-flow produces a feasible physical
witness, checked in Python and again in C++ against all bounds/balances. If
preflight instead produces an admitted shortage cut, do not call Solve; retain
the patched bounded hint for later recovery. Never disable feasibility without
a checked feasible witness. Cuts do not count as failed solves.

The full guard can skip both preflight and Solve when the prior physical flow
and potentials remain an admitted optimum. Its proof can differ from the
patched, unsolved native hint after a lower-bound change; do not represent
that hint as a certified allocation. Every later patch/solve uses its actual
native flow. Failed guards remain charged, and full proof completion uses the
same exact residual potentials/admission for all routes. No sparse-check claim.

Nonoptimal native statuses retain the failed state record, charge cold Simple
fallback, and discard the failed optimizer before rebuilding on the next query.
A simulated nonoptimal-status control tests that fallback/rebuild branch and
is explicitly labelled; it is not an observed native solver failure. Inherited
repair keeps the 10,000 augmentations/1,000 cancellations guards and charged cold
fallback. Each worker has a 90-second wall guard and 2-GiB address-space guard
after module import. Failed workers and outputs remain retained; no silent removal.

Development consists of six disjoint 48-update streams (1,764 observations),
48 exhaustively enumerated tiny models across six routes (288 observations),
30 inherited transaction/ownership controls and 12 additional native-state
controls. They include reverse-flow need decreases, witness rejection, shortage
recovery without reconstruction, false absolute-excess traces, guarded lower
transforms and topology rejection. Repeated bridge compilation must match bytes.

Audit every proof with separate balance/cost/residual/cut arithmetic and compare
distinct model outcomes with NetworkX network simplex and SDK Simple cold.
Replay actual native-state arithmetic independently: capacity-clipped y,
remaining imbalance, object/construction/solve counts, feasible preflight witness,
post-solve physical flow or explicitly unsolved hint. Wrong-context and false
cost/empty-cut controls are applied to every distinct certificate. A new directory
must reproduce inputs, freeze, controls, full journal bytes and logical evidence.

Headline timing is the median of two complete process sessions. It includes
startup, hash checks, transaction and ctypes copies, full feasibility preflight,
native patch/optimization, guards, proof completion/admission, flushed full
journals and final output. Also report query-only sums and instrumented phases
separately. Repair optimization includes its internal potential work; its phase
is not directly comparable with native kernel time. Phase sums need not equal
complete query time due other Python bookkeeping and copies. Timing/RSS are not
required to replicate exactly. Flush is not fsync. Finite synthetic results with
two repetitions cannot establish significance, general speed, policy validity,
fairness, consent, power-loss safety, novelty or deployment readiness.
