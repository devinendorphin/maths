# Review of this conversation and its experimental evidence

Reviewed 9 October 2026. This document supersedes any implication that the provisional continuation completes the user's full 111–120 roadmap. No previous evidence or Git history was removed or rewritten.

## What is verified

The environment setup and experiments 96–100 replication were executed, independently audited, and their evidence was pushed in commit 788a12e. The later 273-worker experiments 101–110 batch was pushed in commit 245fffe; GitHub main still points to that commit. Its 2,188 archive members and all 57 frozen source/input/dependency files were rechecked during this review. That batch contains an original Python recurrence-table checker and ordinary SCIP candidates certified by duplicated exact DP work. It does not contain the official CP 2024 adaptation, VeriPB proofs or SCIP reoptimization described in the later supplied handoff.

The handoff appeared only after this session's 101–110 publication. It describes another 300-worker batch with a 687,116-byte archive and a different checksum. Accessible workspace traversal and GitHub origin ref inspection did not locate that evidence. Absence in these locations does not prove that it never existed in another workspace. The discrepancy remains unresolved; the requested result counts must not be borrowed.

The provisional continuation ran 284 workers across eight tested stage numbers (113–120), with five held-out models, two training models and one crossing control. Its final independent audits include training evidence: each checked 2,829 answers, 430 DP certificate admissions, 50 invalid admissions, and 26 accepted VIPR proofs plus 26 rejected weakened controls. Earlier commentary's 2,185 answer count referred to the held-out-only auditor before training evidence was added; it was not the final complete count.

Both runs' compared logical result fields and underlying DP certificate/proof hashes match. Component timings and RSS measurements differ as expected. The first packaging comparison mistakenly retained decomposition timing fields; that comparison failed and no successful match was reported from it. The corrected receipt lists excluded measurements. Stream transport hashes may differ because stream JSON embeds timed VIPR diagnostics; underlying proof hashes are compared separately. The DP manifest includes deliberately invalid control records, not solely valid certificates. No independent SDK installation was performed.

The provisional archive contains 370 verified members. It and the continuation are local and uncommitted. They have not been published as a completed 111–120 batch.

## Scope problems requiring correction before a completion claim

| Requested work | Work actually performed | Assessment |
|---|---|---|
| 111 compatible exact SCIP deployment | Official v10.0.0 source configuration failed for missing MPFR; local apt metadata has no candidate. Existing wheel also lacks exact support. | A failed configuration attempt, not proof that a compatible deployment is unobtainable. The timeout capped configuration, not the entire installation investigation. |
| 112 actual SCIP certificates | None produced. | Unsupported in the tested deployment, not passed. |
| 113 amortized proof checking | Stateless persistent Python DP recurrence checker versus process per request. | Useful narrower test; no amortized VIPR/VeriPB or native SCIP checking result. |
| 114 complete cost decomposition | DP optimization/table production combined; I/O/readmission combined; full total retained. | Partial decomposition, not all requested components separately measured. |
| 115 held-out larger suite | Five fixed held-out models up to 20 items, explicit cell and serialized-proof limits. | Completed bounded coverage; no general scalability conclusion. |
| 116 rational crossings/edges | Exact queries around one known crossing, generic endpoint neighborhoods and ties. | Bounded control coverage, not a systematic sweep of all held-out model crossings. |
| 117 trained local-window policy | Frozen choice among three widths, separate training models, charged unsuccessful endpoint probes. | Valid bounded comparison; fixed method order and small timings limit interpretation. |
| 118 density policy | Both density buckets selected factor-aware mode; non-factor models fall back to the same DP point computation. | No demonstrated density discrimination. Training compares overlapping/duplicate routes; tiny timing differences cannot establish policy quality. |
| 119 memory and eviction | Two-entry LRU, serialized retained bytes, separate self/child maximum RSS and request-boundary combined RSS samples in 113. | Partial. Serialized bytes are not Python object memory; separate peaks are not simultaneous process-tree peak memory. Dependency invalidation is not exercised in the LRU itself. |
| 120 admission challenges | Model/time/scope rejection and injected declared checker identity mismatch. | Bounded declared-scope controls. It does not alter a live checker or exercise integrated snapshot-cache dependency invalidation. |

The key process error was proceeding from the recovery discrepancy directly to a materially narrower continuation and describing supported execution too broadly. Unavailable requested evidence should remain explicit; alternative tests must be identified as supplementary rather than silently satisfying the original scientific comparison.

## Next work

Keep the published 273-worker batch and provisional evidence intact. Do not label the provisional campaign as ten fully completed requested experiments. Improve exact SCIP prerequisite recovery within a genuinely measured total setup budget; if it still fails, retain a precise unsupported certificate result. Freeze a revised protocol before any additional headline execution. Separate production/proof/checker/I/O/admission costs, compare nonduplicate policy choices with balanced timing order, measure a simultaneous process tree during execution, and exercise dependency invalidation in the actual cached/snapshot route. Publish the corrected scope, evidence and unresolved recovery discrepancy together without borrowing the separate handoff's results.
