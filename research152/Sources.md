# Credited specialist methods and executable custody

The primary methods inspected are the complete pinned OR-Tools v9.14 header and
implementation retained with their Apache-2.0 license:

- <https://github.com/google/or-tools/blob/v9.14/ortools/graph/min_cost_flow.h>
- <https://github.com/google/or-tools/blob/v9.14/ortools/graph/min_cost_flow.cc>
- <https://github.com/google/or-tools/releases/tag/v9.14>

The header describes cost-scaling push-relabel and distinguishes the Generic
incremental interface from Simple's lack of incremental state. Inspected methods
include Generic SetArcCapacity, SetArcUnitCost, SetNodeSupply, Flow, Supply,
CheckInputConsistency, CheckFeasibility, Solve and CheckResult; Simple's complete
SolveWithPossibleAdjustment rebuilds its graph and Generic optimizer. Generic
Solve retains residual flow/capacity but resets node potentials. Its supply
setter assigns remaining node excess directly. Its internal feasibility check
builds from forward total capacities, so this adapter instead requires externally
checked full-model feasibility before disabling that check and solving warm.

The official Ubuntu 22.04 x86_64 C++ SDK release is pinned by its published SHA256:
`127a82bbbf304d26721bb9b41ecce2d66f21c757204ab5aa2cc37eaa6ffb7eb6`.
Both native routes execute this SDK, not a locally rebuilt solver or Python-wheel
variant. Build.json records compiler, adapter build command and SDK library
hashes. Freeze.json pins the actual mapped library hashes, exact adapter bytes,
sources and environment. The SDK remains an external reproducible dependency;
the small compiled adapter and source are retained in complete evidence. Absolute
build paths are provenance, with SDK override/loader guidance in reproduction.

The wrapper is assistant-authored for this inquiry and uses credited established
solver methods. NetworkX 3.4.2 supplies the algorithmically different cold audit
reference. Exact admission, residual feasibility/cancellation and transaction
code are copied unchanged from 148–151; its family generator is reused with
new seeds and extended mixed streams. The inherited controls remain separately
identified. New contributions are the inspected adaptation, literal retained-state
audit and this finite comparison, not a new flow algorithm or a broad solver rank.

This source inspection does not close a priority review of all dynamic-allocation
literature. No inference about novelty is made from titles, abstracts or metadata.
