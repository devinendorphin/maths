# Experiments 56–65: findings

All ten bounded experiments finished. **420 workers** covered **70 input records**: **402 completed their declared trajectories and 18 stopped at prospective allocation limits**. At least one method produced complete exact answers for every input. The record contains **53,278 integer-observation checks** and **14,233 oracle/interval-endpoint checks**; all stored audits passed. Completed logical repeats matched across 66 repeated groups. Capped runs are censored in speed comparisons.

The execution phase took about 55.5 seconds against a declared 900-second limit; implementation, checking and archiving were separate work. Larger numeric capacities were not uniformly harder. Removing common weight factors and choosing a suitable exact oracle mattered much more than merely increasing the number of items. Integer bisection and retained search partitions did not consistently improve performance.

## 56 — Larger written capacities can be redundant

Two 12-item draws were each rescaled by factors 1, 16, 256 and 4,096, multiplying all weights and capacity together. The feasible packing set was unchanged. Gcd-normalized dense DP and exact B&B completed all eight cases. Raw dense DP completed six and stopped before allocating an array on the two largest cases.

On the fixed two-case repeated subset (seed 1 at factors 1 and 256), median aggregate CPU was **0.841220 seconds raw**, **0.006346 normalized**, and **0.008409 B&B**. Normalization reduced raw dense CPU by 99.25%, with both paired inputs faster. This is a familiar representation reduction, not a new optimization principle or an independent difficulty increase.

All eight normalized and B&B curves used 72 oracle calls per method. Normalized dense work was 41,712 transitions. Raw work was 2,788,524 transitions on its six complete cases; those totals have different completion denominators and are not a fair eight-case speed comparison.

## 57 — More items were manageable at bounded capacity

All three methods completed all eight 12/24/48/64-item cases at capacity 96. Each method made 114 parametric oracle calls. Dense DP performed 433,113 transitions and sparse DP 401,663; B&B visited 12,733 bound nodes and sorted 355,584 positive terms.

On the fixed 24/48-item seed-1 subset, repeated aggregate CPU was **0.042153 seconds dense** and **0.041138 sparse**. Sparse had a slightly lower aggregate median, but it was slower on both inputs' own three-repeat medians. These different aggregations need not rank methods identically; this is a near tie, not convincing evidence of a sparse advantage.

The successful 64-item cases have a small capacity and an independent exact-weight layer audit. They do not demonstrate scalability for arbitrary 64-item knapsack instances with large weights and capacities.

## 58 — Integer-only queries were not automatically cheaper

Matched trajectories used H64/H256/H1024, plus two crafted examples with several real-valued optimal pieces between integer observations. Real-curve recursion used **82 oracle calls** across eight cases; integer bisection used **88**. Both produced exact integer answers.

The six-item boundary fixture had six real pieces but only two observed packings. Integer bisection needed eight queries versus nine for the real curve. On the four-item fixture it needed eight versus seven, despite observing only two of four real pieces. Eliminating unobserved pieces can be offset by the bisection depth.

On the declared mixed timing subset, integer bisection used **0.004702 seconds**, versus **0.003189** for real recursion: **47.5% more aggregate CPU**, with one paired win out of two. Its output intervals are bisection certificate blocks, not a canonical count of distinct optimal pieces.

**Decision:** retain integer bisection as an exact alternative, without assuming it is the default faster method.

## 59 — The standard gcd reduction handled capacity remainders exactly

Eight cases tested common weight factors 16/256 and capacity offsets 0/g−1. Dividing every weight by g and replacing capacity by floor(C/g) preserved feasibility, including the unused remainder. Both versions completed every case with the same **48 oracle calls**.

Raw dense work was **4,263,616 transitions**; normalized work was **31,636**. Repeated CPU on the two factor-256 seed-1 cases was **1.047155 versus 0.004260 seconds**, a 99.59% reduction with both paired cases faster.

**Decision:** apply this known exact reduction before capacity-based allocation and solver selection. The offset controls verify the implementation; the mathematical reduction itself is established and elementary.

## 60 — Sparse storage helped some large-weight instances and also reached its cap

Six 12/16-item cases used small, gapped and large integer weights. Normalized dense DP completed two small-weight cases and stopped before allocation on four others. Sparse DP completed four and stopped before exceeding 30,000 states on two 16-item cases. B&B completed all six.

On the two complete 12-item large-weight timing cases, B&B used **0.002908 seconds**, versus **0.028412 sparse**, about **89.8% less CPU**, with both paired cases faster. Missing dense or sparse answers are not counted as wins.

The largest written capacity in the entire batch was **32,767,508**. That instance had gapped weights with special structure; solving it does not establish a general large-capacity performance guarantee.

## 61 — The fixed solver gate was useful but not the best universal choice

The untrained rule normalizes weights and chooses dense DP when C<=4,096, sparse when n<=16 otherwise, and B&B for the remaining cases. Feature calculations are repeated and charged at each oracle call. It completed all eight new cases, as did sparse DP and B&B. Fixed dense DP completed four; its incomplete cases make its mixed aggregate timing ineligible for a speed ranking.

On the four-case repeated subset, the gate used **0.050610 seconds**, B&B **0.032919**, and sparse **0.357399**. The gate used **85.8% less CPU than sparse**, with three paired wins out of four, but **53.7% more than B&B**, with one paired win out of four.

**Decision:** keep the gate provisional. Input-only choice avoids obviously oversized dense arrays, but its fixed sparse branch can be expensive. No held result was used to retune the thresholds or select a new gate.

## 62 — Forced query failure remained sound and its cost was visible

Every primary dense/sparse/B&B oracle attempt was forced to stop after one transition/node, then retried with normalized dense optimization. Across four headline inputs, each forced variant had **31 abandoned attempts and 31 successful fallback queries**. All trajectories completed; abandoned queries remained inactive and provided no interval certificate.

Relative to direct normalized dense optimization on the fixed timing subset, forced dense/sparse/B&B paths used **14.3% / 11.4% / 37.0% more aggregate CPU**. None was faster on either paired input. Both failed and fallback work, including cleanup and decisions, are inside the timing boundary.

These are query-level interruption tests. They do not claim partial sparse-frontier continuation or recovery inside the unchanged native generator.

## 63 — Full-grid tree reuse reversed the earlier small-sequence result

Eight matched cases, including two H256 extensions, were solved at every integer observation. Each point method made **904 solves**. Cold B&B visited 9,968 bound nodes; incumbent-only reuse visited **6,136**; retained terminal partitions visited **17,529**. Retaining partitions increased the amount of repricing work as the sequence grew.

On the two-case repeated H64 subset, cold/incumbent/tree CPU was **0.124359 / 0.101439 / 0.197052 seconds**. Incumbent reuse saved **18.4%**, winning both paired cases. Partition reuse cost **58.5% more than cold**, losing both. This diverges from experiment 52's smaller 17-point comparison, where partition reuse helped. The newer B&B oracle also uses an exact lexicographic tie encoding, so the difference is not a clean sequence-length-only intervention.

Point DP took **0.127489 seconds**; real-curve DP took **0.017940**, or **85.9% less**, winning both paired inputs with the same underlying oracle. Across the eight headline cases, the curve used **82 solves** instead of 904.

Two additional tree trajectories forced a later output-partition cap at t=1. Both retried cold and completed all 130 observations in total. This is a controlled exact reference implementation; production SCIP remains unavailable. Do not transfer these timings to SCIP.

**Decision:** incumbent reuse remains useful. Retained partitions should be subject to a cost/size decision rather than accumulated unconditionally.

## 64 — Larger external proofs worked, with explicit scope limits

The unchanged pinned official VIPR checker accepted **24 valid point certificates** and rejected **24 deliberately false final bounds**. The certificates totaled **205,182 bytes and 2,956 derivations**. Aggregate native/adapter/checker CPU was approximately **0.0184 / 0.0847 / 0.4492 seconds**; valid-check subprocess wall time was measured separately.

Eight bundles paired the same packing's exact endpoint proofs over real intervals. Only **12 integer observations**, counting shared endpoints separately, lay inside these early intervals: several useful real intervals were shorter than one integer step. That is evidence about this selected subset, not proof of broad integer-time savings.

The connector rejected **16 explicit scope violations**: varying feasibility, nonlinear objectives, a different domain, or different endpoint packings. These are model/metadata validation tests. The connector assumes the stated trajectory model is truthful; it cannot infer hidden constraint changes from two point proofs. VIPR certifies the original binary knapsack points without presolve. Neither VIPR nor our Python adapter/interval connector is claimed formally verified.

## 65 — The frozen gate transferred well on some large-weight cases

All three methods completed eight fresh 16/24/40-item trajectories at H256/H1024, including power slopes and large integer weights. The real gate made **145 oracle calls**; the integer gate made **136**. Integer queries still performed more DP work: **665,840 transitions versus 511,836**, while using fewer B&B nodes (118 versus 1,264). Fewer total calls did not imply less total cost.

On the four H256 timing cases, real-gate / integer-gate / normalized-dense CPU was **0.144436 / 0.160577 / 3.758273 seconds**. Real gating reduced dense aggregate CPU by **96.2%**, but won only **two of four paired inputs**: savings were concentrated in the large-weight cases. Integer gating used **11.2% more aggregate CPU than real gating**, with two paired wins out of four.

No transfer outcome was used to revise the gate. The H1024 cases are headline exactness/transfer checks; the reported repeated timing subset uses H256.

The 24-item wide/power regime pairs share each seed's base profit and unscaled weight draw before their differing slope/weight transformations. They are dependent trajectory records, not independent random samples.

## What this changes

The strongest practical direction remains established parametric optimization with an appropriate exact oracle. Normalize weights before choosing a capacity-based representation. Dense DP remains strong for small normalized capacities; exact B&B can avoid huge dense arrays; sparse storage needs an explicit state limit. Solver selection remains instance-dependent.

Keep the earlier cached certificate queue as a maintenance option. Neither integer-only bisection nor retaining every old search partition should be assumed to improve performance. A production reoptimization baseline and genuinely difficult large-capacity cases remain useful future comparisons.

These are finite, small, machine-local benchmarks of known methods. Three repeats and small timing subsets do not establish statistical confidence or universal speedups. Paired wins use each input's own repeated median, while aggregate rankings use medians of repeated sums. Counts of DP transitions, B&B nodes, sorted terms and retained states have different units and are not interchangeable CPU or memory bounds.

## Evidence

[Roadmap](Roadmap.md), [protocol](Protocol.json), [inputs](Inputs.json), [source/dependency seal](Freeze.json), [worker summaries](Path-results.json), [summary](Summary.json), [execution receipt](Execution.json) and [final audit](Final-audit.json) record the ten comparisons. [Recovery instructions](REPRODUCE.md) explain the complete archive and independent checks. All prior campaigns remain unchanged; no novelty, application impact or general complexity improvement is claimed.
