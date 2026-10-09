# Exact facts, immutable admission and trusted components

The model has fixed binary variables, fixed positive integer weights and a fixed capacity. Profit for item j is the signed affine expression p[j] + t v[j]. Parameter queries and interval endpoints are rational. Each admitted packing is feasible and attains an exact endpoint optimum. A packing optimal at both endpoints remains optimal between them by the existing rational endpoint theorem. Feasibility changes and nonlinear objective changes are outside this contract.

The snapshot constructor checks endpoint facts, candidate endpoint values and coverage, then captures tuples of model identity, dependency epoch and intervals. A query checks exact model identity, the supplied epoch, model class, interval containment and primal feasibility. It does not read disk proofs after admission. The caller supplies the dependency epoch at the beginning of the stream; the implementation does not continuously hash all executing code or authenticate arbitrary untrusted callers. The epoch identifies four declared components, while the pre-run freeze records the wider source/dependency set. Trusted code must preserve that deployment throughout the stream.

Captured facts are mathematical statements about a fixed model. Altering an external proof copy or mutable diagnostic record does not alter those statements. Repeated admission has a different operational contract: it revisits current stored records. Experiment 106 intentionally distinguishes these contracts. Claims of faster snapshot lookup must not be presented as maintaining continuous file-integrity checking at the same cost.

| Layer | Evidence and limitation |
|---|---|
| Mathematical implication | Unchanged `formal/Endpoint.lean`, previously checked with Lean 4.24.0 in experiments 96–100. No new formal compilation or proof is claimed in 101–110. |
| Native point bound | Frozen exact optimizer, scalar domain/coverage audit and accepted VIPR certificate; compact witness admission reconstructs the logged proof. Trusted serializer and checker deployment remain. |
| CP point bound | Pinned CP 2024 knapsack algorithm with disclosed adapter, original and solution-expanded proofs, accepted pinned VeriPB v2 check. Signed inputs differ from the published benchmark generator. |
| SCIP proposal | Ordinary floating solver proposal, checked as an integer packing and matched to a separately generated exact native/VIPR optimum. SCIP floating dual bounds are not admission evidence. No SCIP exact certificate is produced. |
| Snapshot / cache | Trusted ordinary Python, immutable tuples and explicit context checks. Not formally verified machine code, secure isolation, or a general persistent certificate database. |
| Independent audit | Imports no optimizer, admission routine or cache implementation. Enumerates every subset of each small model, checks answers, endpoint values, file identities and native coverage, replays external checkers, and rejects false-bound controls. Auditor written after producer freeze, identified by its own hash in `Audit.json`. |
| Replication | New campaign directory and generated evidence, same frozen sources and external SDK. All logical fields and proof/witness hashes match; timing fields and receipt seals containing timings are excluded explicitly. No independent SDK deployment is claimed. |

Zero-node interruption retains a feasible lower bound and an independently calculated exact root-price upper bound. A positive gap is reported as bounded, never optimal. Final continuation answers require an accepted native/VIPR certificate. The LRU limit counts only live admitted point facts; retained archival records are additional storage.

Capabilities, cap failures during development, rejected prototypes and accepted headline results are separate in their named receipts. The 600-second campaign, 5-second SCIP solve, 100,000-node SCIP solve, 10-second external producer, 15-second checker and 8-MiB CP proof limits were frozen before the headline run. Completion here does not establish scalability outside those inputs and limits.
