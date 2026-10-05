# Experiment 31: results

32 development and 96 held-out unique trajectories; all policy paths attempted and independently audited. Unlike work units remain separate. Full counters and paired common-time debt/payback are in Summary.json. CPU outside stage34 selection is descriptive; no held-out runtime advantage is claimed.

| Policy | Complete / 96 | Candidate evaluations | DP entries | DP transitions | Dominance comparisons | Switches | Charged CPU seconds |
|---|---:|---:|---:|---:|---:|---:|---:|
| maintain | 96 | 1,198,568 | 0 | 0 | 0 | 194 | 15.779576 |
| selected | 96 | 1,201,556 | 0 | 0 | 0 | 194 | 25.390278 |
| rebuild | 96 | 2,666,372 | 0 | 0 | 0 | 194 | 28.946282 |

| Comparison vs maintenance | Completed pairs | Candidate saving | Benefited / harmed / tied | Saving without largest beneficiary |
|---|---:|---:|---:|---:|
| selected | 96 | -2,988.0 | 0 / 50 / 46 | -2,988.0 |
| rebuild | 96 | -1,467,804.0 | 15 / 38 / 43 | -1,500,540.0 |

Complete recurrence induction accounts for exclude and feasible include packings at each prefix, with unreachable classes explicit. A maximum intercept for a fixed cardinality/count/slope bounds all packings in that group, and its predecessor mask attains it. Uniform slopes give A_k+gamma*k*t. Affine slopes give (1+alpha*t)*P+beta*k*t: maximize P when the factor is positive, minimize P when negative, and any feasible intercept when zero. Maximizing over both extrema therefore gives the exact global optimum for every sign; every line is feasible. Count-vector lines have slope sum(gamma_j*k_j); exact slope states group by their actual integer sum(v). These completed unpruned certificates are valid for all t>=0 (max-only only in its positive domain). For endpoint pruning at the same prefix, a lighter state with both endpoint values at least those of the deleted state dominates throughout [0,256] by affinity and permits every identical remaining-item completion. Witness edges point to retained states and are acyclic. This proof has no implication beyond 256 for the pruned format. Tables, masks, grouping, crossings and every dominance witness are independently checked. These are elementary parametric optimization constructions, with potentially exponential slope-state width, and no new arithmetic claim.

Preparation is charged at time zero; scalar expiry detection includes failed detection and optimizer replacement. Price counts, DP work and dominance work cannot be summed into a speedup. Common-time CPU includes event costs and remaining driver/recognition/horizon bookkeeping at observation end, so intermediate CPU payback is a conservative ledger description rather than clean continuous wall sampling. All initialization/native optimizer costs are charged fully to each policy despite physical sharing. Serialization and audit are outside algorithm CPU and separately saved.

Decisive limitation: An unchanged packing can still require extensive repricing or repeated root splitting. Completing a selected hard tail is not fresh independent evidence.

Every held-out comparison has 96 completed pairs. Complete-work-ledgers.json supplies every operation counter separately, payback times, benefited/harmed/tied counts, largest-beneficiary deletion, and the actual-vector structural ablation. Additional-accounting.json supplies cardinalities, reachable/unreachable entries, raw/retained states, envelope sizes, duplicate slopes, proof memory, phase lengths and source costs. No trajectory or construction caps occurred.
