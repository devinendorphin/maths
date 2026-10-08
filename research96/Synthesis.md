# Experiments 96–100: checked interval bridge and bounded certificate admission

Completed 8 October 2026 from the [OpenAI-informed roadmap](../research-notes/Roadmap-after-OpenAI-review.md). The useful gain is a **Lean-checked endpoint-to-interval theorem over rational parameters**, alongside explicit claim/dependency scope. Compact witness transport worked, but the additional runtime admission route did not establish a speed improvement over the existing guarded method.

All 116 workers completed on 28 input records representing ten distinct mathematical models. Twenty workers test mechanisms; 96 timed workers compare four methods on eight matched observation records, with three repetitions each. These are repeated small fixtures, not 116 independent problem samples. The headline run took 10.90 seconds within a 300-second wall cap, excluding development, deployment, independent auditing and packaging.

## 96: Claim and dependency audit

Four signed-affine models exercised 44 receipt decisions: unchanged/restored models were accepted; changed times, objectives, capacities, model classes and declared rule/admission/checker identities were rejected. Ordinary cache matching conservatively rejects a capacity restriction even when a separate subset-transfer theorem could justify reuse.

The [claim ledger](Claim-ledger.md) distinguishes point optimality, scalar coverage, rational translation, the interval theorem, admission and reuse. This closes a reporting gap: independent point checks do not make the entire pipeline formally verified. Metadata seals identify consistency, not an authenticated producer.

## 97: Formal rational interval connector

Lean 4.24.0 accepted five theorems: convex-mixture endpoint regret and optimality, the corresponding rational interval statements, and the positive-denominator affine scaling identity. The independently written `ExpectedIntervalRegret` contract was accepted by exact type ascription. Kernel-checked counterexample facts illustrate the excluded nonlinear and varying-feasibility cases. An attempted ascription to `False` failed.

The clean compilation reports only the standard axioms `propext`, `Classical.choice` and `Quot.sound`, with no `sorryAx`. Mathlib was unnecessary. The deployment archive matched the official release digest; setup took 18.42 seconds and downloaded 459,625,674 bytes outside the research repository. Frozen successful compilation used approximately 3.07 CPU seconds, recorded separately from runtime comparisons. Comparator was not run.

Six interval workers connect accepted endpoint proofs and exact scaled candidate values on small models, checking endpoints and interior rational queries. The formal theorem applies to all rational queries satisfying its hypotheses. Numerical examples do not replace that proof. Real-number completion, parsing, subset-sum extraction, the native optimizer and the Python cache remain outside the formal result.

## 98: Compact witnesses and an established checker

Eighteen point records were encoded as four integers per native scalar cell, reconstructed, checked for exact bounds and complete coverage, then expanded through the unchanged original-problem VIPR route. All succeeded. Seventy-two corrupted-witness controls rejected missing coverage, false objectives, zero denominators and changed models.

The raw compact witnesses total **5,147 bytes**, versus **49,169 bytes** for expanded VIPR text: an 89.5% reduction in this transport representation. The witnesses contain 117 scalar cells; expansion uses 802 VIPR derivations. Those counts measure different obligations and are not a proof-step saving. The same expanded VIPR checking is still performed, and keeping both representations uses 54,316 raw bytes. This experiment did not establish reduced total evidence storage.

A descriptive post-run comparison with ordinary gzip is recorded in `Summary.json`; the raw-text reduction should not be confused with an advantage over compressed archives. The repository already compresses and deduplicates archived evidence.

CP 2024 certifying DP and VeriPB interoperability remain unimplemented. The route reproduced here is the available VIPR compiler/checker. It emits point proofs; the rational interval bridge is checked separately. This is an explicit limitation of this bounded batch, not a finding that other proof formats cannot express interval reasoning.

## 99: Progress, interruption and invalidation

Four reference branch trees were stopped after declared budgets and resumed. Twenty snapshots retained sound lower/upper enclosures, with nondecreasing lower bounds and nonincreasing upper bounds. Every final tree matched fresh completion. Twenty-four invalid-state controls rejected changed objectives, capacities, rule/admission/checker identities and a deleted pending branch.

Each model also forced the native producer to stop after one step. Cleanup completed; the unfinished attempt was never admitted. A freshly produced and checked fallback succeeded, with attempted work and fallback included in the recorded mechanism cost. The resumption demonstration uses a small exhaustive reference tree, not native solver checkpoint recovery or a faster optimization algorithm.

## 100: Full runtime cost

Median complete CPU time in milliseconds, including required VIPR checker child CPU:

| Model and observations | Independent points | Guarded intervals | Factor-aware baseline | Compact admission |
|---|---:|---:|---:|---:|
| Wide n=8, dense 17 | 79.46 | 36.36 | 33.77 | 50.25 |
| Same model, sparse 3 | 15.95 | 36.01 | 37.61 | 43.19 |
| Positive scaling n=12, dense 33 | 223.02 | 14.14 | 6.36 | 49.50 |
| Same model, sparse 3 | 21.37 | 15.24 | 7.73 | 18.61 |
| Constant objective n=10, dense 65 | 1468.27 | 43.61 | 19.90 | 157.12 |
| Same model, sparse 3 | 65.16 | 50.89 | 20.24 | 64.92 |
| Sign reversal n=10, dense 5 | 32.35 | 26.39 | 24.32 | 30.94 |
| Same model, sparse 3 | 26.12 | 24.17 | 22.69 | 31.53 |

The compact route was slower than guarded intervals on all eight original records and seven of eight fresh records; the fresh wide/sparse difference reversed by less than one millisecond. It repeatedly loads and checks witness coverage during observations, whereas the older guarded route checks admitted point receipts during preparation. This compares complete implemented assurance paths, not an isolated serialization optimization. The measured overhead is not a lower bound on the cost of stronger checking.

Compact admission beat repeated point checking on six of eight records in both executions, but some differences were near equality. Existing interval reuse retained the larger dense-stream gains; the known positive-factor shortcut was preferable on the matching profiles. The wide/sparse case still favored point solves. The factor baseline correctly fell back when the common factor crossed zero.

No claim of statistical significance or general competitiveness follows from these small timings. In particular, the original guarded-versus-points ranking of seven wins became six in the fresh run. The formal theorem is checked once; Lean is not part of each timed observation. Its deployment and compilation costs are separately disclosed.

## Verification and resulting direction

Independent subset enumeration passed 2,400 answer checks, 655 point-record checks, 521,882 feasible-cover checks and 20 progress-enclosure checks. These are repeated verification counts, not independent observations. All 93 distinct VIPR proofs were accepted again, and 93 separately weakened final-bound controls were rejected. A fresh isolated run completed all 116 workers, matched every logical result after excluding timing and timing-dependent receipt seals, and passed the same independent audit.

The elementary endpoint theorem is now formally checked for the specified rational domain. That improves assurance; it is not a new mathematical theorem or a formal verification of the whole application. The compact route has a useful transport representation and an explicit admission contract, but no demonstrated speed advantage over the strongest existing route. Further runtime expansion of that route should wait for a concrete improvement and a comparable assurance contract.

The next substantive comparison remains the close certifying-DP/proof-logging baseline and production exact solver path identified by the earlier literature review. Preserve the new formal connector and scope ledger; avoid another broad gate sweep. Novelty assessment remains specific to an integrated capability or measured advantage, with no inherited prohibition on claiming a supported result.

Read [reproduction and archive instructions](REPRODUCE.md), [frozen protocol](Protocol.json), [formal-check receipt](Formal-check.json), [independent audit](Audit.json) and [fresh replication](Replication-check.json).
