# Complete measurements and decomposition

The primary decision-cost measure is the isolated nine-observation worker session:
external wall time and wait4 user+system CPU include Python startup/imports,
frozen-source checks, input reading, all query work, final report serialization
and output. Workers create no children, so there is no omitted descendant CPU.
Launcher CPU/wall, audit CPU/wall and setup observations are separate research
costs. Peak wait4 RSS covers the worker's full kernel lifetime, including startup
and reporting; it is not an application-object memory measure. All workers run
sequentially, so adding peak RSS values is not a meaningful concurrent memory
total. Summary.json retains descriptive arrays/aggregates; use max/min for memory.

Query components are disjoint measured blocks: encoding (raw JSON decode/rebinding),
admission (domain validation), feasibility augmentation, negative-cycle search
and updates (solver), final shortest-distance/certificate construction (proof),
failed captured/potential probes, final full checker, serialization, buffered disk
write/read plus full replay, and cache maintenance. The unassigned remainder is
ordinary dispatch/counter/report overhead; full query/session totals retain it.
Within NetworkX the solver block includes import, graph encoding and simplex;
these internal pieces are not separately timed. Its potential/cut completion is
separate and charged. I/O replay includes its second checker invocation, rather
than pretending that replay is free or subtracting it from total cost.

One previous proof is retained. Cache bytes are its exact serialized size,
not a count of entries or the Python heap allocation. Whole worker RSS measures
actual process memory, including heap/import/temporary data; cache-object-only
heap or allocator fragmentation is not measured. The 64-byte binding control
evicts all nine entries per method and charges the resulting work. Normal proofs
are 179–285 bytes and fit the 4,096-byte cache. No proof exceeded 16,384 bytes and
no worker exceeded the wall/address-space limit.

The parent waits at 5ms polling intervals, so external wall has polling/launch
overhead; CPU does not use this quantization. Native session medians near 36ms
must not be used to rank sub-millisecond improvements. NetworkX's first import is
inside each fresh session and is charged; its longer session times therefore do
not establish an inferior asymptotic algorithm or steady-state solver performance.

Setup.json's 1.196s observation covers wheel-hash verification and installation
only. Venv creation and the earlier wheel download were not captured by that
timer; full independent installation cost is unmeasured. The wheel identity was
checked against PyPI's SHA-256 over verified HTTPS. Both runs share this venv.
Input generation, development, code construction and archive preparation are
research work outside query maintenance, not silently part of a cheaper solver
baseline. This campaign makes no full-installation amortization claim.
