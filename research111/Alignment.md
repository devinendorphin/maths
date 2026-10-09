# Evidence alignment

The question is when an exact answer remains optimal, when a proof remains applicable, and when the complete checked reuse path costs less than solving and certifying again. The model is binary knapsack with fixed positive integer weights and capacity, signed affine coefficients, and rational queries. These three obligations are tracked separately.

## Three evidence sets

| Set | Identity and evidence | What can be used |
|---|---|---|
| A: published 101–110 | Commit `245fffe57a67168c9c4d35fb8de868e11abef23f`; `research101/Protocol.json`, frozen code, `Audit.json`, `Replication-check.json`, and the 256,316-byte archive with SHA-256 `caed8f982a8e57044e8ab1f9c8867947e5f3a474803f6454a831a97836419dc2` | 273 workers; 1,716 answer checks per audit; 42 distinct VIPR proofs. This is the available DP/SCIP-candidate batch. |
| B: historical local 101–110 | User-supplied continuation report; expected 687,116-byte archive SHA-256 `4a01c756935d8efda38fb7df02b9ad1caeec4cbbf3ccd8f2a568783969f5e758`; archive and number-specific protocol unrecovered | Reported 300 workers, 6,239 answer checks, 139 VIPR and 21 VeriPB proofs are historical claims, not verified results here. Its reported findings become comparison hypotheses. |
| C: provisional 111–120 | `research111/Protocol.json`, `Freeze.json`, `Audit-source.json`, `Results.json`, `Audit.json`, `Fresh-audit.json`, `Replication.json`, `REVIEW.md`, and the 246,856-byte archive SHA-256 `dc7269260c1114a4ec61446efc7dcc4ac8e1894f3ff7f692beb9489b2034212b` | 284 workers in eight implemented stages; 2,829 audited answers including training evidence; 26 distinct VIPR proofs. Some comparisons were substituted or partial. The original files are preserved. |

Set B's numbered 101–110 mapping is unavailable. Assigning its unnumbered findings to Set A's experiment numbers would invent a correspondence. The table below therefore identifies the actual questions in Set A, and separately states gaps against the broader historical trajectory.

## Published experiments 101–110 (Set A)

Evidence references `A-code` and `A-audit` mean `research101/code/campaign.py`, its independent `code/audit.py`, `Audit.json`, and archived proof/table artifacts. Status is relative to the published protocol, not equivalence with Set B.

| Experiment | Intended question / comparison | Available test and supporting evidence | Status | Smallest additional work for trajectory alignment |
|---|---|---|---|---|
| 101 | Independently certified point solving | Exact capacity-DP tables, recurrence checker and independent enumeration; A-code/A-audit, stage 101 | Complete | Keep as a distinct Python DP assurance baseline. |
| 102 | Production SCIP candidates with exact admission | Cold ordinary SCIP plus a complete independent DP solve/certificate; stage 102, `Capabilities.json` | Complete for published question; partial production comparison | Add ordinary reoptimization with the same fully charged certification contract. |
| 103 | Capacity scaling and DP cost | Weight/capacity factors 1/4/16 preserve feasible subsets and expose table growth; stage 103 | Complete | No rerun. Do not infer a general crossover. |
| 104 | Signed, zero and tied objectives | Tie and zero-capacity fixtures, nine queries; stage 104 | Complete | No rerun. |
| 105 | Rational coefficient scaling | 1/3, 7/5, 15/2 checked exactly; stage 105 | Complete | Retain rational-input checks when adding new paths. |
| 106 | False-table admission controls | Six corruptions per baseline input; stage 106 and rejected table artifacts | Complete within declared scope | Preserve controls; extend them to any new checker deployment. |
| 107 | Resource caps and fallback | Preallocation cap failure then exact completion; stage 107 | Complete for cap gate; narrower than interruption recovery | Historical zero-node SCIP continuation remains an unrecovered report. Do not rename this as solver checkpoint recovery. |
| 108 | Capacity applicability and subset transfer | Old certificate rejected on changed capacity; conditional unchanged optimum transfer; stage 108 | Complete | Challenge the actual reusable cache, not only a standalone verifier. |
| 109 | Repeated point checking versus memoization | Point certificates replayed on cache hits; stage 109 | Complete for point memoization; partial endpoint trajectory | Add comparable repeated endpoint admission versus immutable endpoint admission. |
| 110 | Complete cost, dense versus sparse | DP, SCIP+DP, VIPR points and guarded intervals on matched streams; stage 110, `Summary.json` | Complete for tested methods | Add compatible immutable admission and ordinary SCIP reoptimization; CP 2024/VeriPB adaptation remains absent. |

## Historical hypotheses from Set B

| Historical comparison / reported finding | Evidence status | How it will be treated |
|---|---|---|
| One-time endpoint admission cheaper than replay | Unrecovered | Test two implementations with identical endpoint proof/model contract. |
| Dense interval reuse and sparse point solving on two twelve-item models | Unrecovered models | Preserve as a hypothesis; use explicitly identified available frozen models without claiming replication of those two models. |
| Official CP 2024 DP adaptation checked with VeriPB | Unrecovered | Current Python DP is a substitute; neither implementation nor proof format is claimed recovered. |
| Ordinary SCIP reoptimization faster than cold solving | Unrecovered | Test cold/reoptimization using the available SDK and the same external exact certificate cost. |
| Wheel lacks exact support; native/VIPR duplicate certification | Historical report; wheel limitation independently observed in A | Exact deployment requires its own bounded attempt; ordinary solver answers remain separate from native SCIP certificates. |
| Zero-node interruption/continuation | Unrecovered | Retain report; no deep-checkpoint claim. |

## Continuation experiments 111–120 (Set C) and targeted repairs

`C-code` is `research111/code/campaign.py`; `C-audit` is its sealed independent auditor and both audit receipts. The immutable facts/bytes in Set C will not be replaced by repair outcomes.

| Experiment | Intended question / comparison | Available implementation and evidence | Status before repair | Smallest additional work |
|---|---|---|---|---|
| 111 | Compatible exact SCIP deployment | Wheel gate and official source configuration fail at missing MPFR; `Capabilities.json`, `Exact-configure.log` | Partial attempt | Recover signed package metadata locally, obtain prerequisites, and bound the entire build/setup interval. |
| 112 | Actual SCIP-produced certificates, independently checked | Zero native SCIP certificates; `Availability.json` | Unsupported in tested deployment | If 111 succeeds, disable uncertified presolve, obtain native certificates, charge completion, verify externally with false controls. |
| 113 | Valid amortized proof checking with isolation | Persistent Python DP verifier versus process per request; C-code/C-audit stage 113 | Substituted | Add a disclosed pristine-parent/fork deployment of the unchanged external VIPR checker; compare identical request sequences and invalid controls. |
| 114 | Full solver/encoding/proof/I/O/admission/checker cost | DP production combined; I/O/readmission combined; stage 114 | Partial | Instrument a compatible original-problem VIPR path with disjoint phases, child CPU and full total; disclose measured residual. |
| 115 | Modest larger frozen transfer suite with limits | Five held-out 18/20-item models, explicit table/storage caps; stage 115 | Complete bounded coverage | Reuse fixtures; no rerun of their earlier validation. |
| 116 | Rational crossings/ties/edges | Known 3/2 crossing and endpoint-neighborhood queries; stage 116 | Complete narrow controls | Use those controls in new admission paths; no claim of all-crossing coverage. |
| 117 | Local windows versus separately trained policy | Width 2/4/8 training, failed probes charged; stage 117, `Training.json` | Complete bounded comparison with timing-order limit | Preserve results and caution; balance ordering only in new matched repair paths. |
| 118 | Query-density policy among compatible choices | Both buckets select factor mode; non-factor fallback duplicates point path; stage 118 | Partial discrimination | Report degeneracy; add compatible point/guarded/immutable comparison and distinct cold/reoptimization paths, not a new tuned sweep. |
| 119 | Cache memory, eviction and model/dependency changes | Serialized bytes, self/child RSS maxima, model miss; stage 119 | Partial | Sample simultaneous resident process-tree memory; measure traced live Python cache allocations; test real epoch-based eviction. |
| 120 | Capacity/weight/domain/nonlinear/dependency applicability | Standalone scope controls and injected identity mismatch; stage 120 | Partial integrated coverage | Exercise actual point/snapshot cache on all changes, distinguish model recertification from unsupported-domain rejection, and demonstrate explicit dependency epoch change. |

Immutable admission captures checked facts in a fixed process and model. It does not monitor external files continuously. A deliberate dependency epoch update can invalidate a cache; arbitrary unannounced code changes are outside that contract. Lean's endpoint implication is conditional mathematics, not formal verification of the Python pipeline.

## After the bounded repair supplement

The preceding tables preserve the pre-repair reconciliation. New results are a separate supplement, not modifications of A/C or a recovery of B. Evidence references below are relative to `research111/repairs/`; the archive contains both runs and all proof artifacts. Both final independent audits passed, and every logical field and raw/final proof identity matched in replication.

| Experiment | Additional implementation and evidence | Current status relative to the intended question | Smallest remaining work |
|---|---|---|---|
| 111 | Official MPFR-enabled SoPlex/SCIP build; Exact-setup.json and SDK-manifest.json | Complete compatible deployment; setup scripts bounded, broader development acquisition not fully timed | New clean SDK installation only if installation independence becomes a comparison requirement. |
| 112 | Nine actual native SCIP certificates, six officially completed, original-model normalization binding and false-bound controls; Results/Audit/Proof-manifest | Complete on declared bounded fixtures/settings | Broader transformations/settings remain outside this comparison. |
| 113 | Unchanged VIPR in pristine-parent/fresh-child adapter, identical alternating valid/invalid sequence; R113 records and audit | Complete deployment-startup amortization; explicitly substituted for persistent logical checker-state reuse | A separately justified incremental route would require its own state-isolation contract; no VeriPB result. |
| 114 | Disjoint solver/native-witness/encoding/I/O/admission/checker/output phases, full total/residual; R114-scip | Partial decomposition, complete charged maintenance totals | Optimization and native witness are inseparable in this producer; separately instrument another producer only for that narrower attribution question. |
| 115 | Earlier held-out frozen suite retained; two existing fixtures reused | Complete earlier bounded validation | No rerun needed. |
| 116 | Earlier controls retained; new native certificates around the exact crossing | Complete narrow rational controls | A systematic all-crossing campaign would be new work. |
| 117 | Earlier trained local-window work retained; failed probes explicitly charged in new wide-interval route | Complete earlier bounded comparison with timing-order caveat | No renumbering rerun; a new transfer campaign would need separate models. |
| 118 | New distinct certified cold/reoptimized and point/replay/immutable comparisons; R-admission/R114-scip | Partial policy question: original density policy still degenerate | Future discriminatory policy needs genuinely different trained choices and separate evaluation; do not claim this supplement repaired density selection. |
| 119 | Reachable Python cache graphs, tracemalloc scenario and controlled runner/checker RSS/PSS checkpoint; Memory-amendment, Memory-repair and final audit | Partial combined-memory coverage. Original sampler invalid because runtime omits task/children; values preserved as runner-only. Supplement is a separate retained-state checkpoint | Unmodified integrated cache/checker process-tree peak requires a corrected observer during that scenario; not established here. |
| 120 | Live context switching on capacity/weight/objective/domain/nonlinear/actual checker-binary changes, explicit refresh and LRU reconstruction | Complete declared integrated controls; arbitrary code monitoring unsupported | No blanket monitoring claim; new dependency semantics require a separately specified epoch contract. |

The compatible additions also test the historical endpoint-admission and ordinary reoptimization hypotheses on identified available fixtures. They do not reproduce unrecovered models, the CP 2024 adaptation or interruption fixtures. The [repair synthesis](repairs/Synthesis.md) gives conditional findings, full-cost comparisons and remaining discrepancies.
