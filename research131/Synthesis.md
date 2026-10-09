# Closing the small knapsack map: experiments 131–132

These two bounded experiments finish specific open edges of the small-instance inquiry. They are a stopping point for this experimental phase, not a claim that every mathematical, implementation or scalability question is settled. Earlier evidence sets and freezes remain unchanged.

## 131: short-lived checker memory

Two archived models, eval8 and eval12, each supply unchanged native/VIPR and CP/VeriPB certificates at parameter zero. Independent workers compare a 2ms sampler on/off, three repetitions, for 24 records in each directory. A small C launcher calls `wait4` on the unmodified checker, subject only to the frozen 30-second cap. It reports kernel child CPU and lifetime high-water RSS without keeping the checker alive.

All 24 kernel child peaks were positive in each execution. Native peaks were 2,176 KiB on eval8 and 2,304 KiB on eval12. Most VeriPB peaks were about 19,572–19,576 KiB; the primary sampled eval12 series included 19,704 KiB. All checker decisions remained valid and independent false bounds were rejected. The measured checker boundary includes the launcher/checker, observer where enabled and checker-log I/O; worker imports and final JSON reporting lie outside it; these are measurement scenarios, not revised 121–130 performance totals.

**Scope matters:** these are individual process-lifetime peaks, not an exact simultaneous tree peak. The C launcher's own `ru_maxrss` is about 16,000 KiB and contains its earlier Python-launch lifetime; it is not an isolated C-runtime footprint. The initial freeze's small-launcher hypothesis must not be read as a numerical bound on that reported history. Per-checker peaks include fork/exec lifetime. Sampled observations see at least the launcher in this deployment, so “sampled child seen” does not establish that the brief native checker itself was captured. Summing independent lifetime peaks is not a measured simultaneous peak. The earlier 127 limitation remains visible, now complemented by useful per-checker accounting.

## 132: two parameters and certificate geometry

For fixed feasibility and affine objectives, a common feasible packing optimal at every vertex remains optimal throughout their convex hull. This is the established convex-combination argument in two dimensions. The experiment applies the inherited native producer and unchanged VIPR checker to exact point objectives; the adapter converts both rational parameters to a common integer scale and the separate auditor reconstructs the original two-parameter objective.

Three initial three-item cases test a stable packing, a crossing and an omitted rectangle corner. The first two admit their declared triangles. The rectangle case passes three vertices but fails the fourth: the candidate loses optimality at `(2,2)`. Admission of the triangle therefore does not certify the whole rectangle. At `(3/2,3/2)` the answer can stay optimal outside that admitted triangle and receives fresh point certification.

Those first cases have degenerate/redundant directions on feasible alternatives. They are useful controls but do not by themselves demonstrate two independently effective priorities. A separately frozen fourth case supplies vectors `(0,2,0)` and `(0,0,2)` acting on separately feasible items. The candidate is optimal on `t <= 3/2, s <= 3/2`, while the admitted triangle covers only `t+s <= 3/2`. At `(1,1)` the answer is still optimal outside the admitted triangle; safe fallback checks it afresh. Rational observations on either side of the boundaries remain exact.

In all initial cases the packing stays optimal at `(1,0)`, but the independent original-model binder rejects the old point proof under the changed objective. The old bytes remain valid for their own original point. Answer stability, original point-proof applicability and admission of a vertex-based region remain distinct.

## Audit and replication

The 27 original records (24 memory + three geometry scenarios) match all logical fields in fresh-directory replication. The independent original audit checks 36 two-parameter answers and 36 encoded/fixture point answers, binds 34 proofs, accepts 23 distinct proof identities and rejects all corresponding false bounds. These proof identities include old memory fixtures; they are not all new proofs.

The separate rank-two scenario adds twelve original query checks, eleven encoded point answer/binding checks, eleven valid distinct VIPR proofs and eleven rejected false bounds. These eleven are disjoint from the original 23 proof identities, yielding 34 across this closure. It is one additional scenario, not twelve additional models. All 28 scenario/worker records reproduce logically and in their underlying proof/formula/witness identities. Timings and memory measurements are excluded only from exact equality and retained in Summary.json and both raw result sets.

An initial rank-two runner failed before solving because the inherited native module inserts its dependency path and caused `campaign` to resolve to an older module. The corrected import order, original script, freeze and amendment are preserved. It did not change inputs, methods, assertions or existing results.

The four new geometry models are explicit designed controls, not blinded transfer samples. The two memory models are archived fixtures, not new sampled models. External SDK installation is shared. Python admission/audit/cache code is not formally verified. Vertex interpolation, parametric regions, kernel accounting and proof checking are credited as established ingredients.

## The larger direction

The next problem is [affordable, auditable resource allocation as needs change](../projects/certified-allocation/Problem.md). Network flows give a tractable starting model and small potential certificates. Explicit service commitments can be checked across changing costs, capacities and supply; fairness choices remain a separate human and mathematical question. The new charter includes a checked four-edge example and a precise maintenance-cost research target. It does not claim a large benchmark, a new general theorem or a replacement for human mathematical work.
