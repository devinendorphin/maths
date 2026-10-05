# Experiments 66–75: findings

All ten bounded comparisons finished: **58 input records, 468 workers (192 headline and 276 timing), 455 complete trajectories and 13 resource-limit stops**. Every input has complete exact answers from at least one method. The record contains **61,797 integer-observation checks** and **16,695 oracle/interval-endpoint checks**. These counts include repeated checks, not distinct observations. All stored audits and the subsequent full independent re-audit passed. All 468 statuses and logical worker signatures, including the same capped work, matched a fresh replication; the proof summary counts also matched.

The strongest changes are a simpler exact solver gate and crossing-guided integer queries. Neither establishes a universal winner. Unrestricted tree retention remained costly even on matched short sequences, while the difficult correlated-profit inputs exposed a terminal-partition storage limit in our B&B reference implementation. The algorithm/audit execution phase took **20.29 seconds**, against a declared 900-second limit; design, implementation, further verification and archiving were separate work.

## 66 — The simpler gate improved this mixed subset

The new fixed rule normalizes weights, then chooses dense DP if capacity is at most 4,096 and exact B&B otherwise. It removes the prior gate's sparse branch for n<=16. Both gates and B&B completed all eight small/large-weight inputs. Fixed dense completed five; its other three stopped before dense allocation.

On four fixed repeated cases, old/new gate/B&B aggregate median CPU was **0.083155 / 0.073517 / 0.086931 seconds**. The new gate used **11.6% less CPU than the old gate**, winning three paired inputs out of four; it used 15.4% less than B&B, with two paired wins. Dense's mixed timing aggregate is ineligible because only six of twelve timing runs completed.

Small/large weight variants share each (n,seed) profit/slope draw and transform the same base weights. They are matched records, not independent draws. The threshold was fixed before execution from the preceding batch's existing dense threshold; no timing-based training occurred.

## 67 — Huge profit integers preserved decisions and work counts

Two 12-item draws were each multiplied by 1, 2^128 and 2^512, scaling every profit intercept and slope together. All six inputs completed under dense and B&B. Each seed's optimal integer packings, seven oracle calls, real pieces and operation counts were unchanged across scales. Positive common objective scaling preserves the exact optimizer.

The timing subset used seed 1. Dense per-input medians at 0/128/512 added bits were **0.005278 / 0.003783 / 0.003290 seconds**; B&B medians were **0.013015 / 0.010200 / 0.005994**. These tiny measurements do not establish that large integers are faster or have no arithmetic cost: temporal/runtime variation dominates this small test, and the fresh validation run did not reproduce that monotone timing pattern. Logical replication is separate from the original timing pool. **Decision:** preserve the exact-arithmetic result; draw no numerical-size speed law from these timings.

## 68 — Degenerate ties passed independent checks

Six explicit four-item fixtures covered duplicate lines, all-zero profits/slopes, everywhere-negative profits, zero-profit items, and exact integer crossings. Real dense, integer midpoint, integer crossing and real B&B all completed. Every oracle followed the declared primary-profit / directional-slope / smallest-mask ordering; every emitted integer answer was independently optimal. In this batch none of the primary-optimal outputs differed from the positive-side canonical answer, although the protocol only requires primary optimality at real-envelope endpoint ties.

Headline real/midpoint/crossing methods made **16 / 23 / 18 queries**. The repeated timing subset consists of two very small fixtures and sub-millisecond totals; it is a correctness control, not a useful application-speed estimate.

## 69 — Matched short sequences also made unrestricted tree reuse expensive

The same two 14-item draws and the same current B&B implementation were evaluated at H16, H64 and H256. Cold, incumbent and tree methods each performed **678 point solves** across the six records. Cold and incumbent each visited **4,626 nodes**; tree reuse visited **29,961**. The initial greedy bound already found equally strong candidates on these inputs, so the old incumbent saved no nodes.

On seed 1 across the three matched horizons, cold/incumbent/tree aggregate median CPU was **0.059835 / 0.059080 / 0.197121 seconds**. Tree cost **229.4% more than cold**, losing all three paired cases. Its per-input medians were slower at H16, H64 and H256, not merely the longest horizon. Incumbent was essentially tied with cold (1.3% lower aggregate, two paired wins).

This removes the solver-version confound within this comparison and supports experiment 63's caution. It does not invalidate experiment 52's different input/implementation result or isolate horizon length as its explanation. **Decision:** unconditional partition retention is not the default; incumbent-only reuse has lower storage exposure, but its benefit depends on the input.

## 70 — A size ceiling helped, but incumbent-only still won overall

The fixed policy retains a terminal partition only if it has at most eight cells, otherwise carrying just the last best packing. All three methods completed all six 10/14/18-item trajectories. Incumbent/small-tree/full-tree methods visited **1,616 / 3,066 / 6,838 nodes**, with 390 point solves each.

Repeated aggregate CPU was **0.036244 / 0.043411 / 0.099085 seconds**. The ceiling saved **56.2% versus unrestricted retention**, winning all three paired cases, but cost **19.8% more than incumbent-only**, winning one of three. The decision and discarded-history handling are inside algorithm timing. The eight-cell threshold was not tuned after outcomes. This shows a way to contain overhead, not evidence that eight is an optimal general threshold.

## 71 — Crossing-guided integer queries reduced midpoint work

Integer recursion now optionally probes the floor of the intersection of the two endpoint packing lines, clamped strictly inside the integer interval. Equal slopes use the midpoint. Equal endpoint packings certify the whole interval because every objective difference is affine. This is a query-selection variant of established exact parametric methods, not a new optimality theorem.

Across matched H64/H1024 draws and the previously used six-item subinteger boundary fixture, real/midpoint/crossing methods used **53 / 66 / 29 oracle calls**, with **40,572 / 51,008 / 24,896 DP transitions**. All five records completed. The boundary fixture is a reused control, not a new independent sample.

On three fixed repeated cases, CPU was **0.011565 / 0.009048 / 0.004345 seconds**. Crossing saved **52.0% versus midpoint** and **62.4% versus real recursion**, winning all three paired inputs against each. Progress clamping makes recursion finite but can yield poorly balanced splits; the existing query/CPU caps still apply. Integer interval counts describe certificate blocks, not the number of real optimal pieces.

## 72 — More capacity did not mean more B&B work

Two fixed 16-item item sets were evaluated at capacities floor(total_weight/8), floor(total_weight/2), and floor(7*total_weight/8). All dense/sparse/B&B methods completed all six inputs. These variants deliberately change feasible packings; they are not representation-equivalent rescalings.

Dense transitions grew substantially with capacity. B&B node counts were **167/70/42** for seed 0 and **111/480/62** for seed 1 from tight to loose capacity: intermediate capacity was harder for seed 1, while seed 0 decreased throughout. Oracle-call counts also changed with the number of real pieces.

On the three seed-1 timing cases, dense/sparse/B&B CPU was **0.022723 / 0.013443 / 0.021213 seconds**. Sparse used **40.8% less than dense**, winning all three paired inputs, and 36.6% less than B&B, with two paired wins. This favorable sparse subset is a reason to keep it available, even though the simplified gate omits it. Capacity alone does not predict every solver's cost.

## 73 — Correlated profits exposed a reference B&B storage limit

Four 16/20-item inputs used profits equal to their weights, with small signed slopes. Dense and the new gate completed all four, using **13 queries and 690,807 transitions** per method. All normalized capacities were below 4,096, so the new gate correctly selected dense.

B&B completed three; the fourth (20 items, seed 1) stopped during its first query at the **4,096-cell terminal-partition allocation cap**, after 8,894 visited nodes. Our audited B&B implementation stores terminal partitions even for cold solves. This is an operational limit of that reference implementation and evidence format, not proof that a production B&B solver cannot solve the instance. The three completed headline inputs visited 24,164 nodes altogether, much more than many earlier uncorrelated cases.

Dense/new-gate repeated CPU was **0.123678 / 0.129682 seconds**. Their kernels and work were identical; gate overhead/noise produced 4.9% higher aggregate CPU with one paired win out of two. B&B's mixed timing is censored (only three of six runs complete). **Decision:** keep bounded-capacity dense optimization and explicit storage limits; do not extrapolate earlier easy B&B timings to correlated instances.

## 74 — Shared checked bounds halved actual point-proof checks

Three fresh eight-item curves contained eight positive-length optimal pieces. Both proof sweeps covered every piece and included two point controls per case. Without caching, **22** point certificates were generated and externally checked. A time-keyed cache needed **11**, serving **11 additional endpoint references**. A cached certificate proves the optimal objective bound at that time; each possibly different endpoint packing is separately checked for feasibility and equality to that bound. Sharing a bound does not assert that neighboring optimal packings are identical.

Across both sweeps the pinned official VIPR checker accepted **33 valid certificates** and rejected **33 deliberately false final bounds**. The sweeps produced **16 interval bundles** and **36 explicit scope rejections** (varying feasibility, nonlinear objective, mismatched domain, mismatched coefficients, reversed endpoints, different endpoint packing). The 206 interval integer checks count both sweeps and any shared integer endpoints.

Fresh/reused certificate bytes were **28,640 / 14,328**, derivations **398 / 199**, and valid-check CPU **0.079019 / 0.037772 seconds**. Native/adapter CPU components were approximately **0.003802/0.005428** versus **0.002243/0.003182**. These are single sweep component measurements, not three-repeat end-to-end proof-speed estimates; connector/cache/feasibility arithmetic is not included in those component sums. The count reduction is exact; the timing ratio is exploratory.

Independent re-audit regenerated every non-reused certificate from its frozen source proof, reran VIPR, checked every alias packing and every interval, and verified continuous interval coverage. The scope connector is ordinary Python and assumes truthful trajectory metadata. Neither VIPR nor the adapter/connector is claimed formally verified, and point proofs cannot reveal a hidden model change.

## 75 — Transfer favored the simpler real gate, with mixed integer gains

All five methods completed eight fresh n12/20/24/40 trajectories at H128. The 40-item audit uses independent exact-weight layers at capacity 96; n<=24 uses meet-in-the-middle enumeration. Old/new real gates made **100 queries each**; midpoint/crossing integer gates made **157 / 106**. Crossing reduced midpoint DP transitions from **264,234 to 176,363** and B&B nodes from **3,110 to 2,368**, but real gating used **173,963 transitions and 1,771 nodes**. These different work units are not a combined cost measure.

On four fixed repeated seed-1 inputs, old-real/new-real/midpoint/crossing/B&B CPU was **0.063540 / 0.048896 / 0.085087 / 0.062388 / 0.265655 seconds**. The new real gate saved **23.0% versus the old**, winning three of four paired cases. Crossing saved **26.7% versus midpoint**, winning all four, but used **27.6% more than the new real gate**, winning only two. The new real gate's 81.6% aggregate reduction versus B&B was concentrated in bounded-capacity cases; it won only two of four paired cases.

No result was used to retune the gate, crossing rule or partition threshold. **Decision:** use the simpler real gate as the provisional continuation baseline, keep crossing as a tested integer-only alternative, retain sparse optimization for favorable instances, and prefer incumbent-only carryover when full point sequences are required.

## Limits and next questions

These are small finite machine-local benchmarks of known methods. Timing subsets contain only two to four cases and three repeats; paired wins and medians of repeated sums are different aggregations, and neither provides statistical confidence. Objective scaling and horizon variants are dependent records. Original timing data was preserved; the validation replica is not pooled into the findings. No production SCIP comparison, peak-RSS study, general complexity improvement, novelty claim or application validation has been completed.

Useful next controls are a B&B implementation that can avoid retaining terminal certificates for cold optimization, harder large-capacity inputs under bounded independent checks, failure recovery across solver choices, and an external production exact solver when it becomes available. The integer crossing choice also needs deliberately unfavorable split examples before stronger performance claims.

[Roadmap](Roadmap.md), [protocol](Protocol.json), [inputs](Inputs.json), [freeze](Freeze.json), [worker summaries](Path-results.json), [summary](Summary.json), [verification](Verification.json), [replication receipt](Replication-check.json) and [recovery instructions](REPRODUCE.md) provide the reviewable record. The [prior literature review](../research-notes/Literature-review-2026-10-05.md) and [56–65 findings](../research56/Synthesis.md) remain the context. Previous campaigns are unchanged.
