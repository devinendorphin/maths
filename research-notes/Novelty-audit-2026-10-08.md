# Novelty audit: what the inquiry actually established

Reviewed 8 October 2026 in response to the user's concern about “no novelty claim.” This audit adds a comparison and corrects the interpretation of earlier caveats. Completed protocols, sources and results remain unchanged. The attached handoffs are historical evidence, not a present instruction prohibiting discovery.

The conclusion is **original experimental work and a potentially distinctive implementation; no established first-in-literature mathematical result yet**. “No novelty claim” means that priority has not been established. It must not be used to conclude that no novelty exists, or to prevent looking for it. Elementary ingredients can support a new algorithm, implementation or empirical contribution, but a new combination still needs a concrete comparison.

## Where the wording entered

The trace reaches the surviving 26–30 campaign, nested inside the restored 31–35 archive. Earlier full conversations and the original 36–40 detailed archive are unavailable here, so this is the earliest located occurrence, not an assertion about the first occurrence anywhere.

| Surviving source | Wording and meaning |
|---|---|
| Original 26–30 `Handoff.md`, line 42; `Synthesis.md`, line 41 | The independent model does not recover Allen Brooks's unpublished mathematics or establish a new arithmetic. The instruction is to distinguish empirical findings, guarantees and speculation. |
| Original 26–30 `Handoff.md`, line 90; experiment 29 report | “not a novelty claim” refers specifically to removing redundant representation work under a known positive common scaling factor. |
| Restored 31–35 `research/stages/31/Protocol.md`, lines 51, 274, 281; repeated in later stage protocols | Positive scaling is known; frontiers are parametric optimization constructions, not evidence of novel arithmetic. Endpoint pruning and acyclic witnesses are proved, without attributing world priority. |
| [36–40 handoff](../research36-rebuild/Handoff.md), opening paragraph | “make no claim of new arithmetic.” This is narrower than banning a novel algorithm or experimental finding. |
| [5 October literature review](Literature-review-2026-10-05.md), frontier discussion | It expressly leaves the particular endpoint-dominance test and Fenwick implementation for a further novelty assessment. |
| Same review, final discussion | Compact checked interval certificates with a cost guarantee are a research hypothesis. The review expressly says it is not an exhaustive search or novelty clearance. |
| Reports 51–85 and earlier commentary | Broad phrases such as “no novelty … is claimed” carried that caution forward. They describe the claims made, not a proved absence of originality. Treating them as a blanket negative conclusion would be an overstatement. |

The recovered 31–35 campaign is reachable through the [storage instructions](../STORAGE.md). Within its archive, `supplied/Temporal-proof-five-experiment-campaign.zip` contains the 26–30 files cited above. The lost original 36–40 has surviving summaries; the regenerated run is a separate experiment history. No source inspected shows the user instructing us to suppress a supported novelty finding.

## Claim-by-claim comparison

### Time-dependent numbers and changing optima

The implemented quantities are ordinary integers or rational numbers with explicit affine profit functions. We did not construct a new arithmetic or recover Brooks's intended definitions. Parametric knapsack and solution regions have established exact and approximate methods. The [Nemesch–Ruzika–Thielen–Wittmann survey (2025)](https://arxiv.org/html/2501.11544v1), especially sections 1.2, 3.1 and 4.5, supplies the relevant framework and the endpoint/intersection method used in experiment 51. The existence of changing answers, convex envelopes, and intervals of optimality is already covered by that framework. This comparison supports a narrow prior-art conclusion about those ingredients, not about every implementation in this repository.

### Endpoint dominance and the pruning index

At one item prefix, let state z have weight W and affine value A+tB. Map it to the vector `(−W, A+aB, A+bB)` for the declared interval [a,b]. A state at least as good in all three coordinates dominates throughout the interval: every value difference is affine, and lower weight permits the same remaining-item completions. Thus this test is ordinary three-coordinate dominance after a change of coordinates. Ties need deterministic handling; the proof does not extend beyond the interval.

The weight sweep and compressed-coordinate prefix-maximum index exploit that structure. A Fenwick tree is a standard data structure, and multidimensional maxima are an established geometric problem; see [Kung, Luccio and Preparata (1975)](https://www.eecs.harvard.edu/~htk/publication/1975-jacm-kung-luccio-preparata.pdf). This is not a claim that their paper contains our exact Fenwick code or signed-parametric proof format. The narrower potentially distinctive part is the audited record of retained feasible witnesses, deletions, index operations and interrupted construction. It needs comparison with certifying DP, rather than claiming that coordinate dominance itself was invented here.

### Independently checked dynamic-programming and dominance proofs

An especially close additional reference is [Demirović et al., CP 2024, “Pseudo-Boolean Reasoning About States and Transitions to Certify Dynamic Programming and Decision Diagram Algorithms”](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.CP.2024.9). Its [open manuscript](https://eprints.gla.ac.uk/328333/2/328333.pdf), particularly the introduction and state-merging discussion, describes a common proof system for state/transition algorithms and applies it to knapsack. Therefore “proof-producing knapsack DP” is not a first claim available to this program. Their reasoning framework is stronger precedent than the old 1969 DP citation alone.

[Jabs, Berg, Bogaerts and Järvisalo, “Certifying Pareto Optimality in Multi-objective Maximum Satisfiability” (2025)](https://arxiv.org/abs/2501.17493) also gives checked multi-objective reasoning and Pareto-dominance cuts. That is a different problem and proof representation, but it prevents treating proof-producing dominance reasoning as a generally new principle. Our exact signed-affine interval deletion format, resource controls and maintenance experiments still require a direct implementation comparison. Ordinary Python replay is not equivalent to a formally verified checker.

### Proof expiry versus answer change

The distinction is real in the implementation. Existing kinetic data structures already maintain predicates with certificates and failure events: [Basch, Guibas and Hershberger, “Data Structures for Mobile Data”](https://www.ime.usp.br/~cris/aulas/19_1_6957/BaschGH-DSforMobileData.pdf) distinguishes failures requiring certificate maintenance from changes in the maintained structure. We therefore should not claim that “a proof can expire before an answer changes” is a new general idea.

The particular scalar partition proof gives exact integer expiration times using convex piecewise-affine cell bounds, while exhaustive competitor lines give strict answer-loss times. Experiment 90 independently distinguishes these quantities, including fixed-price proofs that fail at time 1 under positive scaling despite permanent optimality. This is a concrete demonstration for this certificate format. Scaling the proof removes that artificial failure; it is not an inherent renewal lower bound. Novelty of a general expiration theorem or a better certificate representation has not been established.

### Certificates for optimization and sensitivity

[Cheung and Moazzez (2016), “Certificates of Optimality for Mixed Integer Linear Programming Using Generalized Subadditive Generator Functions”](https://doi.org/10.1155/2016/5017369), discusses optimality certificates, sensitivity analysis and computational knapsack tests. Its introduction also identifies earlier inference-duality and branch-and-bound sensitivity work. This is a close warning against claiming that reusable optimization evidence or post-solution analysis is new as a broad category. The generator-function representation differs from our scalar partition certificates; we have not proved superiority or equivalence.

[Szeider, CP 2026, “VIPR Certificate Construction from Black-Box ILP Solvers”](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.CP.2026.52), describes independently verifiable rational proof construction and evaluates it against SCIP exact mode. Our narrow native-knapsack adapter is original repository code, but general independent proof production is established. This audit reviewed that paper's abstract and scope, not its entire implementation. The production comparison remains outstanding for our experiments.

### Cost, stopping and transfer

Our record contains original observations on specified inputs: indexed pruning avoided some caps; growing windows reduced proof rows without repaying their cost; a selected gate failed to transfer; a zero renewal threshold prevented every composed build; bounded partial builds remained inactive while fallback recovered correct answers. These findings exist regardless of whether the ingredients are known. They are original finite-sample evidence, not a general algorithmic speed guarantee or a literature priority certificate.

Experiments 91–95 additionally charge discovery, proof construction, file I/O, external checker child CPU and reuse integrity checks within the comparison. Dense streams favor reuse on the declared cases; sparse observations on a matched problem reverse that ranking. The inequality “preparation plus reuse costs must be lower than repeated full costs” is accounting, not a new competitive theorem. No bound on unknown construction prices, renewals or arbitrary input distributions has been proved. Classical rent-or-buy reasoning cannot supply such a guarantee without its assumptions.

## What can responsibly be called a contribution

The current strongest description is:

> An independently audited experimental implementation of exact signed-affine knapsack certificates, connecting interval pruning and maintenance with explicitly bounded construction, safe fallback, and measured end-to-end verification cost.

It is supported by repository sources and verified evidence. Its exact combination may be distinctive; the targeted searches did not establish a prior implementation matching every feature. Failure to find one is not evidence of priority. “Possibly novel integrated method” remains an open assessment, whereas “we built and measured this implementation” is established.

The most promising next novelty test is a direct comparison with CP 2024 certifying DP and CP 2025 Pareto proof logging on the same signed-affine instances. A substantive result would need a specific advantage: fewer proof steps or bytes with equally strong checking, a supported interval format they do not provide, or a proved cost bound under clearly declared assumptions. The basic endpoint theorem, positive scaling, dominance relation, checksum binding and preparation inequality are poor standalone novelty candidates.

For future reports, use **“Novelty not yet assessed for [specific contribution]”** or **“This ingredient is established; the following implementation difference is being tested.”** Use “no new arithmetic claim” only where arithmetic or Brooks's unpublished work is actually at issue. A supported new result should be stated and checked rather than excluded by an inherited caveat.

This was a targeted primary-source comparison, not an exhaustive systematic search. Sources were read at the stated access levels; older unavailable conversations limit the historical trace. It establishes neither that all contributions are new nor that all contributions are already known.
