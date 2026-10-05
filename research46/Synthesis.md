# Experiments 46–50: findings

All five experiments completed. The 1,020 independently audited workers
cover 110 distinct input records: 444 headline paths, 216 development timing
paths and 360 held timing paths. Every policy reached its declared end, and
**261,852 integer-time answers** agreed with a separate
capacity dynamic program. Every logical repeat matched.

## What the five experiments found

1. **46 — Size estimates do not encode temporal pace.** On all sixteen
   matched slope-scaling pairs, multiplying slopes by eight left the old
   gcd-adjusted gate bounds and decisions unchanged. The underlying eight
   item/seed groups were held fixed while slopes and observation horizons
   varied. The repeated matched condition timings below show the actual
   costs; the old gate used 73.9% more median aggregate CPU than maintenance; 1 of 8 paired inputs faster across the eight
   timing variants. These are two independent seed/item groups with four
   variants each on the timing subset, not eight independent random draws.
2. **47 — A wider gate helped, but the pace filter was not selected.** Development chose
   `{"method": "indexed", "threshold": 30000}` from five declared candidates.
   On sixteen held inputs it accepted 7
   and rejected 9. On the eight-input
   repeated subset it used 8.5% less median aggregate CPU than maintenance; 5 of 8 paired inputs faster. The older gate
   used 8.7% less median aggregate CPU than maintenance; 6 of 8 paired inputs faster. Choosing the never-build option is
   allowed and still pays feature/gate arithmetic.
   The two pace filters changed the development decisions, but neither beat
   the plain 30,000 threshold on the declared selection criterion. These
   finite samples do not establish a benefit from adding the pace estimate.
3. **48 — Stop-renewing thresholds expose construction debt.** Development
   selected threshold **0**; zero means never build. The fixed
   4,000-operation rule stopped 12
   renewals on sixteen held inputs and used 20.1% less median CPU
   than unconditional doubling windows. Against maintenance it used
   167.3% more median aggregate CPU than maintenance; 0 of 8 paired inputs faster. The selected rule used
   5.9% more median aggregate CPU than maintenance; 5 of 8 paired inputs faster. The initial build and fallback proof
   repricing are included in CPU. A threshold checks past construction work
   before the next build; it is not a strict bound on the total cost already paid.
4. **49 — Later forced failures remained safe.** All sixty paths had the
   three intended strict-loss switches. Fifty-four forced failures cover
   entries, index and auxiliary guards, at each of the second, third and
   fourth constructions. Every partial construction was audited and stayed
   inactive. There were 36 stale
   scalar proof reprices across the forced paths. Tie times and window joins
   are included in the integer-time checks.
5. **50 — Transfer was tested without retuning.** Fresh 16/20-item inputs
   were observed through mathematical time 512. The composed rule used
   1.8% less median aggregate CPU than maintenance; 4 of 8 paired inputs faster; the transferred input gate alone used
   0.2% less median aggregate CPU than maintenance; 3 of 8 paired inputs faster. Of twenty-four headline inputs,
   6 were normalized controls and correctly
   bypassed construction. The composed gate accepted
   3 non-normalized inputs and rejected
   15; a selected zero renewal threshold can
   still prevent building after gate acceptance.
   Here the selected zero threshold prevented **every composed construction**.
   The small CPU difference from maintenance cannot be credited to an active
   combination of gate and rolling proofs: it performed maintenance plus
   extra gate decisions, with ordinary timing variation.

## Repeated held CPU

Each number is the median of three sums over the same eight inputs per
experiment. CPU includes gates, renewal decisions, native solves,
cleanup/disposal, construction, scalar maintenance and driver bookkeeping.
It excludes input decoding, serialization and independent auditing. A ratio
below one is faster than maintenance on that finite subset. Paired wins use
each input's own three-repeat median, which differs from aggregate ranking.

| Experiment | Policy | Median CPU seconds | Ratio to maintenance | Paired wins |
|---|---|---:|---:|---:|
| 46 | indexed_full | 0.289684 | 5.514 | 0/8 |
| 46 | legacy_gate | 0.091359 | 1.739 | 1/8 |
| 46 | maintain | 0.052538 | 1.000 | 0/8 |
| 47 | feature_gate | 0.151563 | 0.915 | 5/8 |
| 47 | indexed_full | 0.286162 | 1.727 | 5/8 |
| 47 | legacy_gate | 0.151331 | 0.913 | 6/8 |
| 47 | maintain | 0.165672 | 1.000 | 0/8 |
| 48 | adaptive | 0.311436 | 3.345 | 0/8 |
| 48 | budget_fixed | 0.248897 | 2.673 | 0/8 |
| 48 | budget_selected | 0.098587 | 1.059 | 5/8 |
| 48 | maintain | 0.093113 | 1.000 | 0/8 |
| 50 | composed | 0.411613 | 0.982 | 4/8 |
| 50 | feature_gate | 0.418115 | 0.998 | 3/8 |
| 50 | indexed_full | 0.406700 | 0.970 | 4/8 |
| 50 | maintain | 0.419129 | 1.000 | 0/8 |

## Matched pace/horizon conditions in 46

Each condition is a median sum over two inputs (12 and 16 items), from three
repeats. Scaling slopes changes which integer times correspond to the same
continuous objectives; it does not create new independent item draws.

| Condition | Maintenance CPU | Full indexed CPU | Old gate CPU |
|---|---:|---:|---:|
| H64-scale1 | 0.019142 | 0.073627 | 0.029499 |
| H64-scale8 | 0.006199 | 0.066581 | 0.015351 |
| H256-scale1 | 0.020197 | 0.072967 | 0.030659 |
| H256-scale8 | 0.007011 | 0.072354 | 0.017633 |

## Interpretation and evidence

These results extend the 41–45 observation that a reusable proof may save
later maintenance but must first repay construction and renewal costs.
The pace estimate is a heuristic, not a proven profitability condition.
The operation threshold adds determinism to renewal decisions but does not
turn operation counts into equivalent CPU costs. No held-case timing was
used to tune either rule. A selected rule may be less effective after transfer.

Inputs, algorithm sources, caps and roadmap were frozen before training.
Both development selections were sealed before any held worker ran. Smoke
checks used disjoint implementation fixtures. Detailed native/scalar proofs,
repair events, complete or capped frontiers, accounting and independent audits
are in the Drive archive linked by `Archive-storage.json`. Content addressing
stores repeated proof objects once. An interrupted worker restarts cold;
there is no claim of within-action continuation.

All native temporary stores were empty after cleanup/disposal. Independent
checks replay recurrence, deletion and index records; verify scalar covers,
prices, repairs and horizons; and recompute gates and renewal decisions.
The audit-only capacity DP never chooses a policy or supplies a proof to it.

The stage-50 normalized controls are separated in `Summary.json`. Small CPU
differences and three machine-local repeats do not establish statistical
confidence or a universal speedup. Headline denominators are 32 inputs in
46, 16 held inputs in 47/48, 6 chain inputs in 49, and 24 in 50. Timing
denominators are eight per timed stage. Ten conditions on each chain are
dependent views of the same input.

This is exact integer parametric knapsack on the declared finite inputs.
The old lost 36–40 detailed archive remains unavailable; no byte-level
comparison or recovery of that run is claimed.
