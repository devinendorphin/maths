# Proposed experiments 51–55 after the literature review

Proposed 5 October 2026; not executed or frozen as an experiment protocol. This updates future priorities following the [literature review](Literature-review-2026-10-05.md). It does not revise any completed campaign or its original roadmap.

The purpose of this batch is to compare with established methods and remove duplicate work. Freeze inputs, implementation versions, stopping limits, timing exclusions and selection rules before each held comparison. Reusing completed inputs gives a retrospective comparison, not a fresh independent sample. Reserve new held inputs for transfer claims. Keep summaries and sources in Git; keep large proof records in the existing verified archive workflow.

## 51 — An established exact parametric baseline

**Question:** Does discovering the optimal value curve through exact solves cost less than constructing our reusable frontier?

Implement the exact endpoint/intersection recursion described by the Eisner–Severance literature and the 2025 survey (review [1]), with an exact rational-parameter oracle. Record the affine line and packing returned by every call. Specify extreme tie handling, endpoint ownership and stopping rules. For rational parameter `a/b`, scale the objective to integer coefficients `b*p_i + a*v_i`; retain exact arithmetic throughout.

First compare on a small fixed subset of completed inputs, then on a sealed held set. Compare the baseline with cold point solves, scalar maintenance and the existing indexed frontier. Check all declared integer observations independently. Separate the number of real-valued envelope pieces from the number of packings relevant at integer observations; a curve method may discover pieces that our observation grid never visits.

Report total CPU, oracle calls, memory, output pieces and proof/verification costs under the same boundaries. Do not describe oracle-call efficiency as a CPU guarantee. If this baseline wins clearly, adopt it before designing another frontier gate. Obtain Eben-Chaime's full paper before claiming a faithful implementation of that specific knapsack algorithm.

## 52 — Reuse the native optimization search

**Question:** How much of our apparent reuse benefit is already available from warm optimization?

Compare cold solves, incumbent warm starts and genuine search-tree reoptimization over the same objective sequence. Use the 2015 reoptimization work (review [6]) as the reference. Pin the solver and configuration. Reprice or reconstruct objective-dependent bounds and pruning decisions; check each returned answer against the independent exact oracle.

Before timing, check whether the selected solver supports the required combination of exact arithmetic and reoptimization. If it does not, keep the floating-point reoptimization comparison separate from the exact certificate comparison. Independently checking a small instance's answer does not make a floating-point solver generally exact. SCIP's transformed-problem certification and presolve limitations must be reflected in any proof claim (review [7]).

Charge initial setup, retained memory, repairs and the full sequence. A warm tree that beats our policy is a useful result: it lets us reuse existing software rather than maintain a duplicate solver.

## 53 — Schedule certificate failures instead of rescanning them

**Question:** Can an event queue reduce maintenance work while preserving our integer-time semantics?

Apply the kinetic-data-structure pattern (review [5]): cache each active scalar cell's failure time, maintain a priority queue, and batch simultaneous expirations. Invalidate or recompute entries when certificates change. Compare with the current horizon-scan driver using identical bounds and repair rules, so the experiment isolates scheduling.

Include strict-loss boundaries, ties, multiple simultaneous failures, stale queue entries, window joins and fallback after capped construction. Audit all observed answers and certificate coverage. Count internal proof failures, actual best-packing changes, horizon calculations, queue operations and repair work separately.

Do not infer that cheaper event dispatch makes expensive repairs cheap. Retain this change only if total sequence cost or a justified work bound improves.

## 54 — Reuse a standard proof checker

**Question:** Can an existing optimization proof format reduce custom checker work without losing the scope of our guarantees?

Do a small capability check for VIPR and VeriPB/CakePB (review [8–9]), then choose one format for a bounded adapter experiment. Start with exact point certificates. List the reasoning steps that translate directly, the transformations that need justification, and any unsupported steps. Preserve the original problem's feasibility and objective through every conversion.

Only then test whether interval reasoning can be expressed economically. A collection of selected point certificates does not prove every intermediate time. Measure proof size, production cost, verification cost and the remaining trusted code. Distinguish an independently executed checker from a formally verified checker.

If the adapter would require recreating most of the proof infrastructure, document that limitation and stop the integration. Do not turn this experiment into two full solver rewrites.

## 55 — A policy with an explicit cost model

**Question:** Can we state when construction is worth paying for, with bounded overhead under clear assumptions?

Start from rent-or-buy and costly-prediction work (review [11–13]). Define the actual model: maintenance charges, construction price, expiration, renewal, post-build maintenance, probe cost and fallback. State what future information the policy may observe. Determine whether a known theorem applies; if it does not, do not borrow its guarantee.

Compare a literature-informed policy with never-build maintenance, the strongest baseline from 51–53, and a hindsight benchmark defined for this same model. Prove a bound under stated assumptions or supply a counterexample that explains why one fails. Keep operation-count bounds separate from observed CPU results.

Use sealed inputs and charge every decision. If construction offers no active advantage after stronger comparisons, stop adding gates and retain the simpler method. A negative result that prevents unnecessary work is a successful outcome of this batch.

## Decision after the batch

Choose the simplest exact method that performs well under the declared evidence and guarantees. Continue research on a narrower gap only after the established baselines are competitive and the gap has a precise statement. No application impact, universal speedup or novelty claim follows merely from completing these five comparisons.
