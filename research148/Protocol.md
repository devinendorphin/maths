# Frozen bounded inquiry: changing capacities, needs and floors, 148–151

148 fixes an atomic fixed-topology update contract. 149 repairs a retained primal
flow and recovers exact optimality or a shortage cut. 150 compares that repair on
fresh transportation and directed cyclic multigraph streams with Python network
simplex and native OR-Tools cost scaling. 151 audits, replicates and identifies
the next boundary. These are stages of the larger allocation inquiry, not four
claims of new algorithms.

The model and exact certificate domain is unchanged from 145–147: at most 256
nodes and 16,384 arcs, integer finite lower/upper bounds 0..10,000, integer costs
of absolute value at most 1,000,000, balanced integer supplies and a common
positive denominator. Outflow minus inflow equals supply. The campaign has six
fresh streams: transport and cyclic, each with 16/32/64 nodes and 24 updates.
Cyclic networks include reverse, parallel and self-loop arcs. Each route runs
twice per stream, in an isolated sequential process: 48 workers and 1,200 queries
per directory. A fresh-directory replica must reproduce all non-timing data.

Packets bind context, current version and the complete old-model digest.
They carry old/new values for up to 32 distinct (arc, field) pairs for lower,
upper or cost, and up to 256 distinct node balances. Strict integer types exclude
booleans. A valid final model commits atomically and advances the version even
when infeasible. Invalid messages leave all model/version bytes unchanged.
Graph topology, priorities' meaning, eligibility and denominator changes are
outside this interface. Completeness and authenticity of a supplied packet are
caller assumptions: omitted changes to an external model cannot be detected.

Both cold routes rebuild per query. Both repair routes retain only a previously
certified primal flow, clamp it to the new bounds, augment residual paths to
restore balances and cancel negative residual cycles to regain optimality.
They retain a last feasible flow through shortages only as an untrusted hint.
The guard route first tries complete linear certificate admission with the old
flow/potentials, including balance and newly opened residual-arc signs. This is
not a sparse check. Failed guards and failed warm attempts are charged. At the
10,000 augmentation or 1,000 cancellation limit, a repair route performs a
charged cold NetworkX solve. No basis/tree is maintained across noncost changes.

Every optimal output includes the whole integer flow and potentials; infeasible
outputs include a cut with supply strictly above outgoing upper capacity minus
incoming lower bounds. Every output passes the exact checker. The audit uses
separately written balance/cost/residual/cut arithmetic and compares distinct
model outcomes with both independently constructed cold solver references.
Every distinct proof receives wrong-context and false-cost/empty-cut controls.
Thirty additional controls cover rollback, aliasing, replay, used-capacity
reductions, simultaneous bounds/needs, a new negative residual self-loop,
shortage/recovery and a deliberately forced, charged budget fallback.

The six disjoint development streams and 48 exhaustively enumerated tiny
integer-flow models are excluded from headline comparisons. They must pass
before freezing. No route selection, threshold or stream is changed afterward.

Measure complete process wall/kernel CPU and peak RSS, plus the sum of timed
query calls, separately. Complete time includes startup/imports, source and
native-binary hash checks, reading input, transaction copies, guards, solving,
proof completion/admission, flushed full journals and final output. All routes
import both solver modules to use the same startup contract. Each worker has a
90-second wall and 2-GiB address-space limit; failures are retained and never
silently excluded. Journals use flush, not fsync, with no crash durability claim.
Two repetitions yield descriptive medians, not significance estimates. The
sum of query times excludes startup, source hashing and output serialization;
it cannot be presented as complete session time. No broad speed, novelty,
fairness, application or deployment claim follows from these synthetic cases.

Pinned native OR-Tools SimpleMinCostFlow is explicitly cold; source inspection
shows it clears arc flow and constructs GenericMinCostFlow inside each Solve.
The lower-level Generic interface's incremental facility is not exposed by
this route. A specialist warm-state comparison remains open. All earlier
research freezes, archived evidence and mathematical contracts remain intact.
