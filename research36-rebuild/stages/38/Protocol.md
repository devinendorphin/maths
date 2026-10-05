# Rebuilt experiment 38

# Continue exact parametric-knapsack research: experiments 36–40

## Launch prompt

Use this handoff with `Temporal-proof-experiments-31-35-campaign.zip`. Verify the checkpoint, then implement, verify, execute, audit and save experiments 36–40 in one continuous run. Preserve every completed case, phase and audit prefix. Use fresh development and held-out data for every new experiment. Finish all five stages without another “Continue.” Negative findings are completed experiments; capped computations remain incomplete and must be disclosed. Save a concise synthesis, a reproducible archive and exact resume cursors. Distinguish mathematical certificate guarantees from empirical performance and make no claim of new arithmetic.

This request authorizes the prospective budgets below for new experiments. It does not authorize rewriting prior results or silently raising a frozen cap. If an environment limit interrupts execution, checkpoint the exact pending action, preserve completed work, and state the interruption.

## Checkpoint and first inspection

The required archive is:

- Filename: `Temporal-proof-experiments-31-35-campaign.zip`
- Byte length: **176,127,453**
- SHA256: `656930b55f767e811089a8b345abb1cbf228559dd13afaf4be770d4c7c4f7b9f`
- Archive entries: **8,276**, including `Manifest.json`.
- Manifest: **8,275** hashed members.

Unpack into a new workspace. Paths below are relative to that archive's root. Preserve the supplied files unchanged and place new work under a separate directory, such as `research36/`.

Read before implementing:

1. `research/Synthesis.md`, `Mathematical-guarantees.md`, `README.md`, `Campaign-status.json`, `Final-audit.json`, `Checkpoint-verification.json`, `Resume-cursors.json` and `Environment.json`.
2. Stages 31–35: `Protocol.md`, `Frozen.json`, `Verification.json`, `Report.md`, `Final-audit.json`; both splits' `Summary.json`, `Complete-work-ledgers.json`, `Additional-accounting.json`, `Resource-log.json`, `Resume-cursors.json` and `Audit.json`; and each `Record-reconciliation.json`.
3. `research/stages/31/Evidence-recovery.json`, `Audit-marker-reconciliation.json`, and `research/stages/32/Evidence-recovery.json`.
4. `research/stages/34/Freeze-amendment.json`, `Frozen-initial.json`, both retained `Before-amendment-*.py` files, `Selection.json` and `Timing.json`.
5. `research/stages/35/Structural-candidate.json`, `Timing-development.json`, `Timing-held.json`, and `Serialization-accounting.json` for stages 33–35.
6. `research/stage30-extension/Protocol.json`, `Summary.json`, `Report.md`, `Complete.json`, `Resume-cursors.json`, the five extension result files and their audit records.
7. The actual APIs in `research/stages/35/code/engine.py`, `source_guarded.py`, `frontier.py`, `check_frontier.py`, `runner.py`, `fixtures.py`, `horizon.py`, `audit_new.py` and `extend30.py`; also `research/code/ledgers.py`, `reconcile.py`, `diagnostics.py`, `final_check.py`, `recover_evidence.py` and `reproduce.py`.

The old runner routes only stages 31–35 and assumes observation ends at 256. Implement new orchestration for stages 36–40 and parameterize interval boundaries explicitly; passing a new stage number to the old runner is not a supported continuation. Reuse verified kernels through inspected APIs, preserving the frozen originals.

Verify the archive checksum, every manifest member and every current stage freeze. Verify the retained stage-34 prior sources against the amendment's prior hashes separately; its amended freeze is authoritative. Stream large-file hashing rather than loading the entire archive into memory. Record exact counts and failures.

The archive also contains the unchanged older campaign under `supplied/Temporal-proof-five-experiment-campaign.zip`, SHA256 `bb2469796172764663afa5e081c2de5b42607c8b30bae8e1333c8cbe93428ad8`. If its extracted paths are needed, extract that nested archive to `campaign/`. Do not assume previous absolute paths exist. Do not replay any completed old campaign.

There is **nothing unfinished to resume** in experiments 31–35 or the stage-30 extension. The top-level resume file has empty lists for unfinished paths, incomplete constructions, unstarted cases, pending audits and extension work. Begin with inspection, then fresh experiment 36.

## Findings and qualifications to preserve

Experiments 31–35 each completed 32 development and 96 held-out trajectories: **640 fresh trajectories and 1,920 policy paths**, with **96 completed pairs in every held-out comparison**. No new trajectory or frontier construction capped. All five old stage-30 capped paths reached time 256 under the separate extension, with no further incumbent switches. Those selected tails are not a new independent held-out sample.

| Stage | Held-out result | What it does not establish |
|---|---|---|
| 31 | Maintenance / skip15 / rebuild: 1,198,568 / 1,201,556 / 2,666,372 candidate evaluations. Skip15 had no successful probe. | No general impossibility of coarsening or worst-case cheapness of maintenance. |
| 32 | Uniform-frontier policy avoided 2,827,592 candidate evaluations; it built 520,032 DP entries. | DP entries are not candidate evaluations. Zero slopes incurred preparation when renewal was already unnecessary. |
| 33 | Maintenance / max-only / max-min: 1,105,203 / 656,133 / 435,262 candidate evaluations. Max/min built 468,372 DP entries. | Maximum-intercept normalization cannot cross a nonpositive factor without a separate proof or scalar handoff. |
| 34 | Two-class policy: 78,470 candidate evaluations and 599,242 DP entries; maintenance: 752,819 evaluations. | The fixed two-class gate does not cover general slope vectors. |
| 35 | Unpruned / endpoint-pruned: 123,846 / 41,536 DP entries; both had zero scalar renewal evaluations. Pruning made 1,716,097 dominance comparisons and 10,721 deletions. | Small observed slope frontiers do not bound worst-case width. Endpoint pruning has no guarantee beyond its interval. |

Stage-34 development timing selected two-class for stage 35. Its median aggregate CPU on the declared eight-case subset was 0.075950 s, versus 0.290468 for affine max/min and 1.212845 for maintenance. This was a development-only choice.

On stage 35's prescribed eight-case subsets, median full algorithm CPU was:

| Subset | Maintenance | Two-class | Unpruned slope | Endpoint-pruned |
|---|---:|---:|---:|---:|
| Development | 0.331398 s | 0.362534 s | 0.011061 s | 0.028280 s |
| First held-out seed | 0.106246 s | 0.072443 s | 0.013645 s | 0.047536 s |

Unpruned construction beat pruning in every declared repetition on both subsets after charging preparation. This is evidence for those trajectories, not a universal winner. Two-class varied substantially across development repetitions; do not conceal that variation or select the fastest repetition.

Three missing policy-result records retained earlier partial file versions: one stage-31 held-out rebuild path and two stage-32 uniform-frontier paths. Only those records were regenerated from frozen code and independently audited. Original aggregates and surviving paths were retained; repeated work is disclosed separately. Later stages kept immutable per-policy results and continued missing saved audit ranges without policy replay. Stage 34's first timing attempt failed at a checkpoint pathname; its uncheckpointed first policy attempt was repeated, and its CPU was not retained. Do not invent those measurements. Earlier serialization CPU was not retained; prospective save records exist from stage 33. Intermediate CPU ledgers contain conservative allocations of otherwise unallocated bookkeeping, while operation ledgers locate horizons at their actual anchors.

## Model and guarantees

Weights are positive integers; capacity is nonnegative; profits and slopes are signed integers. Modeled integer time is explicit:

`q_i(t) = p_i + t v_i`, for `t >= 0`.

For feasible mask M, define `W_M`, `P_M`, `S_M` as its weight, intercept and slope sums. Its value is `P_M + t S_M`. Empty packing is feasible. Retain an incumbent through ties; switch only after a feasible witness proves strict loss.

Preserve the exact scalar-price repair kernel, deterministic ratio ties, infeasible-include omission, cover semantics and native optimizer. A scalar-price failure is not an improving witness. A partial repair or partial DP is never a certificate. All methods get exact `v=p` positive-factor normalization first, recognized from the vectors. Other structural shortcuts must be explicitly included in a fixed policy and charged; do not give one method another method's proof for free.

A sparse recurrence state at prefix j is `(W,S,P,M,predecessor)`: the maximum intercept for exact weight W and slope S among prefix packings, with a feasible witness M. Include/exclude transitions account for every packing, including negative profits and slopes. Same-state maximum reduction is exact. Terminal aggregation over weights `W<=c` supplies lines `A_s+t s`. Complete unpruned recurrences give an exact all-time optimum representation; their size can be exponential.

At anchor tau, a competing line A+s*t has margin `V_M(tau)-(A+s*tau)`. If `d=s-S_M>0`, first strict crossing is `tau + floor(margin/d) + 1`. Smaller/equal slopes cannot cause future loss from an optimal anchor. Keep all lines on the original time axis; enforce finite certificate domains. The scalar horizon API assumes its supplied profits are anchored at time zero, so pass shifted integer profits explicitly at later phases.

Every replacement packing must come from the same cold native optimizer, including when a frontier already supplies the optimum value. Identical solves may be shared physically, with full recorded construction, cleanup and disposal costs charged to each policy. Audit enumeration/DP must never supply missing algorithm states, selector features, branch choices or free optimizer answers.

## Common fresh-data protocol

Stages 36, 37, 39 and 40 use the standard core matrix: n=12/16, four profit families, four directions, one development seed and three held-out seeds. This gives **32 development and 96 held-out trajectories per stage**. Stage 38 has the same core plus the separate stress matrix below. Sharing weights/profits across directions creates dependence; do not report trajectories as independent statistical trials.

| Stage | Core development seed | Core held-out seeds | Observation interval |
|---|---:|---|---|
| 36 | 151000 | 151500 / 151501 / 151502 | 0–256 |
| 37 | 152000 | 152500 / 152501 / 152502 | 0–256 |
| 38 | 153000 | 153500 / 153501 / 153502 | 0–256 |
| 39 | 154000 | 154500 / 154501 / 154502 | 0–256 |
| 40 | 155000 | 155500 / 155501 / 155502 | 0–1024 |

For each n/seed, use `random.Random(seed)` and the frozen generator's advancement: n weights drawn from 2–20, capacity `floor(sum(w)/3)`, then all four profit vectors in this order: random 5–50; proportional `w_i+15+randint(-2,2)`; mixed -15–40; negative `-randint(1,10)`. For each family, obtain the common initial native optimum, then generate the old directions before filtering to sparse, signed, scale and harm. Sparse draws one index and a ±1 sign; signed draws n values in -3–3; scale equals p; harm is -1 on the initial packing and +1 elsewhere. Preserve draws for unused directions. Inspect actual vectors rather than labels.

Record weights, profits, slopes, source solve, initial mask/proof, RNG/control metadata and case IDs. Independently check seeded generation. A capped initial optimizer makes initialization incomplete; record its charged work, the pending solve and all blocked policy paths, rather than inventing an initial optimal packing.

### Prospective limits

| Resource | Stages 36–39 | Stage 40 |
|---|---:|---:|
| Cumulative scalar candidate evaluations per policy trajectory | 2,000,000 | 8,000,000 |
| Returned/pending scalar cells | 4,096 | 4,096 |
| Native generator steps / live cells / wall seconds per solve | 500,000 / 4,096 / 30 | same |
| Cumulative native generator steps per policy trajectory | 2,000,000 | 8,000,000 |
| DP proof entries per individual construction | 500,000 | 500,000 |
| DP transitions per individual construction | 2,000,000 | 2,000,000 |
| Dominance comparisons per individual construction | 5,000,000 | 5,000,000 |
| Cumulative DP entries / transitions / dominance comparisons | 500,000 / 2,000,000 / 5,000,000 | 2,000,000 / 8,000,000 / 20,000,000 |
| Index query/update visits per construction | 5,000,000 | 5,000,000; 20,000,000 cumulative |
| Total algorithm wall seconds per policy trajectory | 120 | 240 |
| Independent audit wall seconds per streaming batch | 45 | 45 |

These are ceilings, not expected costs or evidence that computations finish. Bound sorting, compression and index allocations before they can exceed proof-memory limits; count stored auxiliary index/witness records separately. Use a further **500,000 simultaneously retained auxiliary records** guard, independent of the DP-entry guard. Count raw recurrence proof rows across retained layers, not merely the final active layer. Native stores must be disposed even on failure. Include aborted construction/search and disposal costs.

Freeze one construction-cap fallback: preserve the partial proof/cursor, abandon it as an active certificate, and use the last complete scalar partition. If its cached numerators are stale, reprice/repair at current original integer profits before computing a new horizon. Charge both the failed build and fallback. If the total trajectory budget is exhausted, the path remains incomplete. A completed scalar fallback does not make the abandoned frontier construction complete; report those statuses separately.

Use bounded 900-second outer algorithm/audit batches, with checkpoints at policy/construction/audit boundaries and guards inside loops. If a batch expires, commit the exact cursor and continue a new explicitly bounded batch if permitted. Aim for roughly ten minutes per ordinary stage; stage 38's stress cases and stage 40's longer window may need multiple batches. Do not silently shrink a matrix after seeing outcomes.

### Measurements and timing

Keep separate counters for candidate bounds, hinge terms, prices, splits, probes, scalar horizons, recognition comparisons, DP entries/transitions/backpointer updates, frontier lines, envelope queries/intersections, sorting comparisons, same-slope checks, endpoint-dominance comparisons, coordinate-compression work, index queries/visits/updates, witness records/deletions, native generator/cleanup/disposal steps and interval rebuilds. Also report returned/peak active/retained proof and auxiliary-index sizes. Never sum unlike units into a speedup.

Log work at the modeled time at which it is performed. Horizon lookahead is paid at its phase anchor, not at the future predicted loss; constructor debt is paid at construction's anchor; failed expiry detection is paid at the attempted expiry. Require CPU component reconciliation instead of assigning unexplained residuals to time 256/1024. Keep input preparation, initial solve, recognition, construction, horizons, maintenance, native replacement, proof allocation and final certificate handling visible; serialization and independent audits stay separate. Declare whether retained output-proof disposal is inside the measured boundary and apply that boundary uniformly.

For timing, use fresh isolated policy workers, or an equally verified isolation design, so garbage from a previous retained proof cannot be charged accidentally to another policy. Record interpreter/import/input-decoding infrastructure separately; fully charge each worker's own native solves. Cold solves in separate workers are acceptable and avoid sharing confounds. Do not make a kernel-only performance claim stand in for total algorithm CPU.

Predeclare three repetitions on the eight core development trajectories with n=12, families random/negative, all four directions. If making any held-out runtime advantage claim, also repeat exactly that subset from the first held seed. Verify identical logical counters and switch times across repetitions. Capped repetitions are ineligible for full-window CPU selection; report the actual prefixes, not fabricated completion times. Select by median aggregate full CPU across repetitions, never by the fastest repetition or per-held-case winner. Timing repeats remain separate from unique-case headline counts.

Stage 38 adds the eight stress timing cases with n=12, half-capacity, random/negative families and all four stress directions. Its method comparison uses a predeclared combined 16-case development subset, with the matching first-held subset if runtime advantages are claimed. Stage 39's selector tuning uses the separate candidate grid below and the eight-case core development timing subset; archive every candidate, including rejected/capped ones.

At modeled times 0,64,128,256, all switches/expiries, and every construction boundary, compare cumulative ledgers. Stage 40 adds 512,768,1024. Report preparation debt, first strict advantage and first advantage persisting to the observation end separately for each counter and measured CPU. Report paired-completed denominators, benefited/harmed/tied distributions, removal of the largest beneficiary, and a descriptive ablation excluding actually recognized structural trajectories. Include failed builds and failed loss detection. No held-out tuning.

## Experiment 36 — Can same-slope dominance shrink an all-time proof cheaply?

Compare normalized scalar maintenance, the frozen unpruned sparse-slope recurrence, and a new same-slope dominance recurrence on fresh core data. Give all policies only the common `v=p` shortcut before their declared method.

At the same prefix j, X may dominate Y for **all times** when:

`S_X = S_Y`, `W_X <= W_Y`, `P_X >= P_Y`.

Their value difference is the constant `P_X-P_Y`. Any identical remaining-item completion feasible for Y remains feasible for lighter X, with the same added slope/intercept. Prove the induction/completion argument explicitly. Cross-slope comparisons are forbidden in this format.

After generating and applying exact `(W,S)` maximum reduction, process each slope group in increasing W and decreasing P for equal W. Retain a running maximum intercept and a feasible witness ID. Use a fixed tie rule: keep the first canonical earlier survivor; equality may delete the later state. Store complete generated raw rows, retained IDs and each deletion's same-prefix survivor witness. Future recurrence generation uses only retained states, but the proof retains enough information to check the entire generated domain and every deletion. Do not call a rolling value dictionary a complete proof.

Audit independently that every predecessor is feasible, every transition is generated, grouping by slope is complete, each deletion has identical slope and a lighter/higher-intercept survivor, and witness edges are acyclic. Check exact frontiers and original-profit optima at all integer times 0–256 on core cases; supplement with analytic all-time derivation. All-time pruning may delete entire weight states for a slope, so correctness is global optimum preservation, not preservation of an optimum for every exact weight.

Fixtures: equal weight/slope with unequal intercepts; a heavier state with larger intercept that must survive; equal intercepts at different weights; negative intercepts/slopes; slope zero; a cross-slope counterexample that must be rejected; capacity zero; all unreachable includes; deterministic equality and duplicate witnesses. Verify deliberate predecessor/deletion mutations are rejected.

Report sort/group costs, states generated versus retained at each prefix, full raw-plus-witness proof memory, avoided later transitions, envelope sizes and payback. If pruning costs more than unpruned construction, complete the negative result. Do not replace the unpruned reference because of stage-35 held-out timing.

Question: can a time-independent dominance rule reduce preparation without paying for interval-specific two-endpoint searches?

## Experiment 37 — Can an exact index repay endpoint-pruning overhead?

Compare five fixed methods: maintenance, unpruned sparse, experiment-36 same-slope pruning, stage-35 naive endpoint pruning, and a new indexed endpoint-pruning implementation. All use [0,256] for interval pruning and the same canonical raw-state order:

`(W ascending, P descending, Q descending, S ascending, M ascending)`, where `Q=P+256*S`.

At a candidate Y, all earlier retained states are no heavier. The question is whether some retained X satisfies `P_X>=P_Y` and `Q_X>=Q_Y`. An exact possible implementation compresses all P coordinates in the current raw layer, uses descending ranks, and queries a prefix maximum of Q with a feasible witness ID. A Fenwick or segment tree is allowed, with exact signed integer arithmetic and explicit unreachable values. Build/compress/sort/update/query costs and auxiliary proof records are charged.

Insert only retained states. If the queried maximum Q is at least Q_Y, delete Y with the returned survivor witness; otherwise retain and insert Y. For equal Q choose the earliest inserted canonical survivor. This need not reproduce the naive implementation's first witness, but it must reproduce its retain/delete decisions under the same state order. Replacing a query by a library call does not replace its certificate or verification.

Independently verify compression/ranks, index update paths, stored aggregates, query maxima and feasible witnesses against the insertion prefix. A negative query must not conceal an existing dominator if equivalence/performance is claimed. Compare retained-ID sets layer by layer with the naive algorithm on fixtures and bounded development instances, without sharing its construction for free. The independent checker may use a simple pairwise scan; the algorithm may not use audit output to choose states.

Endpoint deletion correctness remains the affine endpoint/completion argument on [0,256]. A fast index does not extend that interval. Require explicit rejection of time 257.

Fixtures: signed/duplicate P and Q coordinates, empty index, equal endpoints at different weights, all candidates dominated, all candidates surviving, one-endpoint-only domination, interior crossings, high-slope/low-intercept states, prefix mismatch rejection, incorrect coordinate ranks/aggregates/witnesses, and a capped index build followed by charged scalar fallback.

Report naive comparisons versus index visits/updates as separate measures, identical retained-set denominators, index certificate memory, construction debt and repeated full CPU. The result may be that indexing helps only above a certain width; describe that finding without selecting a held-out width threshold.

Question: was stage-35 pruning's loss mainly its quadratic search, or does verified indexing still cost more than retaining states?

## Experiment 38 — Where does the sparse frontier cease to be small?

Run the fresh core matrix and a separate predeclared stress matrix. Compare maintenance, unpruned sparse, same-slope pruning and indexed endpoint pruning. Preserve each method's own build and fallback costs.

Stress matrix: n=12/16/20; families random/negative; capacities `floor(sum(w)/3)` and `floor(sum(w)/2)`; four directions; one development seed **253000** and three held seeds **253500/253501/253502**. This is **48 development and 144 held-out stress trajectories**, additional to 32/96 core, giving **80 development and 240 held-out** trajectories for stage 38.

For each stress n/seed, use a fresh RNG. Draw weights and all four profit-family vectors in the common order, retaining random and negative only. Then, for each retained family in random/negative order, draw all four vectors below in this order; reuse those generated vectors across the two capacity ratios:

1. Bounded signed: n independent integers in -3–3.
2. Wide signed: n independent integers in -256–256.
3. Separated powers: n independently drawn ±1 signs, with `v_i=sign_i*2**i`.
4. Shared-block powers: split consecutive item indices into blocks of at most three; draw one ±1 sign per block, and use `v_i=block_sign*2**block_index`.

Record all vectors and block memberships. Stress directions do not depend on the native initial packing. Repeated capacities/directions share data and are not independent observations. Signs on separated powers preserve unique subset slope sums by the largest-power argument; that is a structural fixture/derivation, not a claim that every subset is feasible or every line reaches the envelope.

Report numerical span, actual reachable distinct slopes, repeated-slope collisions, exact-weight state counts, retained/raw prefix widths, frontier/envelope sizes, peak proof/index memory, construction caps/fallbacks, scalar fallback caps, native initialization/replacement caps and completed pairs. Separate core from stress and each capacity ratio; never pool selected hard tails into an independent sample.

For n=20, do not reuse the old unguarded full-array/giant-mask audit initialization. Implement bounded streaming subset enumeration or equivalent independent domain checks, checkpoint mask/layer/event ranges, and use independent original-profit capacity DP. Audit constructors themselves need deadlines. If an audit batch caps, resume its pending range without rerunning the algorithm. Enumeration must remain audit-only. Check completed value frontiers, cover correctness, witness feasibility and exact crossings; do not claim a capped frontier's value from an oracle.

Keep powers/counterexamples even if a guard fires. A capped path is unfinished, although the stage may finish attempting every declared case. Distinguish large slope integers, many reachable slopes, many weight/slope states, and many surviving envelope lines: those are different possible burdens.

Question: did stage 35's success reflect a generally efficient construction, or the small slope range and collisions in its original directions?

## Experiment 39 — Can a fixed preconstruction gate avoid costly certificates?

Use fresh core data. Compare maintenance, always-unpruned construction with frozen guard/fallback, a fixed conservative gate, and a development-selected gate. These selectors choose only **all-time** unpruned or same-slope constructions; interval-pruned methods remain a separate hypothesis for stage 40.

Allowed preconstruction features are exact functions of supplied `(w,p,v,c)`: n, capacity, weight statistics, slope extrema/distinctness, and the prefix slope lattice bound below. No generator label, incumbent's audited future loss, enumeration, trial frontier, hidden optimizer result or held-out outcome may serve as a free feature. Inspect all vector entries needed and charge their actual comparisons/arithmetic.

For prefix j, define `L_j=sum(min(0,v_i))`, `U_j=sum(max(0,v_i))` over its items. Let `g_j=gcd(abs(v_i))` for that prefix. If `g_j=0`, there is one possible slope; otherwise possible slopes lie on multiples of g_j and the bin bound is `1+(U_j-L_j)//g_j`. Exact weights lie in 0–c, so a conservative unpruned prefix-state bound is `(c+1)*bins_j`. Set

`E_bound=sum(prefix_state_bound_j for j=0..n)` and

`T_bound=2*sum(prefix_state_bound_j for j=0..n-1)`.

Prove these bounds and audit their arithmetic. They overcount many infeasible states and do not bound CPU or native search. Prefix gcd is an indexing/count bound, not an arbitrary changing-objective normalization or a new arithmetic.

The fixed conservative gate builds unpruned only if `E_bound<=500000` and `T_bound<=2000000`; otherwise it immediately uses scalar maintenance. Actual guards still apply, including wall time. All methods give `v=p` priority before the gate.

For the selected gate, predeclare the eight candidate combinations: method unpruned/same-slope × entry threshold 50,000/125,000/250,000/500,000, all also requiring `T_bound<=2000000`. Run and retain all candidates on the eight fresh n=12 random/negative development trajectories in three isolated timing repetitions. Use only their median aggregate full CPU; capped candidates are ineligible. Tie-break by smaller threshold, then unpruned. Compare with maintenance: if no eligible candidate beats it, maintenance remains the preferred reference and carry the cheapest eligible gate solely as a hypothesis. If no candidate is eligible, seal immediate maintenance as the selector's behavior.

Archive the complete tuning results, then freeze the single selected gate before its full held-out matrix. Retain full 32-case development results for the four headline methods as well as the separate tuning subset. Previous development stages may inform interpretation, but the specified grid/score/tie-break is not changed after observing outcomes. Never choose the cheapest method independently for each held-out case. Seal `Selection.json` and its hash for stage 40.

Report acceptance/rejection, accepted bound versus actual states, conservatism, rejected cases where an unconditional frontier completed, avoided failed-build debt, preparation/payback, complete pairs, and caps. Any retrospective “could have accepted” calculation is an audit-only descriptive ablation, not an algorithmic result.

Question: can cheap certified resource bounds preserve the fast cases while avoiding expensive attempts, or are they too conservative to repay recognition?

## Experiment 40 — Can interval-pruned proofs be renewed economically through time 1024?

Use fresh core data and the longer interval 0–1024. Compare maintenance, all-time unpruned sparse, the sealed stage-39 all-time selector, and indexed endpoint pruning rebuilt on windows `[0,256]`, `[256,512]`, `[512,768]`, `[768,1024]`. Do not retune the selector on stage-40 development or held-out results. Apply the extended cumulative limits in the common table.

For a current window [a,b], the same-prefix deletion rule is:

`W_X<=W_Y`,
`P_X+a*S_X>=P_Y+a*S_Y`, and
`P_X+b*S_X>=P_Y+b*S_Y`.

Index the exact endpoint values for that window; all stored affine lines retain their original intercept P and slope S. Prove the affine difference/completion argument on [a,b]. A window certificate must reject queries outside [a,b].

**Rebuild each new window from the original item recurrence domain.** A state deleted for an earlier interval may be needed later. Do not continue the old pruned terminal states, reuse discarded states implicitly from an audit, or relabel an old proof's interval. No frontier rebuild is needed merely because the incumbent switches within a valid window.

At a boundary b<1024, the old proof remains valid at b. If strict loss occurs at b, first invoke/charge the common native optimizer for that loss, then build the next window using the resulting common packing. Otherwise build the next window at b and keep the incumbent through ties. A new proof must agree with the old optimum at b; disagreement is a verification failure, not a routine boundary switch. Do not build a gratuitous fifth window at 1024.

When a window build caps, save its exact recurrence/index cursor and all charged work. The frozen fallback restores the most recent complete scalar partition, updates prices/numerators at b's original integer profits and repairs it. Only a feasible strict-improvement witness can trigger a native replacement. If fallback or total trajectory budget caps, preserve the last verified proof and pending action; a DP oracle does not complete it.

Fixtures must include a previously deleted state that becomes necessary immediately beyond an interval. One explicit two-item, capacity-one instance is `w=[1,1]`, `p=[10,-246]`, `v=[0,1]`: item 1 dominates item 2 through 256 with a tie at 256, but item 2 strictly wins at 257. Reusing the old pruned states would be unsound. Also test a strict loss exactly at 256 (`p=[10,-245]`), negative slopes, no boundary switch, several switches within one window, shifted-window dominance, stale scalar numerators at fallback, a capped later rebuild, and rejection at 1025.

Audit all windows, recurrence/deletion witnesses, boundary values, exact loss times, native masks, and joins. Stage-39 all-time selection has no interval-expiry debt; rolling pruning does. Compare cumulative costs at 256/512/768/1024, every switch/expiry and every rebuild, including unsuccessful attempts and fallback. Report whether the first-window memory savings survive repeated construction costs, and how often the shorter proof still loses amortized work.

Question: does interval-specific pruning repay repeated restoration/reconstruction, or does an all-time certificate retain an advantage as observation time grows?

## Evidence, verification and persistence requirements

Define and independently check each new certificate format. Check recurrence base cases, every generated include/exclude transition, reachability, exact grouping, predecessor masks, complete proof domains, dominator feasibility, acyclic deletion chains, signed index aggregates, interval declarations, scalar covers/prices/numerators, branch choices, exact integer crossings and native objectives. Value-only DP results are not complete recurrence certificates.

Use distinct algorithm and audit implementations. For n<=16, enumerate feasible packings once per source when useful; use it to check grouping and frontiers, not to construct them. For n=20, stream bounded audit ranges. Original-profit audit DP at sampled/all observed integer times supplements analytic proofs; it cannot establish all-time validity by extrapolation. Fixtures must include both successful cases and deliberately invalid certificates that the checker rejects.

Persist immutable, uniquely named input/source/policy/phase/construction records before audit, preferably content-hashed. Use fresh temporary names, flush/fsync where supported, atomic rename, and read/hash verification. Mutable case indexes are reconstructible views, never the sole copy of a completed policy. After write/restart, reconcile exact expected case/policy counts, record hashes and required audit ranges. A `passed` flag alone is insufficient: verify coverage of every phase, DP layer, terminal grouping and pending partial-proof prefix. Preserve an earlier verified audit prefix rather than resetting it.

Use explicit serialization for state keys and cursors: numeric W/S fields or typed arrays, not tuple keys silently converted into strings requiring guesswork. Record recurrence prefix, next predecessor/include transition, current raw states, retained IDs and predecessor witnesses. Pruning/index cursors also need canonical order, candidate position, next dominator/query/update position, compression map and tree state. Save original inputs, current packing/anchor, last full scalar proof/forest/cooldown, optimizer cache and complete cumulative costs. A native generator with no serializable continuation must be labeled pending-restart; any authorized restart of that one unfinished solve retains prior failed work and charges the repeat. Never restart completed phases.

Freeze source hashes, direction generation, tie rules, dispatch, caps, index design, fallback and measurement scopes after meaningful fixtures and before held-out. Stage-39 selection is sealed before held-out, and its exact hash is carried into stage 40. Any necessary orchestration/audit correction retains prior source/hashes, records when it occurred and verifies that policy, inputs and caps did not change. Held-out performance does not authorize changing an algorithm.

Before leaving each stage, save its protocol, frozen source/hashes, fixtures and mutation tests, all unique inputs/results, independent audit coverage, complete recurrence/cover/dominance/index evidence, common-time ledgers, component CPU/memory accounting, timing repetitions, failed hypotheses, cap/resource logs, immutable status/cursors and a short report through the environment's supported persistent-file workflow. Do not depend on scratch surviving. Do not assume an upload succeeded from a top-level success alone; check each result. If evidence is missing, recover retained immutable records first and disclose any unavoidable regeneration and repeated costs.

A top-level completion record distinguishes: all cases attempted, all policy paths complete, complete frontier constructions, completed scalar fallbacks, pending audit ranges, initialization failures and unstarted work. A capped construction that fell back successfully remains an incomplete construction even if its policy trajectory finished. Reconcile caps from all saved records, including earlier invocations.

## Final deliverables and claims

After all five stages, save one concise synthesis and one reproducible campaign archive, including this handoff, the unchanged input checkpoint or an explicit byte-identical nested reference, all new source/evidence and a checked manifest. Include exact resume cursors for every unfinished path/construction/audit/initialization. State which matrices were attempted and completed, actual paired denominators, core versus stress results, repeated timings versus unique executions, and decisive limitations.

Explain in plain language the differences among modeled time, execution CPU, true optimality loss, expiry of a particular proof, proof width, and amortized preparation/reconstruction. Separate the elementary same-slope and endpoint-dominance arguments, the verified finite certificates, and the observed runtime findings. Do not infer a generally efficient optimizer from a small observed envelope or zero scalar-price evaluations.

This remains exact parametric integer-knapsack research. It arose from questions about Allen Brooks' “numbers with time built in,” but does not recover his unpublished mathematics or authenticate a breakthrough. No new arithmetic is claimed. Begin with checkpoint inspection and proceed through experiment 40 without asking for another launch between stages.


## Rebuild implementation declaration

{
  "policies": [
    "maintain",
    "unpruned",
    "same",
    "indexed"
  ],
  "caps": {
    "entries": 500000,
    "transitions": 2000000,
    "dominance": 5000000,
    "index": 5000000,
    "auxiliary": 500000,
    "native_per_solve": 500000,
    "scalar_cells": 4096,
    "native_cells": 4096,
    "native_seconds": 30,
    "audit_seconds": 45,
    "batch_seconds": 900,
    "cumulative_entries": 500000,
    "cumulative_transitions": 2000000,
    "cumulative_dominance": 5000000,
    "cumulative_index": 5000000,
    "scalar_evaluations": 2000000,
    "cumulative_native": 2000000,
    "wall_seconds": 120
  }
}

Original unpruned recurrence and first-transition tie behavior are fixture-compared with stage 35. Same-slope order is (S,W,-P,M,raw-ID). Endpoint order is (W,-value(a),-value(b),S,M). Indexed queries use descending endpoint-a ranks and prefix maxima of (endpoint-b value,-canonical position,witness-ID); unreachable values are explicit nulls. Raw rows, predecessor IDs, every deletion, coordinates, query outcomes and terminal tree aggregates are retained. The independent checker reconstructs every generation domain, index range and deletion. Auxiliary memory guards conservatively reserve sorter/order/map/tree/query records before allocation; these guard details may differ from the unavailable prior implementation.

All policy workers are isolated fresh Python processes. Each pays for its own cold native initial and replacement solves, recognition, construction, horizons, scalar repair, driver bookkeeping and certificate handling. Model time is independent of CPU. Native stores are disposed even on failure. Retained output-proof disposal is outside the CPU boundary for every method. Interpreter/import/input decoding, logical fingerprinting, serialization and audits are separate infrastructure costs. Operation ledgers place horizons at their anchors and construction at its actual build time. CPU bookkeeping is tracked within its operation blocks; final accounting overhead is disclosed as a separate component. Timing uses median aggregate full CPU over the exact three declared repetitions and never the fastest trial. Capped repetitions are ineligible. No held-out tuning.

Construction caps preserve partial proof/cursor, abandon it as active evidence and use a complete scalar partition, repricing stale numerators before its horizon. A later rolling build failure permanently hands that policy to scalar maintenance. All failed preparation is charged. Incomplete constructions remain incomplete even when fallback finishes the window. Each complete rolling window rebuild starts from the original items. At a strict loss on a boundary, native replacement precedes the new build. No fifth build at 1024.

Same-slope correctness: at any prefix a lighter state with equal S and no smaller P admits every identical remaining completion and has a constant nonnegative value difference. Induction through the complete include/exclude recurrence therefore preserves global optima for all nonnegative times. Endpoint correctness: a lighter state's affine value difference nonnegative at both a and b is nonnegative throughout [a,b], so the same completion argument preserves the global optimum only there. Discarded states can be necessary later. These elementary arguments and exponential worst-case widths are separate from checked finite proofs and empirical CPU observations. No new arithmetic is claimed.
