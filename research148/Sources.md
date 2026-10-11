# Implementation and comparison provenance

Residual feasibility repair and negative-cycle cancellation are established
minimum-cost-flow methods. `producer.py` and the exact checker are copied from
145–147; only the checker's module description changes. This stage adds a strict
transaction interface, ownership/rollback controls and a new finite comparison.
It does not claim algorithmic novelty or a literature-wide performance result.

NetworkX 3.4.2 is the credited cold network-simplex implementation. Its exact
source hash is frozen. The previously credited retained-basis adapter is not
used here because that adapter rejects noncost and self-loop changes.

The specialist cold baseline is Google's OR-Tools 9.14.6206 Python binding of
SimpleMinCostFlow. Inspected primary source is pinned to the v9.14 tag:

- <https://github.com/google/or-tools/blob/v9.14/ortools/graph/min_cost_flow.h>
- <https://github.com/google/or-tools/blob/v9.14/ortools/graph/min_cost_flow.cc>
- <https://developers.google.com/optimization/flow/mincostflow>

The full header and implementation are retained unmodified with Apache-2.0
license. The header describes cost-scaling push-relabel and distinguishes
incrementality in GenericMinCostFlow from its absence in SimpleMinCostFlow.
The implementation's complete Simple SolveWithPossibleAdjustment path clears
arc_flow_, rebuilds the graph and maximum-flow feasibility check, constructs a
new GenericMinCostFlow, sets all costs/capacities/supplies and solves it. Therefore
reusing the Simple wrapper would not establish warm optimizer reuse; this code
constructs a new wrapper for each query. Generic's setters and Solve path retain
residual capacities/flows but reset potentials before optimization. This source
reading motivates a future C++ Generic comparison, not a claim it was measured.

The Python native extension and libortools shared-library SHA256 hashes are
frozen alongside versions and the NetworkX source hash. Requirements pin the
installed environment. Retained upstream source documents inspected semantics;
this campaign executes the distributed wheel, not a local source build. Binary
hash equality is required in the accepted replica. The archive does not copy
third-party wheels or the whole environment.

Source review is limited to these concrete implementation methods; the dynamic
allocation literature and established reoptimization approaches still require
the wider priority review named in the larger roadmap.
