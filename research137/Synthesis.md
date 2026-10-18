# From repeated observations to explicit proofs

Experiments 137–139 turn the allocation roadmap's mathematical gap into two
Lean-checked results and a sharp written sensitivity theorem. These are concrete
proof results using established optimization mathematics.

**The general certificate theorem is proved.** On any finite rational network,
a feasible flow with valid node potentials is a global minimum among all feasible
rational alternatives. The formal proof derives potential cancellation from the
actual node balances. A second theorem proves preservation under any complete
set of cost changes whose residual signs still pass, plus an exact objective
update identity. The statements impose no graph-size bound.

**The cost-stability boundary is exact.** For one changed edge cost, two shortest
return paths give the entire closed interval where the same plan stays optimal.
At every finite boundary a different feasible plan ties; beyond it an explicit
plan is cheaper. Unreachable return paths prove an infinite endpoint. Both
residual orientations of the changed original edge must be removed.

The path theorem has a complete written proof in [Theorems.md](Theorems.md),
but is not yet formalized in Lean. Its implementation exports independently
checkable distance/path or reachability witnesses. Lean verifies the mathematical
certificate conditions, not the Python parser or evaluator.

The restored final execution and fresh-directory replication agree byte for byte:

| Evidence | Count per directory |
|---|---:|
| Tiny frozen models | 31 |
| Inherited starting model encodings (four graph families) | 8 |
| Single-edge intervals for selected optimal flows | 217 |
| Rational cost-query checks | 1,070 |
| Strictly cheaper feasible competitors outside the interval | 165 |
| Rejected invalid controls in main validation | 801 |
| Enumerated feasible integral flows across tiny models | 121 |
| All optimal integral flows in those tiny models | 34 |
| Additional interval checks covering all those optima | 115 |

The 115 all-optima checks overlap selected-flow checks and are not independent
new instances. Eight inherited starts are two cost encodings for each of four
earlier graph families (4–10 nodes, 4–25 edges), not eight new unseen families.
Exhaustive enumeration is confined to tiny models. Larger cases use exact
optimality and interval witness evaluation.

In 290 sampled queries the same flow stayed optimal while the old captured
potential failed; newly checked potentials certified it. This is a sampled query
count, not a real-workload frequency estimate. Standalone serialized replay
rechecked every interval/query and every optimal tiny flow, and recreated 369
invalid endpoint/flow controls. Those overlap the 801 main controls and should
not be added as unique controls.

**Separately safe changes can be unsafe together.** For two parallel edges with
costs (0,2) and flow (1,0), changing only the first cost to 2 is safe; changing only
the second to 0 is also safe. Together the old plan costs 2 and the alternative
costs 0. A safe simultaneous update is separately admitted by checking potentials
against all new costs. Single-edge ranges cannot be multiplied into a joint guarantee.

Both formal builds accept Flow.lean and the explicit Spec.lean contract, reject
two deliberately false statements, and contain no sorryAx in successful proofs.
Only source deployment paths in rejected-control diagnostics are normalized.
Both copies share the same verified Lean/Python installations.

The preceding local commit/archive were lost during a temporary workspace reset
before publication approval was processed. The restoration reproduces the FULL
previous 567,235-byte Results.json and SHA-256, not just counts. This new archive
has its own identity and retains the restored runs. See [Restoration.md](Restoration.md).

The concrete advance is a general machine-checked certificate/maintenance
foundation and exact checkable single-edge thresholds. No new optimization
priority or faster complete dynamic-allocation algorithm is claimed; see
[Literature.md](Literature.md).

The next proof task is formal cycle decomposition and the shortest-path necessity
argument. The next implementation task is a genuine versioned delta interface
accounting for admission, rejected updates, repair, export and storage. Larger
frozen workloads and compatible incremental solvers are needed for performance claims.
