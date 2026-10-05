# Rebuilt temporal-proof experiments 36–40

832 declared unique trajectories and 3328 headline policy paths were attempted. This consists of 640 core trajectories and 192 separate stress trajectories. Timing and selector tuning are separate from unique-case counts.

Incomplete trajectories: 0. Incomplete abandoned frontier constructions: 40. Completed scalar fallback never completes the abandoned proof.

| Stage | Held trajectories | Policy | Complete windows | Candidate evaluations | Raw proof rows | Incomplete builds |
|---|---:|---|---:|---:|---:|---:|
| 36 | 96 | maintain | 96 | 1123895 | 0 | 0 |
| 36 | 96 | unpruned | 96 | 0 | 121728 | 0 |
| 36 | 96 | same | 96 | 0 | 56962 | 0 |
| 37 | 96 | maintain | 96 | 629135 | 0 | 0 |
| 37 | 96 | unpruned | 96 | 0 | 122843 | 0 |
| 37 | 96 | same | 96 | 0 | 56764 | 0 |
| 37 | 96 | naive | 96 | 0 | 37819 | 0 |
| 37 | 96 | indexed | 96 | 0 | 37819 | 0 |
| 38 | 240 | maintain | 240 | 1977297 | 0 | 0 |
| 38 | 240 | unpruned | 240 | 31521 | 8146561 | 18 |
| 38 | 240 | same | 240 | 30561 | 5502512 | 12 |
| 38 | 240 | indexed | 240 | 0 | 228312 | 0 |
| 39 | 96 | maintain | 96 | 1069529 | 0 | 0 |
| 39 | 96 | unpruned | 96 | 0 | 118286 | 0 |
| 39 | 96 | conservative | 96 | 0 | 118286 | 0 |
| 39 | 96 | selected | 96 | 0 | 57114 | 0 |
| 40 | 96 | maintain | 96 | 3951995 | 0 | 0 |
| 40 | 96 | unpruned | 96 | 0 | 116249 | 0 |
| 40 | 96 | selected | 96 | 0 | 58685 | 0 |
| 40 | 96 | rolling | 96 | 0 | 82037 | 0 |

| Stage/subset | Median aggregate full algorithm CPU, seconds |
|---|---|
| 36/development | maintain: 0.239137, unpruned: 0.048937, same: 0.028472 |
| 36/held | maintain: 0.659682, unpruned: 0.045942, same: 0.024748 |
| 37/development | maintain: 2.686769, unpruned: 0.046976, same: 0.028409, naive: 0.066013, indexed: 0.045390 |
| 37/held | maintain: 0.604675, unpruned: 0.050394, same: 0.029431, naive: 0.060950, indexed: 0.040914 |
| 38/development | maintain: 2.114794, unpruned: 0.255738, same: 0.209857, indexed: 0.105807 |
| 38/held | maintain: 1.154827, unpruned: 0.273224, same: 0.209561, indexed: 0.128303 |
| 39/development | maintain: 0.451811, unpruned: 0.035564, conservative: 0.037736, selected: 0.022817 |
| 39/held | maintain: 0.245637, unpruned: 0.044792, conservative: 0.044329, selected: 0.026202 |
| 40/development | maintain: 9.381997, unpruned: 0.044250, selected: 0.025970, rolling: 0.085863 |
| 40/held | maintain: 2.432140, unpruned: 0.042500, selected: 0.023975, rolling: 0.068360 |

The 1,152 declared timing workers and 216 stage-39 tuning workers are archived separately. Each timing worker is isolated and pays for its own cold native initial/replacement solves. The held timing subset uses only the first held seeds. Results sharing weights/profits/directions/capacities are dependent paired observations.

Modeled time is the integer parameter of p+t*v. CPU is execution cost. Strict optimality loss means a feasible packing beats the incumbent; scalar certificate expiry can happen sooner without any switch. Proof width counts saved recurrence and auxiliary records. Preparation and rolling reconstruction must repay their debt separately in each counter and CPU; unlike counts are never added into a synthetic speedup.

[Comparison with the retained prior reports](Comparison.md) records both matching and differing aggregates. The prior detailed 36–40 evidence remains unavailable. New sources, immutable inputs/policy/construction/event records, independent range audits, timings, counters and exact cursors are retained here. The original 31–35 checkpoint remains unchanged as an explicit byte-identical repository reference.

These are exact parametric integer-knapsack experiments motivated by questions about Allen Brooks’ “numbers with time built in.” They do not reconstruct unpublished mathematics or authenticate a breakthrough. No new arithmetic is claimed.
