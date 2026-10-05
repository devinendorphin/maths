# Experiments 66–75: prospective roadmap

Parent: 160c020d345ab3b8afbd08d05ee7b3a93394cf32 (experiments 56–65). All inputs, method lists, caps, thresholds and timing subsets are frozen before execution. These are evaluations of known exact knapsack/parametric methods; no novelty claim.

| Experiment | Question | Fixed comparison |
|---|---|---|
|66|Does removing the sparse branch improve the old gate?|Old gate / normalized dense-or-B&B gate / B&B / dense on small and large weights, n12/20.|
|67|What does larger exact arithmetic cost without changing the optimum?|Multiply all profit intercepts and slopes by 1, 2^128, 2^512 on matched draws; dense and B&B.|
|68|Are degenerate ties handled soundly?|Six crafted tied, zero, negative and exact-boundary trajectories; oracle lexicographic checks and primary-optimal emitted answers.|
|69|Does the earlier tree-reuse reversal survive matched controls?|Same current B&B kernel and two draws, H16/64/256, cold / incumbent / full partition.|
|70|Can a fixed size ceiling avoid expensive partition reuse?|Retain partitions of at most eight terminal cells; otherwise incumbent only, against both unrestricted alternatives.|
|71|Does an integer crossing guess outperform midpoint bisection?|Real recursion / integer midpoint / clamped floor intersection; matched H64/1024 and subinteger fixture.|
|72|How does capacity change performance?|Fixed item draws with capacities 1/8, 4/8, 7/8 total weight; dense / sparse / B&B. Feasible sets intentionally differ.|
|73|Do correlated profits expose weak spots?|p=w, large coprime-like weights and tiny signed slopes, n16/20; prospective resource caps, dense / B&B / gate.|
|74|Can checked bounds be reused at shared endpoints?|All positive-length optimal intervals on three n8 cases; fresh endpoint proofs versus time-keyed bound reuse plus exact packing feasibility/value checks. Official VIPR and explicit scope mutations.|
|75|Do the fixed new rules transfer?|Eight fresh n12/20/24/40 trajectories, small/large weights; old/new gates, midpoint/crossing integer and B&B. No retuning.|

Three rotated sequential timing repeats on declared subsets; incomplete runs cannot win comparisons. Mathematical audits are outside timing and cannot influence solver decisions. 67,69,71 share matched draws; 72 shares items. Transfer inputs are separate stage-seeded draws. Memory reports are state/partition proxies, not peak RSS. Proof generation/translation/check costs are components from single sweeps, not a repeated speed benchmark.

Limits and exact boundary conventions are in Protocol.json. All completed queries, integer observations and interval endpoints receive independent enumeration/layer checks; full worker re-audit and fresh replication follow. Detailed evidence stays in the verified Drive archive; compact sources and summaries go to GitHub.
