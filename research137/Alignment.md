# Four bounded continuation stages

| Stage | Execution | Status and remaining work |
|---|---|---|
| 137: sparse transactional cost admission | Owned state and strict complete-delta/version/context contract; instrumented no-full-scan accepted path; residual-sign/value checks; failed attempts leave state intact. | Complete in the frozen domain. Authentication and detection of omitted authoritative changes are outside this trusted-source contract. |
| 138: scale and complete costs | Six 16–128-node, 32–4,096-edge networks, four routes, three repetitions and 25 observations per session. Exact model reconstruction, all certificate checks and shared-NetworkX re-encoding audit. | Complete finite comparison. Larger dense/sparse cases show measured savings in this deployment; small cases are mixed. No dynamic state-of-the-art solver comparison or statistically general speed claim. |
| 139: bounded replay and recovery | 4 KiB live journal, six 64-byte controls; 115 forced compactions; raw-log independent replay, full terminal export/recovery, atomic checkpoint/file-directory fsync route. Ten edit/order/truncation/anchored-rollback controls. | Complete logical recovery/budget tests. Primary 4 KiB route does not reach the cap. Total disk, total heap, real power-loss testing and budget/cadence optimization remain open. |
| 140: assurance boundaries | Twelve refusal/failed-sign transaction controls, caller ownership, explicit omitted-update limit, two feasible non-cost changes and one independently checked shortage cut. | Complete designed controls. These are separate examples, not a larger capacity/balance update benchmark or stakeholder validation. |

Primary and replica each contain 78 workers and 1,950 headline observation
records spanning 150 distinct concrete cost models and 175 headline proof
identities. Three additional non-cost certificates are separate. Twelve
transaction/failed-sign and ten recovery controls are separately counted.
The 887 invalid-certificate rejections include 875 headline mutations and twelve
mutations of the three non-cost cases. No worker or trajectory stopped at a cap.

All frozen files, mathematical decisions, log/checkpoint bytes and identities,
certificate identities, counters, output bytes and control results match between
the two accepted directories. Only measured timing/CPU/RSS fields differ.
One earlier execution failed custody inspection and is retained under
rejected-custody/ in the complete archive; it is not pooled into these results.
The two accepted executions use one newly installed pinned solver environment;
they are fresh-directory replications, not independent installations or human
reviews. The exact frozen source and rejected evidence are preserved.
