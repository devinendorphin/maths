# Frozen scope: allocation roadmap, experiments 133–136

This is a bounded execution of the four stages in the allocation charter at
commit eb1222d70286a4ce13236206558591464e157d4a. Earlier knapsack batches remain
separate. The JavaScript checks during the access failure were preliminary
conversation-only checks, not campaign evidence or timing runs.

133 asks whether an exact general finite-capacity integer min-cost-flow producer
and a separate potential/cut checker agree with NetworkX 3.4.2 network simplex
and independent exhaustive enumeration on tiny fixtures. Include negative costs,
cycles, lower bounds, ties and infeasibility. Reject false costs, flows, capacities,
potentials and infeasibility witnesses; reject unsupported domain/dependency
changes. Enumeration and network simplex do not call the certificate checker.

134 compares six routes: cold cycle cancellation; warm cycle cancellation seeded
with the previous flow; captured-potential recheck with cold fallback; potential
repair with cold fallback; staged recheck/potential/flow repair; and cold NetworkX
plus separately constructed potentials or cut completion. These are explicitly
named implementations, not claims about all warm-start algorithms. Seeded flow
repair and warm solving share the same producer; their different admission paths
are part of the comparison. Four held-out transportation graphs have respectively
4/6/8/10 nodes and 4/9/16/25 edges. Three nine-observation streams per model test
small cost updates, large alternating cost updates, and feasibility changes.
Three fresh worker repetitions per route/stream are timed. Two development graphs
are excluded from headline counts. No trained policy is claimed.

Every route includes input decoding, model validation/binding, failed probes,
fallback, feasibility repair, optimization, potential construction, final checking,
certificate serialization, disk write/read and replay, and bounded cache storage.
Workers have no child processes. External session wall/child CPU and kernel worker
maxRSS include process startup/import and all worker work; per-query phase times
are a decomposition, not a replacement for session totals. Disk operations use
ordinary buffered I/O (not fsync durability). Independent audits and replication
are additional research costs, reported separately from query maintenance.

135 uses synthetic explicitly stated commitments, not stakeholder-approved real
data. Eight two-supplier/three-recipient cases have demands (3,4,5), optional
service floors, eligibility/capacity changes, and costs. A recipient-to-sink lower
bound expresses its floor. Unused supply has a zero-cost route to the sink.
Compare scalar cost minimization with maximizing the minimum served/demand ratio
over integral allocations, then minimizing cost within the best coverage floor.
Try coverage candidates in descending exact rational order; failed probes and
their checked cuts are retained and charged. A scalar cost certificate alone is
not a fairness certificate. Exhaustively enumerate the six supplier/recipient
edge flows to audit max-min coverage and its cost tie-break.

136 establishes a conditional changed-edge checking bound with explicit immutable
admission/trusted-delta assumptions and a one-edge alternating-cost counterexample
to universal answer stability. Compare inspected primary implementations before
assessing originality. This does not claim a novel dynamic min-cost-flow theorem
or a stakeholder evaluation of fairness. Broader primary-paper priority remains
open if sources cannot be read.

## Limits and acceptance, frozen before headline runs

- Inputs: deterministic seed 13320261009; concrete Inputs.json fixed before runs.
- At most 10 nodes, 25 edges, capacities 0–5, integer cost units with rational
  denominator 2; balanced integer supplies and nonnegative finite lower bounds.
- At most 1,000 negative-cycle cancellations and 10,000 augmentations per solve;
  each worker has a 30-second wall budget and 256 MiB address-space limit.
- Each serialized certificate at most 16,384 bytes; one previous certificate is
  retained, with a 4,096-byte cache budget. Oversize entries are evicted; no silent
  truncated certificate or omitted fallback. Separately frozen binding-budget
  controls use a 64-byte cache budget.
- Valid certificates and objective values must match the independent reference.
  Tied plans may differ between methods; deterministic per-method primal/potential
  identities must match fresh replication. Compare every logical field, model
  digest, proof content, operation counter and control outcome. Exclude only the
  explicitly listed timing/kernel-resource/path fields, never mathematical data.
- Every distinct valid certificate is replayed and subjected to invalid controls.
  Infeasibility requires a violated cut, not merely rejection of a prior flow.
- Any incomplete run is retained and reported. No broad scalability/statistical
  superiority claim follows from three small repetitions or this modest suite.
- Source/input/dependency hashes are frozen in Freeze.json after separate
  development checks, before headline execution. Later changes require a preserved
  amendment and a new run, rather than silently modifying a sealed implementation.
- Audit with independently coded exhaustive/network-simplex references; execute
  all headline work again from a fresh directory using the same pinned dependency
  installation. This is replication, not an independent installation.
- Package source, inputs, certificates, measurements, failures, audits and replica
  in a compressed, individually hashed archive. Preserve Git history and SDKs
  outside Git; publish supported claims with unresolved limitations visible.
