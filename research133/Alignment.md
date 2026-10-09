# Execution of the four-stage charter

The starting charter and worked example are preserved at commit
eb1222d70286a4ce13236206558591464e157d4a. This is the successor to 131–132,
not a reinterpretation of any 101–110 or 111–120 batch.

| Experiment / intended comparison | Actual implementation | Evidence | Status and smallest remaining work |
|---|---|---|---|
| 133: static exact flow/checker versus independent solving; invalid and infeasibility controls | Finite-capacity integer flows with rational cost units, lower bounds, cycles, self-loops and parallel edges. Native augmenting feasibility and cycle cancellation; standalone potentials/cut checker; independent NetworkX network simplex and tiny exhaustive oracle. | Protocol, Inputs, Freeze; checker.py, producer.py, reference.py; primary/replica Audit and Proof-controls in archive | Complete within frozen domain. Arbitrary coefficient sizes, generalized constraints and formally verified checker remain outside the tested contract. |
| 134: cold/warm solving, captured proof, potential repair and flow repair; complete costs and budgets | Six named routes on four held-out transportation models, three streams, nine observations, three repetitions. Failed probes and fallback charged. Session startup/CPU/RSS, query phases, buffered proof I/O/replay, one-entry byte cache and forced eviction recorded. Warm and staged flow repair share a seeded producer; they are not two independently designed optimizers. | Sessions/Worker/proof files; Summary; exact Replication; 54 binding-budget records | Complete bounded comparison; no robust whole-session saving established. Pure warm network simplex, scalable dynamic algorithms, fsync durability and per-object cache heap measurement are untested. |
| 135: commitments plus a distinct fairness objective | Eight explicitly synthetic two-supplier/three-recipient cases. Cost optimum versus maximum minimum integral coverage followed by cost tie-break. Descending rational candidates yield valid flow/cut proofs; standalone bundle admission rejects false fairness claims. | 84 scalar/probe records, independently enumerated fairness outcomes; Maintenance-freeze, fairness_admission.py, Maintenance-controls | Complete for this stated formulation and synthetic policy inputs. Stakeholder-defined policies, lexicographic max-min, multiple coupled commodities and practical deployment remain untested. |
| 136: scoped maintenance bound/counterexample and prior-art comparison | Proof of O(k) changed-edge sign/value checking after full admission under a complete trusted delta, with full export costs separated. Five one-edge changes each alter the unique optimal plan. Primary NetworkX, Boost and OR-Tools implementations inspected; full dynamic/fairness papers not reviewed. | Maintenance-bound, Novelty, source receipts/upstream archive copies; six counterexample records, conditional patch controls | Bound and counterexample complete as mathematical arguments and tested illustrations; not formally checked or a new general theorem. Literature priority is partial, so implementation/empirical originality remains a candidate rather than an established first contribution. |

The source/policy freeze preceded headline execution. The 78 static/development
baseline checks and 324 update checks use separate development models where
applicable and are excluded from headline counts. Static fixtures were used as
regressions, not claimed to be unseen. The fairness exhaustive oracle was also
inspected before the freeze; no fairness input or policy was fitted to that output.
Held-out update sequences were not run during development. These distinctions
are recorded in Development.json.

The ten assurance groups were frozen after the primary audit but before their own
execution. They compose retained fairness certificates and test the conditional
checking lemma; they do not replace or relabel the 232 workers. Both directories
use the same reference installation. Earlier archives and all earlier source
freezes are preserved; an updated navigation README has versioned old seals.
