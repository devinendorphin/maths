# Recovery storage closed for the tested cases

Experiments 141–144 finish the bounded question left by 137–140: can full-snapshot
recovery storage be reduced without weakening concrete-model certificate checks?
The compact format stores immutable topology, capacities, balances and eligibility
once, then stores exact cost vectors and fully checked proof changes. It passed
all admitted-model, residual-sign, hash-chain and terminal-anchor checks.

Each accepted directory completed **72 workers and 3,528 observations**, covering
294 distinct concrete models and 294 distinct proofs. All 588 false-certificate
controls and 14 designed recovery refusals passed. The audit replayed 826 images
per directory. Fresh-directory replication matches every meaningful worker field,
historical evidence hash and active recovery file hash exactly. The environments
share one pinned installation; this is not independent human or solver review.

Compact recovery wrote fewer active bytes and had lower peak active disk in all
18 matched network/policy cells in both directories. Complete-session mean time
was lower in 16/18 primary cells and 15/18 replica cells; smaller cases remain
mixed. Each mean has only two sessions. These are finite synthetic results.

For the largest case (128 nodes, 4,096 edges), the following bytes are exact and
identical across repetitions/directories; time includes complete isolated sessions.

| Policy: journal budget / cadence | Format | Active writes, bytes | Peak active disk, bytes | Images | Primary / replica mean wall, ms |
|---|---|---:|---:|---:|---:|
| 1 KiB / 8 | full | 3,154,888 | 441,693 | 20 | 2,877.9 / 2,977.1 |
| 1 KiB / 8 | compact | 502,828 | 176,487 | 20 | 2,521.8 / 2,576.5 |
| 8 KiB / 8 | full | 1,511,408 | 443,926 | 9 | 1,744.2 / 1,837.8 |
| 8 KiB / 8 | compact | 301,502 | 178,802 | 8 | 1,535.7 / 1,496.9 |
| 64 KiB / 24 | full | 1,511,408 | 443,926 | 9 | 1,770.4 / 1,840.1 |
| 64 KiB / 24 | compact | 236,508 | 187,634 | 4 | 1,171.2 / 1,150.4 |

This is 80–84% fewer active bytes written in those largest-case cells. The journal
budget is a bound on the live journal, not the entire active directory: the base,
image, anchor and temporary replacement image are separately charged. Historical
raw evidence retains every event/image outside active recovery, is measured
separately in Summary.json and is preserved completely in the archive.

Compression preserves exact mathematical admission by reconstructing the original
model/proof and running the same full checker for every proof change and image.
The old persistent handle still tests only supplied changed costs on accepted
patches. Trusted complete deltas, version/context binding and a trusted terminal
anchor remain assumptions. Co-located anchor.json cannot authenticate a hostile
source or prevent wholesale directory rollback. Flush without fsync does not
establish power-loss safety or atomic multi-file checkpointing.

No further small storage experiment is needed before beginning the larger
allocation inquiry. [Experiments 145–147](../research145/Synthesis.md) actually
start it: retained optimizer state for cost updates, explicit capacity/need resets,
and checked infeasibility when resources cannot meet the frozen needs.

See [the frozen protocol](Protocol.md), [complete cost tables](Summary.json),
[audits](Audit-primary.json), [replication](Replication.json) and
[reproduction instructions](REPRODUCE.md). Earlier measurements remain intact.
