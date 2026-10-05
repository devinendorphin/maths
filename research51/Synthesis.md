# Experiments 51–55: findings

The bounded batch completed its mathematical comparisons: **422 audited workers on 27 input records**, plus 325 native point-solve controls and 19 external VIPR checks. There were **21,942 integer-observation checks** and **22,043 rational-oracle, tie or certificate-horizon checks**. All stored mathematical audits passed. After correcting a post-run fingerprint that accidentally included elapsed wall time, all logical repeats matched. Frozen algorithms, inputs and original worker evidence were preserved.

The literature-informed exact baseline is the strongest result. It substantially reduced ordinary solve calls on these inputs. Queue-based certificate dispatch also reduced maintenance work. The production SCIP comparison remains outstanding; experiment 52 is a controlled exact reference implementation.

## 51 — Established exact parametric optimization was useful

The Eisner–Severance-style endpoint/intersection recursion used **187 capacity-DP oracle calls**, compared with **1,755** calls at all integer observations on the same 27 inputs. It performed 151,498 DP transitions versus 1,142,570. It discovered 104 positive-length real-parameter pieces; some inputs had more real pieces than distinct packings observed on the integer grid.

On the declared six-input timing subset, its median aggregate CPU was **0.008466 seconds**, versus **0.039693 seconds** for repeated solves with the same DP oracle: **78.7% less**, faster on all six paired inputs. This is the cleanest comparison because the oracle kernel is shared.

Original scalar maintenance and indexed frontiers took 0.104223 and 0.104275 seconds on that subset. The parametric DP was about 91.9% cheaper there, but those comparisons combine the parametric strategy with a different optimizer kernel. They do not isolate proof reuse. All original indexed constructions completed under the existing caps.

The 18 fresh held inputs used 129 parametric calls versus 1,170 point calls. Four retrospective trajectories, truncated to H64, used 40 versus 260; the five crafted boundary fixtures used 18 versus 325. Retrospective trajectories are not new independent draws. Native point solves were additionally checked on all five fixtures without mixing their timings into the DP-oracle ratio.

**Decision:** use this established exact method as the first full-trajectory baseline. Stop further frontier gate tuning until it beats or complements this comparison. This is an implementation of a known approach, not a claim to have reproduced Eben-Chaime's specific algorithm.

## 52 — Retaining search helped in a controlled implementation

All three exact branch-and-bound modes solved 17 fixed time points on 23 fresh/boundary inputs, or 391 solves per mode. The rational fractional-knapsack bound, root heuristic and branching rule were identical. The tree mode retained the terminal domain partition, repriced every old domain for the new objective, and refined domains when necessary. It did not reuse old objective-dependent bounds unchecked.

Across headline trajectories, cold solves visited 3,125 bound nodes; incumbent-only reuse visited 2,847; partition reuse visited 2,868. Partition reuse therefore did not always minimize node count. It reduced the number of sorted positive item terms from 20,189 cold / 18,889 incumbent-only to 15,776.

Repeated median CPU was **0.028054 / 0.025398 / 0.021008 seconds** for cold / incumbent / partition reuse. Partition reuse was **25.1% cheaper than cold**, with four paired wins out of six. Incumbent-only reuse was 9.5% cheaper in aggregate, with two paired wins.

**Limit:** SCIP and PySCIPOpt were unavailable and the shell download proxy refused connection. These results concern our small exact reference implementation, inspired by the established reoptimization literature. They establish no production SCIP speedup or exact-mode/reoptimization compatibility. The 17-point solve sequence also has a different output requirement from the 65-observation full trajectories in 51/53; their CPU totals should not be ranked as equivalent tasks.

## 53 — Event scheduling saved repeated horizon work

The queue and rescan drivers used identical selective repair rules. Across 27 headline trajectories, both processed **588 internal failure events**, involving **934 expired cells**, and **63 strict packing changes**. Both performed exactly **11,104 repair-bound evaluations**. This shows the comparison preserved the underlying repair work.

Rescanning calculated 5,107 cell horizons and 28,956 bound evaluations inside those calculations. Caching failure times reduced these to **1,500 horizons and 7,469 evaluations**, reductions of 70.6% and 74.2%. The queue performed 1,265 pushes and 934 pops. Reset and retained-state handling are included in CPU.

Repeated median CPU fell from **0.083392 to 0.050673 seconds**, or **39.2%**, with six paired wins out of six. The queue reduces scheduling overhead; it does not make the same expensive repairs disappear. Internal failure events outnumbered actual answer changes by more than nine to one on this set.

Two additional chain paths forced an initial indexed construction to stop after one transition. Both partial proofs remained inactive and queue maintenance completed correctly. These are initial partial-build tests; the later-build failures and rolling joins exercised in experiment 49 were not repeated here.

**Decision:** retain cached failure scheduling as a candidate maintenance implementation. Compare selective versus whole-partition repair separately before attributing their combined difference to the queue alone.

## 54 — Existing proof infrastructure worked

The unchanged official VIPR checker was fetched at commit `30f2951d1e90e47afa821bdd1b12b82246656c42` and compiled with the installed GMP libraries. Its source blob matched `1019746a35d6d168e6c4820a28847ac92b6518ec`. No SCIP, presolve or SoPlex transformation was involved.

The adapter exported the original binary knapsack, explicit variable bounds, rational linear combinations, integer rounding and branch-assumption discharge. VIPR accepted **19 of 19 valid certificates** and rejected **19 of 19 certificates whose final claimed bound was made strictly false**. The valid certificates totaled **34,138 bytes and 495 derivations**. Aggregate source/adapter/checker CPU was approximately 0.0029 / 0.0079 / 0.0855 seconds. Checker subprocess CPU and wall time were measured separately from Python.

Four chain pieces and three pieces of an eight-item fresh trajectory yielded **seven interval bundles** with two endpoint proofs each. The same feasible packing appeared at both endpoints; 91 integer observations, counting shared endpoints per bundle, agreed with the independent oracle. For any other fixed feasible packing, its objective difference from the chosen packing is affine, so nonnegative endpoint differences imply nonnegative differences throughout the interval. This certifies the real interval too, under fixed feasibility and affine objectives.

**Decision:** point proof production need not require another custom general checker. Endpoint bundles offer a small route to interval certification in this model. VIPR was independently executed; it is not claimed formally verified. The adapter and affine interval connector remain ordinary Python code, and the checker was built with assertions enabled. These timings are not a direct verifier-speed comparison with our earlier audits.

## 55 — The cost guarantee needs its assumptions

The classical model has unit daily rental cost, a known fixed integer buy price B, and permanent free service after buying. The threshold policy rents B days and buys before another requested day. Its cost is T for T<=B and 2B otherwise. Hindsight costs min(T,B), so the policy costs at most twice hindsight for every horizon. **4,128** combinations of B=1..32 and T=0..128 satisfied the bound.

The recorded counterexample keeps a threshold based on a nonbinding quote of one while the actual purchase costs M. A concrete variable-price realization has prices 2M on day one and M on day two, with horizon two. The unchanged quote-based rule rents once and then pays M; hindsight rents twice for cost two when M>=2. The ratio (M+1)/2 is unbounded. The largest recorded example, M=65,536, has ratio 32,768.5. This is a failure of transferring a fixed-known-price theorem to a quote-based rule, not a theorem that every variable-price policy fails.

The real-input prototype allowed one full-horizon indexed probe with **256 transitions and 256 total index visits/updates**. Other bookkeeping, sorting and proof work was also charged; these two caps are not a total CPU cap. Four probes completed and 23 stopped safely with inactive partial proofs before cold queue maintenance. None exceeded the declared two work caps.

On the unrepeated 27-input headline sums, probing cost about **26.6% more than queue maintenance**, winning on four inputs. It cost about 8.9 times the parametric DP total and beat it on none. These are exploratory single-run totals, not repeated timing conclusions. The classical theorem does not bound this prototype's CPU, expiring proof costs, probes or renewals.

**Decision:** keep the simpler parametric baseline and queue maintenance. Do not add another construction gate on the basis of this batch.

## Repeated CPU summary

Each total is the median of three sums over the same six fresh non-normalized inputs. CPU includes solver work, decisions, cleanup, retained-state and output handling. It excludes JSON persistence and independent auditing. All times are machine-local and small; three repeats do not establish statistical confidence or a universal speedup.

| Experiment | Method | Median CPU seconds |
|---|---|---:|
| 51 | Exact parametric DP | 0.008466 |
| 51 | Point DP, same oracle | 0.039693 |
| 51 | Original scalar maintenance | 0.104223 |
| 51 | Original indexed frontier | 0.104275 |
| 52 | Cold exact reference B&B | 0.028054 |
| 52 | Incumbent reuse | 0.025398 |
| 52 | Terminal-partition reuse | 0.021008 |
| 53 | Selective repair with rescan | 0.083392 |
| 53 | Selective repair with queue | 0.050673 |

The inputs have small capacities and at most 20 items, with fresh draws at 8/12/16 items. Dense capacity DP may lose its advantage at much larger capacities. No general complexity improvement, application impact or novelty is established. Memory reporting uses state-count proxies and serialized proof bytes, not isolated peak RSS.

## Evidence and correction

[Protocol](Protocol.json), [frozen inputs](Inputs.json), [source seal](Freeze.json), [capabilities](Capabilities.json), [compact results](Path-results.json), [summary](Summary.json) and [final audit](Final-audit.json) make the comparisons reviewable. [Recovery and replication instructions](REPRODUCE.md) describe the complete archive and dependency snapshots.

The original campaign's final repeat fingerprint mistakenly included `algorithm_wall` in older policy results. It stopped after all workers, VIPR checks, cost cases and native controls had completed. [Finalization](tools/finalize.py) excludes clock fields, compares complete logical results, and records the correction in `Summary.json`. Twelve repeated logical groups were affected. No mathematical algorithm, input, worker record, policy choice or measured time changed. The original run log and failed fingerprint records remain in the archive.

The external SCIP baseline, broader scaling tests and formal verification of the interval connector remain outstanding. Those are better next priorities than another threshold sweep.
