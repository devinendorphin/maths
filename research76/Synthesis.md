# Experiments 76–85: findings

All ten bounded comparisons finished: **58 input records, 508 workers (220 headline and 288 timing), 461 complete trajectories and 47 resource-limit stops**. Every input has complete exact answers from at least one method. Ten of the stops were deliberately forced all-failed portfolio controls; the other 37 reached prospective node or terminal-storage caps. The record contains **136,012 integer-observation checks** and **18,759 oracle/interval-endpoint checks**, including repeats and shared proof endpoints rather than distinct observations. All stored audits and the full independent re-audit passed. A fresh replication matched all 508 worker statuses and logical signatures, including all 47 stopped runs, plus the proof counts and cache controls.

The central finding is that terminal history was only one B&B limitation. Removing it solved the retained storage-limited control, but difficult correlated inputs still reached node budgets. A fixed capped solver portfolio completed all fresh transfer inputs, while the simpler single-solver gates did not. Crossing-guided integer queries remained useful on ordinary cases, but constructed skewed chains exposed deeper splits and timings that did not track query counts.

The original execution phase, including its immediate audits, took **90.08 seconds** against a declared 900-second limit. Design, implementation, further verification and archiving were separate. Original timing data stays separate from any validation replica.

## 76 — Lean B&B removed the old storage stop, without becoming the fastest method

Four retained experiment 73 inputs and four fresh correlated 16/20-item cases compared stored B&B, lean B&B and normalized dense DP. The lean variant keeps the same exact lexicographic objective, fractional bound, initial greedy candidate and traversal order, but omits completed terminal cells and split traces. Its active stack remains capped, and every completed query is independently checked by enumeration plus a separate work-counter replay. It does not emit a reusable partition certificate.

Stored B&B completed **5/8**, stopping at the4,096-cell terminal-partition cap on three inputs. Lean and dense completed **8/8**. On the retained `73-n20-s1` control, stored B&B stopped after8,894 nodes during its first query; lean completed five queries and19,735 nodes, while dense used311,860 transitions. Across all eight inputs, lean's largest active stack was **12 cells**, with no stored terminal partition. This is a cell-count proxy, not peak RAM.

On the four seed-1 repeated controls, lean/dense CPU was **2.172577 / 0.675736 seconds**. Lean cost221.5% more, losing all four paired cases. Stored B&B's mixed aggregate is censored because only6/12 timing runs completed. **Decision:** dropping history resolves this representation limit, but bounded-capacity dense DP remains strong on these correlated cases. The retained controls are not fresh samples.

## 77 — Large-capacity correlated cases still reached B&B node limits

Six fresh 18/22/24-item correlated-profit inputs used profits equal to weights and small signed slopes. Lean B&B completed **1/6**; five stopped at the30,000-node query cap, despite a maximum active stack of only15 cells. Dense and the portfolio completed **6/6**, making19 successful curve queries each.

The portfolio normalizes each query. At normalized capacity>4,096 it first tries lean B&B with a3,000-node budget, then sparse DP, then dense DP, each with its declared limits. For smaller capacity it tries dense first. All abandoned work is charged; only a successful full query can certify an interval. These are different prospective method budgets, not a comparison under one interchangeable work unit.

Headline portfolio work included **17 abandoned attempts**,55,245 B&B nodes and1,517,224 DP transitions; direct dense used4,834,685 transitions. The fixed18/22-item seed-1 timing subset gave portfolio/dense CPU **0.913797 / 0.916456 seconds**, effectively tied in aggregate. Portfolio lost both per-input median comparisons; medians of sums can rank differently from sums of per-input medians. Lean's timing aggregate is ineligible because all six selected runs were capped. **Decision:** fallback improves completion coverage; no speed advantage over direct dense is established here.

## 78 — Constructed skewed chains exposed deeper crossing splits

Eight capacity-one16-item chains used geometric slope increments with crossings clustered near the beginning or end of H128/H1024. They were constructed algebraically before execution, rather than selected by searching measured outcomes. Every method completed. Integer midpoint/crossing/balanced crossing/real curve made **172 / 140 / 178 / 248 queries** across the eight inputs.

Ordinary crossing reached a maximum split depth of **15**, versus **10 midpoint**. The fixed central-quarter guard replaced56 crossing proposals and limited maximum observed depth to13, at the cost of38 more queries than ordinary crossing. The guard returns to the midpoint whenever the strictly interior crossing guess lies outside the central quarter. Integer rounding is explicitly checked; at very small widths strict interior progress is sufficient.

On the four H1024 timing controls, CPU was **0.003212 / 0.003450 / 0.003510 / 0.017026 seconds**. Crossing had fewer headline queries but7.4% more aggregate CPU than midpoint, winning only one paired case out of four. These are millisecond totals, so the timing difference is weak evidence. The exact deeper-split observation is stronger. **Decision:** crossing is not assumed to balance recursion or win every timing; guarding imbalance changes the work tradeoff.

## 79 — Balancing usually discarded helpful ordinary crossing guesses

Eight12/20-item records used matched H64/H1024 trajectories. All four query methods completed. Real/midpoint/crossing/balanced calls were **88 / 102 / 54 / 96**. Crossing's maximum split depth was5, midpoint10, and balanced11. Thus forcing central splits did not minimize actual depth on these inputs: endpoint equality can terminate a deliberately unbalanced branch cheaply.

On two H1024 seed-1 repeated inputs, real/midpoint/crossing/balanced CPU was **0.026021 / 0.022529 / 0.014784 / 0.024920 seconds**. Crossing used34.4% less than midpoint, winning both cases. Balanced used68.6% more than crossing, winning neither. Its46 headline replacements largely removed useful near-boundary probes. **Decision:** keep the balancing guard available for depth control; these ordinary inputs favor unguarded crossing.

## 80 — Query savings and CPU savings depended on the oracle

A fixed factorial comparison ran midpoint, crossing and balanced integer rules with both dense and lean B&B on the same four bounded inputs. Every method completed. For either oracle, query counts were **53 midpoint / 33 crossing / 48 balanced**. Independent audits confirmed identical optimal trajectories, without using audit results to select queries.

Dense transitions were **89,935 / 57,327 / 83,330**; lean B&B nodes **530 / 416 / 478**. Fewer calls did not imply proportional work savings because query times change how difficult individual B&B solves are.

On the two seed-1 timing inputs, dense CPU was **0.018458 / 0.018204 / 0.023368 seconds**; lean CPU **0.011325 / 0.009670 / 0.009471**. Crossing's aggregate saving versus midpoint was1.4% dense and14.6% lean, winning both paired cases for each. Balanced had fewer benefits in the dense implementation, while its lean aggregate was2.1% lower than crossing with only one paired win. These small subsets do not establish a universal oracle/query ranking.

## 81 — Multiple failed attempts remained inactive and were charged

Four correlated12/20-item controls compared the lean gate, normal portfolio, a portfolio forcing its first two attempts to stop after one node/transition, a portfolio forcing all three to stop, and direct dense. Lean gate, normal portfolio, forced-first-two and dense all completed. The forced-first-two path recorded **22 inactive attempts and11 successful queries** across the four headline cases. Their full fallback work remained inside timing.

All-failed headline controls recorded **12 inactive attempts and zero completed queries**, with no packing or interval output. Including repeats, these account for ten of the campaign's47 capped workers. A quick failure is not an optimization success and is excluded from speed rankings.

Repeated lean-gate/normal-portfolio/forced-first-two/dense CPU was **1.130899 / 0.417275 / 0.362791 / 0.321045 seconds**. Normal portfolio used63.1% less aggregate than the lean gate, with one paired win out of two, but30.0% more than direct dense, winning neither. The forced path cost13.0% more than direct dense. Its earlier interruption of expensive primary attempts made it cheaper than the normal portfolio on this selected subset; that is not a free or recommended general cancellation rule.

These are complete query retries under fixed budgets. They do not resume a partially built frontier or claim recovery inside a native proof generator.

## 82 — Checked bound reuse extended to10/12-item curves

Four fresh curves contained20 positive-length optimal pieces. Both sweeps externally proved every piece's endpoints and included two point controls per input. Fresh checking needed **48 point certificates**; context-keyed reuse needed **24**, serving24 additional endpoint references. Fresh/reused certificate bytes were **221,888 / 110,962**, derivations **3,480 / 1,740**, and valid-check CPU **0.375418 / 0.161306 seconds**.

These are single sweep component measurements, not a repeated end-to-end speed benchmark. The exact count reduction is the useful result. At a shared boundary, a checked optimum objective bound may support different feasible packings of that same value. Reuse separately checks each supplied packing's feasibility and objective; it does not assume adjacent interval packings match.

The cache now keys entries by the complete feasible-set digest (n, weights, capacity), affine-coefficient digest (profits, slopes), and exact rational time. Each source certificate proves the original binary problem without presolve, using the unchanged pinned official VIPR checker.

## 83 — Explicit cache-invalidation controls passed

Two new eight-item proof-backed inputs each tested 12 rejections: changed capacity, weights, intercepts, slopes, item count or time; negative/out-of-range/infeasible/suboptimal packing; an unchecked entry; and inconsistent stored-key metadata. All **24 rejected**. Same-model reuse and a changed human-readable case label produced **four valid hits** in total. Labels do not change the mathematical model.

The two cached proof sweeps additionally checked10 new point certificates and built eight complete interval bundles. Across 82 and 83 together, VIPR accepted **82 valid certificates** and rejected **82 deliberately false final bounds**. The record has48 interval bundles,116 endpoint references,335 interval integer checks (including repeated/shared endpoints), and60 explicit interval-scope rejections. Full re-audit regenerated every non-reused certificate, re-executed VIPR, checked every alias packing and verified continuous interval coverage.

These are explicit model/key/answer controls for a cache of trusted checked bounds. They do not establish resistance to adversarial corruption of an accepted objective value, concurrency safety, signed provenance, hidden model changes or formal verification. The cache and interval connector are ordinary Python, and the declared affine, fixed-feasible-set model must be truthful.

## 84 — Lean storage did not change node work on these easy sequences

Six10/14/18-item H64 full-grid sequences compared stored cold/incumbent and lean cold/incumbent optimization. All completed. Each method made **390 solves and visited1,399 nodes**. As in experiment 69, the initial greedy bound matched the useful strength of the old incumbent on these inputs, so carrying the old optimum saved no nodes.

Stored optimization retained up to18 terminal cells per query; lean retained none, with an active stack of at most6 cells. Repeated stored-cold/stored-incumbent/lean-cold/lean-incumbent CPU was **0.025141 / 0.027656 / 0.030076 / 0.027837 seconds**. Lean cold was19.6% higher than stored cold, with one paired win out of three. Lean incumbent was7.4% lower than lean cold, winning all three, despite identical node counts. The extra counters, control flow and small timing variation prevent interpreting that ratio as reduced search work. **Decision:** lean is a storage option; no general cold-solver speedup or incumbent-node saving is shown here.

## 85 — The portfolio was the only complete transfer rule

Eight fresh H128 trajectories covered large-weight12-item, correlated20-item, bounded24-item and40-item/capacity96 regimes. The old stored gate completed **6/8**; the lean real gate and both lean integer variants completed **7/8**. The portfolio completed **8/8**, including the correlated case where the other four methods stopped. It made83 successful queries with three inactive abandoned attempts.

The stored gate reached terminal-partition storage limits. One fresh correlated input needed more than the30,000-node budget for the lean gate and integer variants. The portfolio instead tried its3,000-node lean budget and recovered with sparse/dense optimization. Its headline work was12,156 B&B nodes and392,744 DP transitions; these different units are not added into a common work score.

On the four seed-1 timing inputs, only portfolio's complete mixed aggregate is eligible: **0.251065 seconds**, all12 runs complete. Every other method had only9/12 complete timed runs, so their aggregate timings cannot rank against portfolio's full solution coverage. The result supports the fixed fallback strategy's bounded robustness on this held set, not a universal speed claim. No thresholds or input choices were retuned from outcomes.

## Evidence and next direction

The full independent audit checked2,443 query splits across the workers, including447 balancing replacements, as well as every completed answer, work counter and stored partition recurrence. No emitted integer answer in this batch differed from the positive-side canonical optimum, although primary optimality is the real-curve endpoint contract.

These are finite machine-local evaluations of known algorithms. Three timing repeats on small subsets provide no statistical-confidence or application-impact claim.58 records include four retained controls, constructed chains and matched horizon variants, rather than58 independent draws. Storage counts are cell proxies, not simultaneous allocation bytes or measured peak RSS. There is still no production SCIP comparison, formal verification or general complexity improvement.

The useful continuation is a fixed capped portfolio, with direct dense optimization as a strong baseline for eligible capacities. Keep lean B&B to avoid unnecessary terminal storage, and unguarded crossing as an integer alternative whose imbalance is explicitly monitored. Future controls should separate portfolio budgets from oracle choices, test accepted-bound provenance independently, and add a production exact solver when available.

[Roadmap](Roadmap.md), [protocol](Protocol.json), [inputs](Inputs.json), [freeze](Freeze.json), [worker summaries](Path-results.json), [summary](Summary.json), [split metrics](Split-metrics.json), [storage metrics](Storage-metrics.json), [cache tests](Cache-tests.json), [verification](Verification.json), [replication](Replication-check.json) and [recovery](REPRODUCE.md) hold the compact review record. The [prior literature review](../research-notes/Literature-review-2026-10-05.md) and [66–75 findings](../research66/Synthesis.md) remain the context. Previous campaigns are unchanged.
