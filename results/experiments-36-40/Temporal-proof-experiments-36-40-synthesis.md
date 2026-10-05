# Temporal-proof experiments 36–40

All five declared matrices were attempted and audited: **832 fresh trajectories** (640 core and 192 separate stress) and **3,328 headline policy paths**. 3,328 policy trajectories completed their observation windows; 0 paths remain incomplete. **40 frontier constructions remain incomplete after frozen guards**; successful scalar fallback does not complete those proofs. Exact construction and path cursors are in Resume-cursors.json. No cap was raised.

| Experiment | Held trajectories | Finding | Limit |
|---|---:|---|---|
| 36 | 96 | Unpruned / same-slope: 122,000 / 57,581 raw reduced proof rows; 57,509 same-slope checks. | All-time completion proof preserves global optima; width can still be exponential. |
| 37 | 96 | Naive / indexed: 1,369,626 endpoint comparisons / 200,961 index visits; retained sets matched in all 96 held cases. | Different operation units; both certify only [0,256]. |
| 38 | 240 | 96 core + 144 stress. Held capped constructions: unpruned 18, same 12. | Stress powers remove slope collisions; caps are unfinished builds, even with completed fallback. |
| 39 | 96 | Sealed same gate, E threshold 50,000; selection used only the eight-case development grid. | Bounds count rows/transitions, not CPU, index records or native search. |
| 40 | 96 | All methods observed 0–1024; rolling used 216 later-window rebuilds. | Each window restarts the original recurrence; interval proofs do not carry discarded states forward. |

Stage 40 retained raw-row savings even after all four windows: 81,056 rolling rows versus 116,145 all-time unpruned rows on held-out data (first window: 38,948). Rolling nevertheless had greater unique-case CPU in 70 of 96 pairs, and higher median aggregate CPU in both declared timing subsets. The 70-case count is descriptive; repeated subset timing supports only those subsets.


The all-time same-slope argument is elementary: a lighter state with equal slope and no smaller intercept admits every identical remaining completion. Endpoint dominance uses a different argument: an affine difference nonnegative at both endpoints stays nonnegative throughout that interval. Complete transition domains, predecessors, deletions, signed Fenwick aggregates, scalar covers, strict crossings, native objectives and window joins were independently checked. Whole-domain streaming audits and original-profit capacity DP stay outside algorithm decisions.

| Stage and timing subset | Median aggregate full CPU, seconds |
|---|---|
| 36 development | maintain: 0.206815, unpruned: 0.033401, same: 0.025152 |
| 36 held | maintain: 0.502229, unpruned: 0.032727, same: 0.023671 |
| 37 development | maintain: 1.745121, unpruned: 0.029767, same: 0.022887, naive: 0.030621, indexed: 0.025962 |
| 37 held | maintain: 0.513333, unpruned: 0.034209, same: 0.023425, naive: 0.030590, indexed: 0.027670 |
| 38 development | maintain: 1.621661, unpruned: 0.150454, same: 0.140897, indexed: 0.068796 |
| 38 held | maintain: 0.744049, unpruned: 0.167187, same: 0.143333, indexed: 0.079450 |
| 39 development | maintain: 0.425981, unpruned: 0.028212, conservative: 0.031079, selected: 0.021612 |
| 39 held | maintain: 0.143606, unpruned: 0.033916, conservative: 0.034634, selected: 0.025071 |
| 40 development | maintain: 4.920642, unpruned: 0.031371, selected: 0.025031, rolling: 0.052781 |
| 40 held | maintain: 1.754930, unpruned: 0.029720, selected: 0.023027, rolling: 0.042557 |

These are three repetitions on the exact declared subsets: eight core cases per split, plus eight half-capacity stress cases for stage 38. Held timing uses only the first held seeds. The 1,152 timing workers and 216 stage-39 tuning workers are separate from unique-case headline counts. Each worker includes its own cold initial/replacement native solves, construction and maintenance. Imports/decoding, serialization and independent audits are separate. Capped repetitions would be ineligible; no fastest repetition or per-held-case winner is selected. Shared weights/profits/capacities make these dependent paired observations, not independent trials.

Stage 39’s complete candidate grid and rejected candidates are archived. Gate acceptance/rejection, bound conservatism and retrospective audit-only “could have accepted” descriptions are in Gate-diagnostics.json. The selected seal was carried byte-identically into stage 40. All four thresholds accepted every non-normalized core case (72 accepted and 24 normalized in each held-out gate). No failed build was avoided on this matrix. Timing differences between thresholds with identical decisions do not establish a uniquely useful cutoff.

Modeled time is the objective parameter. CPU is execution cost. True loss means a feasible packing strictly beats the incumbent; scalar certificate expiry can happen sooner while the packing remains optimal. Proof width counts stored recurrence and auxiliary states. Preparation and repeated reconstruction have to repay their debt separately in candidate evaluations, DP rows/transitions, index visits and CPU. None of those unlike counters is added into a synthetic speedup. Small envelopes and zero scalar renewal evaluations do not imply a generally efficient optimizer.

Evidence qualifications: two stage-36 mutable audit views retained earlier prefixes; only missing audit ranges were continued, with immutable per-range records added. A native-price audit correction allows equally minimal native price representations while retaining scalar repair’s exact tie checks. Prior sources/hashes and saved evidence remain. An early fixture accounting attempt failed before the unique experiments; its attempted records are retained and its invalid CPU is not used. Driver/ledger bookkeeping and final record handling are separate reconciled CPU components. Partial builds remain inactive proofs; their completed prefix audits are preserved.

This is exact parametric integer-knapsack research motivated by questions about Allen Brooks’ “numbers with time built in.” It neither reconstructs his unpublished mathematics nor authenticates a breakthrough. **No new arithmetic is claimed.**
