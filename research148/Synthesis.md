# Capacity, need and floor changes: executed bounded continuation, 148–151

The larger changing-allocation inquiry now has an executed fixed-topology
capacity/need/lower-bound interface. Valid model updates commit atomically;
retained primal flows are repaired, reoptimized and checked, or accompanied by
a concrete shortage cut. This advances beyond the previous noncost reset
boundary. It does not maintain the network-simplex tree, replace a specialist
incremental optimizer or establish a general performance advantage.

Both independent directories completed 48 isolated workers and 1,200 certified
observations: six fresh mixed streams, four routes, two repetitions and 25
queries per session. Each audit checked 150 distinct models and 239 distinct
proofs, rejected 478 invalid-certificate controls and passed 30 transaction,
ownership, shortage/recovery and forced-fallback controls. All model, proof,
action, counter, control and raw-journal identities reproduce exactly. Timing
and process memory are measured separately and are not claimed identical.
The disjoint development set adds 600 mixed-stream observations and 192 route
observations on 48 exhaustively enumerated tiny models; those are excluded from
headline comparisons. No worker failed or reached its declared guard; a separate
control deliberately exercises charged cold fallback.

The audit recorded 40 upper-bound changes below a route's preceding flow and
44 lower-bound increases above it in each directory. There were 240 cut
observations and 48 transitions back from cuts to checked optima. Transport
streams became infeasible when balanced need increases exceeded a local incoming
cut, before the deliberately extreme shortage. Their cuts persist through steps
11–18 and capacity expansion restores feasibility at 19. Cyclic streams have
cuts at 15–16 and recover when needs restore at 17. These are actual infeasible
model states, rather than solver failures discarded from the comparison.

The measured complete sessions below are medians of two fresh processes, in
milliseconds. The native route rebuilds OR-Tools SimpleMinCostFlow per query.
All routes pay the same solver-module imports and frozen-source/native hashing,
transaction copies, solving/admission, flushed full journals and final output.

| Run / network | Nodes / arcs | NetworkX cold | OR-Tools cold | Flow repair | Guard + repair |
|---|---:|---:|---:|---:|---:|
| Primary transport | 16 / 24 | 209.9 | 207.1 | 199.1 | 196.7 |
| Replica transport | 16 / 24 | 209.7 | 212.1 | 211.8 | 201.6 |
| Primary transport | 32 / 48 | 212.2 | 212.9 | 202.1 | 212.7 |
| Replica transport | 32 / 48 | 232.3 | 209.2 | 222.2 | 236.3 |
| Primary transport | 64 / 96 | 250.2 | 227.7 | 225.2 | 232.8 |
| Replica transport | 64 / 96 | 256.4 | 229.7 | 237.6 | 238.1 |
| Primary cyclic | 16 / 96 | 255.9 | 214.6 | 224.9 | 232.2 |
| Replica cyclic | 16 / 96 | 232.4 | 209.6 | 212.5 | 214.9 |
| Primary cyclic | 32 / 192 | 274.6 | 242.8 | 278.2 | 265.6 |
| Replica cyclic | 32 / 192 | 267.9 | 242.3 | 254.9 | 267.8 |
| Primary cyclic | 64 / 384 | 418.9 | 293.9 | 466.1 | 510.0 |
| Replica cyclic | 64 / 384 | 400.4 | 290.7 | 451.2 | 485.0 |

On the largest cyclic case, native cold uses about 35–37% less complete time
than unguarded repair, and about 40–42% less than guarded repair. The sum of
timed query calls there is 102.0/97.9 ms for native cold versus 268.3/258.8 ms
for repair and 288.0/280.2 ms for guard + repair. These query-only figures exclude
startup, source hashing and journal/output serialization. Full certificate
completion remains included inside the query calls.

Repair's query-only sums beat NetworkX cold on the transport cases, but complete
small-session differences vary across replicas and native cold is competitive.
The full guard admits 64 of its 300 queries per directory, yet adds query time
in all six cells relative to unguarded repair. This stage therefore supports
correctness and an explicit update contract, not a recommendation that retaining
this flow algorithm is generally faster. Two repetitions and finite synthetic
inputs do not support significance or production claims.

Sources are credited in [Sources.md](Sources.md). The specialist cold comparison
is real, with pinned native binary hashes, but its Python interface does not
preserve optimizer state. The source-supported C++ incremental comparison and
retained dual/tree repair remain open in the [roadmap](Roadmap.md). Source
inspection of GenericMinCostFlow's SetNodeSupply is particularly relevant: it
sets node excess directly, so changing absolute supplies after a retained solve
requires an inspected adaptation rather than blindly replaying the cold setter.

No real group's allocation, consent, policy choice, fairness or deployment is
represented by these synthetic models. Earlier research evidence and archives
remain immutable; the navigation-only checksum amendment has preserved receipts.
The [complete archive and recovery instructions](REPRODUCE.md) provide both runs,
full proofs/journals, sources, controls and measurements.
