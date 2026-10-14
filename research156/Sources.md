# Credited implementation and measurement sources

The mathematical algorithms, exact admission and C API adapter are the unchanged
[152–155 implementation](../research152/Sources.md), retained byte-for-byte under
vendor/. The official OR-Tools v9.14.6206 C++ SDK, public min_cost_flow source and
Apache license are retained as source/build provenance. SDK shared libraries are
loaded externally and hash checked; they are not republished in the archive.
NetworkX 3.4.2 supplies the independent network-simplex reference. This batch
introduces measurement wrappers and accounting, not a new flow algorithm.

Python time.perf_counter_ns and process_time_ns are used according to the
[official time documentation](https://docs.python.org/3.12/library/time.html).
perf_counter measures elapsed wall time and includes waiting; process_time
measures process CPU and excludes sleeping. Resolution and monotonicity are
retained through get_clock_info. Exact interval closure follows subtraction
of common endpoints, not a claim of nanosecond physical accuracy.

Observer footprint is measured through matched full-process runs. Individual
category durations remain durations of the observed program; they are not
counterfactual costs of an uninstrumented program. Source priority review beyond
these explicit credited implementations remains open.
