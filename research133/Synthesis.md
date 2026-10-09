# A plan can remain right while its old proof stops applying

The bounded allocation roadmap now has a working exact pipeline and a matching
fresh-directory replication. All 232 workers per directory completed. Each audit
checked 2,099 query/probe records, 227 distinct certificates (145 optimality proofs,
82 shortage cuts), and rejected 1,488 invalid controls. Mathematical outcomes,
underlying flow/potential/cut identities, operation counts, failed probes and cache
decisions match exactly. The ten separately frozen assurance groups also match.

The worker count represents repeated measurements and controls. The update
comparison uses **four** held-out base networks, with 4–10 nodes and 4–25 edges,
three nine-observation streams, six routes and three repetitions. Eleven static
fixtures, eight synthetic service-policy cases and a two-edge counterexample are
separate. There are 209 distinct concrete model/observation encodings across the
whole run. These are modest finite inputs, not a large-scale deployment.

Looking at the 96 transitions between observations on the cold route (one
repetition), an old feasible plan remained optimal 45 times. Its old potential
still applied in only 23 of those cases: **22 transitions kept a right answer but
needed a different proof**. Another 21 old plans stayed feasible but became too
costly; 14 became infeasible; eight transitions entered infeasibility and eight
started from an infeasible observation. The supporting proofs distinguish those
outcomes rather than treating a rejected old certificate as a shortage proof.

Warm/potential repair reduced some inner solver work. Complete fresh-session
costs were close among the five native routes, with no robust end-to-end winner.
The table gives median wall time for a nine-observation session and summed worker
CPU across 36 update sessions per route. Full phase data and all measurements are
retained in Summary.json and the archive.

| Route | Primary median session ms | Replica median session ms | Primary / replica summed CPU s |
|---|---:|---:|---:|
| Cold native | 36.16 | 36.39 | 1.269 / 1.333 |
| Warm native | 36.17 | 36.10 | 1.271 / 1.243 |
| Captured proof, cold fallback | 36.39 | 36.13 | 1.271 / 1.274 |
| Potential repair, cold fallback | 36.22 | 36.15 | 1.259 / 1.236 |
| Staged proof/potential/flow repair | 36.15 | 36.22 | 1.286 / 1.262 |
| Cold NetworkX + certificate completion | 123.19 | 122.99 | 4.463 / 4.473 |

Startup, validation and proof I/O dominate much of the native work at these
sizes. NetworkX's import is charged inside each fresh session, so its larger
figures are specific to this deployment and cannot rank the underlying algorithms
in general. Across the entire campaign, summed session wall time was 12.162s /
12.158s and worker CPU was 11.464s / 11.458s (primary/replica). Individual worker
peak RSS ranged from 11,756–27,872 KiB / 11,732–27,872 KiB. Certificates occupied
179–285 serialized bytes. Those bytes are not Python cache heap size. The binding
cache control evicted every entry, proving that its budget was exercised.

The service tests answer a different question from cheap allocation. With six
units available and needs (3,4,5), the best minimum coverage is 2/5, with exact
cost 9; with four units it is 1/4, with cost 15/2. A cost-only policy with no floors
can instead pay zero and deliver nothing because unused supply is allowed. Floors
(1,1,1) force some service but do not by themselves prove max-min optimality.
Every rejected higher coverage has a checked cut; the selected level has a
checked cost optimum. The bundle checker rejects scalar proofs falsely presented
as positive max-min proofs, even after granting the correct new model digest.

If one recipient has no eligibility edge, minimum coverage is zero. This narrow
max-minimum-plus-cost objective may then leave everyone unserved; it is not full
lexicographic max-min and cannot replace people's policy choices. Floors (3,3,3)
exceed the tested supply and receive genuine infeasibility witnesses. All 70 failed
coverage probes across the eight cases are retained and charged. These cases are
synthetic; no real organization's priorities or deployment were validated.

[Maintenance-bound.md](Maintenance-bound.md) shows when checking only changed
cost edges is sufficient under immutable admission and a complete trusted delta.
It also separates the O(k) sign/value test from reading raw models and exporting
a full proof. The current fully serialized pipeline retains those linear costs.
The alternating two-edge example changes the unique optimum on all five updates,
so a single changed coefficient cannot guarantee that an old plan survives.

These ingredients are established mathematics. [Novelty.md](Novelty.md) compares
inspected primary implementations and identifies the unfinished primary-paper
priority work. The verified contribution today is this inspectable bounded
comparison and assurance pipeline. It is not a new general optimization theorem,
a formal verification of Python, or a claim that mathematical research or human
policy deliberation has been completed.
