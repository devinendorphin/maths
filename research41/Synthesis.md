# Experiments 41–45: findings

All five experiments completed. Every policy path reached its declared end,
and every completed or stopped frontier construction passed the independent
proof checks. The tests cover **105 distinct inputs, 72 construction workers,
306 headline paths, 96 development timing paths and 288 held timing paths**.
Across the 690 policy workers, **121,746 integer-time answers** were checked
against an independent capacity dynamic program. Logical repeats matched.

## Plain-language interpretation

The gate is a quick estimate of whether building a larger reusable proof
looks affordable. A rolling window builds a proof for just the next stretch
of mathematical time, then builds another. The new tests show that choosing
when to build can help, but repeatedly rebuilding still has a cost.

1. **41 — Broader inputs make the gate meaningful.** Indexed pruning finished
   all 24 inputs; same-slope pruning finished 20 and unpruned construction 18.
   The other builds stopped at the declared cap and their partial proofs were
   audited. Thresholds 2,000 and 5,000 accepted none; 15,000 accepted 6 of 24.
   Thus the high threshold produces both acceptance and rejection on this
   sample, unlike the vacuous core gates in experiment 39.
2. **42 — A gate gave a small held-case improvement.** Development selected
   indexed construction with threshold 15,000. It accepted 4 of 16 held inputs
   and rejected 12. On the eight-input repeated timing subset, the median
   aggregate CPU was 3.9% below scalar maintenance. The advantage
   came mainly from the block-slope cases. This is evidence on a small local
   sample, rather than a general performance guarantee.
3. **43 — Growing windows reduced repeated work, but did not repay it.**
   Doubling windows used 32.2% fewer aggregate raw proof rows
   than fixed 32-step windows on the sixteen held inputs. On the repeated
   eight-input timing subset they used 30.9% less CPU. Full-window
   indexed construction was still faster, and scalar maintenance was fastest.
4. **44 — Stopping a rebuild was safe at the tested boundaries.** All 18 paths
   returned correct answers, including strict loss one step before, exactly
   at, or one step after a join. All nine deliberate second-build failures
   remained inactive. Six needed stale scalar proof repricing; three had just
   received a fresh native proof at the join and used that directly.
5. **45 — The improvement did not transfer automatically.** Applying the same
   gate to doubling windows on fresh inputs used 8.5% more median
   aggregate CPU than maintenance on the timing subset. Of sixteen held
   inputs, four were normalized controls, two accepted construction, and ten
   rejected it. The normalized controls correctly bypassed construction.

## Repeated held timing

Values below are median sums of CPU seconds over the same eight held inputs,
from three sequential repeats. They exclude serialization and independent
audits, but include native construction, cleanup/disposal, gate arithmetic,
proof construction, maintenance and driver bookkeeping. Mathematical time
runs to 64 in 42 and 256 in 43/45; these are not durations in seconds.

| Experiment | Maintenance | Full indexed | Other policy | Selected/composed |
|---|---:|---:|---:|---:|
| 42 | 0.134089 | 0.222625 | same-slope 0.338548 | gate 0.128876 |
| 43 | 0.093432 | 0.182472 | fixed window 0.445442 | doubling 0.307643 |
| 45 | 0.071601 | 0.165993 | doubling 0.248008 | gate + doubling 0.077676 |

Timing differences of a few milliseconds require caution. The exact
per-repeat totals, gate decisions, row counts and logical signatures are
available in `Summary.json`, `Selection.json` and `Path-results.json`.
Headline row counts refer to sixteen held inputs; timing totals refer to
eight, so the table does not mix their denominators.

## Relationship to 36–40

These results agree with the regenerated 36–40 findings that smaller local
proofs do not necessarily lower overall CPU, and that indexed pruning is
useful on broad slope ranges. The meaningful gate choices and lower cost
of growing windows are new finite-sample findings. The failed transfer in
45 shows why the development result should not become a universal rule.
The old lost 36–40 archive remains unavailable; comparisons with it are
limited to retained reports. No input/mask byte identity with it is claimed.

## Evidence and limits

Caps and deterministic inputs were frozen before the run. Selection used
eight development inputs only and was sealed before held computation.
The deterministic boundary fixtures also served as pre-freeze implementation
smoke checks; they were not used to tune the gate. All detailed proof objects
and worker audits are archived in Drive, with content-addressed deduplication.

One reporting-only repair added a missing `defaultdict` import after all
workers finished and preserved the original freeze reference in the selection
seal. `Freeze-original.json` and `Implementation-amendment.json` document it.
No policy computation, input, cap or selection rule changed.

This campaign concerns exact integer parametric knapsack on these samples.
It proves correctness of the recorded computations, not a new theorem about
all instances. Negative performance findings are part of the result.
