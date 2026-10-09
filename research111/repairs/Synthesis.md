# Aligned continuation and bounded repairs

The available evidence supports conditional reuse and an actual exact-SCIP certificate route. It does not recover the separate historical 300-worker campaign or establish that every proposed comparison is complete. Start with [the evidence alignment](../Alignment.md) and [the preserved review](../REVIEW.md).

The question remains: when an objective changes, when does an exact answer stay optimal, when is checked evidence applicable, and when does the complete reuse path cost less than solving and certifying again? These are separate questions. We use the existing fixed-feasibility binary knapsack models with positive integer weights, fixed capacity, signed affine profits, and rational parameters.

## Evidence and assurance

The published 101–110 batch has 273 workers. The separate 300-worker report remains unrecovered. The provisional continuation has 284 records across stages 113–120. These counts describe different evidence sets and are never combined. This supplement has 77 records per run, plus two memory checkpoints, on two existing eighteen-item fixtures and the existing crossing control. Capacity, weight and objective variants are modifications of those fixtures, not independently sampled transfer models.

[Protocol.json](Protocol.json) and the 88-file [freeze](Freeze.json) preceded headline execution. Completion setup was added after a development gate and before that freeze. The [memory amendment](Memory-amendment.json) and separate [memory freeze](Memory-freeze.json) disclose an audit failure and its correction. The initial frozen auditor remains intact. The final independent auditor imports neither the producer, cache, SCIP API nor campaign; it enumerates original feasible subsets, checks certificate model bindings and original objective scaling, and replays external proofs. A separate integrity audit reconstructs the LRU trace and checks the real checker binary epoch.

Both audits checked 753 answers and 371 proof bindings. Each replayed 31 distinct accepted proofs and rejected 31 strengthened false bounds. All mathematical, admission, cache-event and proof-identity fields match between fresh directories. Raw SCIP proofs, completed proofs and control bytes match separately from measurements. [Replication.json](Replication.json) names every excluded measurement and diagnostic file category; no logical field was excluded. Both runs share the external SDK, so this is not an independent installation.

Lean checked the rational endpoint implication in 96–100. It did not verify these Python implementations. VIPR checks a certificate's encoded problem; the independent binding audit connects that encoding to our original model. Immutable admission captures checked facts about a fixed model and explicit dependency epoch. It does not monitor external proof files or arbitrary code changes.

## What changed and what it showed

**111–112: native exact SCIP now works in a separately built deployment.** Signed Debian metadata supplied MPFR/Boost, and official SoPlex 8.0.0 and SCIP 10.0.0 sources built successfully. All nine native SCIP certificates were independently accepted. Six required official VIPR completion; its CPU, including child work, is charged inside each certificate's full total. The three rational crossing queries were accepted without completion. The auditor checks SCIP's maximize-to-minimize conversion and positive objective normalization, including factors 5 and 9 on the factor fixture and factor 2 on the crossing control. Presolve and separating rounds were disabled. This is nine bounded certificate observations, not general support for arbitrary settings or transformations.

The earlier missing-MPFR configuration failure remains in the provisional record. It establishes that attempt's missing prerequisite; the successful build establishes a different, compatible deployment. The ordinary PySCIPOpt wheel still lacks exact support. Native exact SCIP and ordinary reoptimization are separate paths: the pinned exact-mode source explicitly rejects their combination.

The exact setup script took 320.28 seconds within its 600-second cap; the completion build script took 93.05 seconds within a separately declared 180-second cap. These measured scripts exclude inherited source acquisition, prior development and the preceding CMake installation/failed CMake attempt. They are **not a measured aggregate installation cost**. Setup and independent auditing are disclosed separately from per-stream maintenance totals.

**113: startup can be amortized with verifier state isolated.** An adapter includes the unchanged inherited VIPR source. A resident parent never checks proofs; it forks a fresh child for every request. Each child inherits pristine globals, and cannot update the parent's verifier state. This saves repeated exec/loader startup; it does not reuse a prior proof's logical state or implement in-process incremental checking. Each of three paired trials used the identical twenty-request valid/false/valid/malformed/valid sequence. All decisions matched direct checking. Median total CPU was 142.3 vs 58.7 ms in the headline run, and 137.8 vs 69.0 ms in replication. Totals include child CPU, fork/IPC and startup. File/proof preparation is outside this checker-only comparison. No VeriPB amortization is established.

**Endpoint admission: savings depend on a usable region.** Point solving, repeated endpoint admission and one-time immutable admission share the original-problem native/VIPR assurance contract. Preparation and failed probes are charged. On the factor fixture, the same packing is optimal at both endpoints, so immutable admission can safely cover the interval. On the changing-optimum fixture, endpoints differ; the wide snapshot is refused and checked point fallback runs.

Median complete CPU in milliseconds (three repetitions per cell):

| Fixture / queries | Headline points / replay / immutable | Replication points / replay / immutable |
|---|---|---|
| Changing optimum, nine dense queries | 99.6 / 120.8 / 123.7 | 108.4 / 145.4 / 132.8 |
| Changing optimum, three sparse queries | 35.6 / 54.5 / 53.2 | 36.4 / 54.3 / 61.0 |
| Positive factor, nine dense queries | 148.7 / 212.2 / 27.3 | 158.5 / 223.7 / 27.7 |
| Positive factor, three sparse queries | 44.7 / 90.3 / 30.2 | 45.7 / 101.8 / 29.5 |

These data support cheaper immutable admission for this factor fixture and a charged failure penalty for this wide non-factor interval. They do not reproduce the missing twelve-item models or show a general dense/sparse crossover. Positive-factor reuse needs less preparation and remains an important simpler baseline in the preserved earlier work. This supplement does not establish superiority over that shortcut or over local guarded windows.

**114: ordinary reoptimization and cost decomposition use compatible certification.** Cold SCIP and objective reoptimization each pay for a full duplicate native exact solve, witness, VIPR construction and external check. Those are independently certified ordinary SCIP answers, not SCIP-generated certificates. Reoptimization's dense medians are lower in both runs on both fixtures. The factor fixture's sparse comparison changes order in replication (54.09 vs 54.28 ms); small differences do not establish a stable advantage.

Disjoint phases cover ordinary solver work, native optimization plus witness construction, VIPR encoding, proof hash/write I/O, checker including child CPU, model/primal/hash admission and output I/O. The full total is primary; the measured residual is retained. The native algorithm creates its optimization result and witness together, so those two costs remain inseparable. For example, one headline factor/dense/cold trial charged 178.7 ms total: 120.7 ms checker, 24.3 ms VIPR encoding, 21.6 ms ordinary SCIP, 7.0 ms native optimization/witness, with remaining I/O/admission and residual included. Component values describe that trial, not a new general bottleneck claim.

**119–120: cache bytes, actual resident memory and explicit invalidation are different measures.** Independent replay of the two-entry LRU trace confirms two hits and three initial evictions. Actual cache contexts change capacity, weight, affine objective, domain, nonlinear objective and the checker binary. Supported changes discard old entries and recertify; continuous/nonlinear changes block reuse. The checker changes to a distinct compiled binary implementing the same unchanged verifier, and its byte hash becomes the new epoch. This is a real dependency replacement with an explicit update, not arbitrary code-change detection.

Retained Python cache graphs measured 3,201 and 3,425 bytes in the headline run; serialized point facts measured 914 and 914 bytes. Tracemalloc covers the whole scenario, including other live records, and is not mislabeled as cache-only memory. After the final invalidation/clearing steps, the empty cache graph measured 240 bytes in both cases.

The original process-tree sampler was invalid in this environment: `/proc/.../children` is absent, and its tree-labelled records silently measured only the runner. Those records and the failed audit assertion are preserved. The separately frozen correction discovers parentage using `/proc/*/status` and holds an unchanged verifier's real parsed state after successful checking until release. Live runner-plus-checker RSS was 18,600/18,640 KiB in headline and 18,184/18,232 KiB in replication; PSS is also retained. This is a controlled verification checkpoint in a separate process, not the unmodified campaign's peak memory or a simultaneous live-cache peak. Shared pages can be counted twice in RSS. Thus integrated memory coverage is improved, but a complete unmodified process-tree peak remains partial.

## What remains open

The missing 300-worker evidence is still provisional. The official CP 2024 DP/VeriPB adaptation and historical zero-node interruption controls were not recovered or reproduced; Python DP remains an explicit substitute. The provisional density policy selected the same factor-aware route in both buckets, so discrimination is unestablished. Existing held-out, rational-control and local-window work remains valid in its declared scope and was not rerun for numbering. Original endpoint interpolation/scaling and cache/reoptimization ideas are credited in [Novelty.md](Novelty.md); these measurements and the disclosed adapter are original repository work, without an established literature priority claim.

This publication is a repaired continuation with visible partial comparisons. It is not a claim that ten requested experiments, or the missing previous batch, have all been verified.
