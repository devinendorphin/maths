# OpenAI mathematics review: implications for temporal proof reuse

Reviewed 8 October 2026. The starting point is OpenAI's [6 October release](https://openai.com/index/sharing-ai-progress-in-mathematics/), with the accompanying collection pinned to commit `fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb`. The research baseline is our completed [experiments 86–95](../research86/Synthesis.md), not the earlier count of 85. This review proposes changes; it does not add completed experiments.

The useful connection is **stronger checking of reusable evidence and more precise claims about its scope**. The collection supplies methodological ideas for our existing question: how an answer's stability, a proof's applicability, and the total cost of maintaining that proof relate. It does not establish that our combined implementation is new, or that it has already been reproduced elsewhere.

## Coverage and versions

The pinned [catalogue](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/CONTENTS.md) contains 719 manuscripts in 372 families. I screened all family descriptions and individual-paper abstracts, then inspected selected source sections, verifier code, and formalization scope notes. The direct strings `knapsack`, `parametric`, `dynamic programming`, `reoptimization`, and `ski rental` had zero family hits. This is a catalogue-level search result, not a full-text absence claim or novelty clearance.

The [repository description](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/README.md) distinguishes different verification stages. The [7 October history](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/history.md) records three withdrawals from a shared sign error, repairs to 14 other manuscripts, and citation changes in 13 dependents. Those revisions make version and dependency tracking particularly relevant. Numbers here describe this snapshot, not a timeless inventory of independently established results.

I also read the release summaries for [Ten advances in mathematics](https://openai.com/index/ten-advances-in-mathematics/) and [Our First Proof submissions](https://openai.com/index/first-proof-submissions/), and screened the August collection's abstract and contents. They provide context rather than a direct optimizer replacement. The February account describes a submitted answer later judged incorrect, reinforcing the need to separate generated arguments from accepted evidence.

No OpenAI verifier, Lean proof, or Comparator run was executed in this review. Source inspection is distinct from independent reproduction. The [source receipt](OpenAI-review-sources-2026-10-08.json) records access levels and pinned paths.

## 1. Check the intended statement, not just a proof-shaped artifact

[Comparator](https://github.com/leanprover/comparator/blob/ca04cfc72b550331658ec314bf47685281bfd4bf/README.md), originally developed by Lean FRO, compares a solution against a separately trusted challenge. Under its stated trust and execution assumptions, it checks statement/declaration agreement, permitted axioms, and kernel acceptance. Definition holes require additional semantic review. A `sorry` in a challenge specifies an unproved target; it is not the purported accepted solution.

The collection's [family 266 scope note](https://github.com/openai/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/lean/docs/266.md) gives a concrete example. The paper's headline is a maximum of three mutually unbiased bases in dimension six. One selected formalization proves at most five and a Fourier-vanishing statement; it does not prove the headline exclusion of four arbitrary bases. Another selected statement is a supporting cancellation lemma. This is a documented difference in coverage, not my determination that the headline is false.

**Application to our project:** maintain a claim ledger distinguishing a point optimality certificate, an interval connector, model-to-certificate translation, and the running cache implementation. Our VIPR checks establish bounds for encoded point problems. They do not by themselves kernel-check the continuum argument or the Python admission/cache code. A future Lean result should identify precisely which of those obligations it proves.

The first small formal target should be our [affine endpoint guarantee](../research86/Mathematical-guarantees.md): one fixed feasible set, one feasible candidate, unchanged affine coefficients, and valid endpoint bounds imply an interpolated regret bound for every interior point. Zero endpoint gaps give optimality throughout. Freeze those definitions and hypotheses independently before proof construction. Then connect rational endpoint encodings to the declared coefficients and candidate. This is a manageable bridge; importing the entire OpenAI library would add substantial unrelated machinery.

## 2. Let discovery be flexible; require exact admission

The [Exact Fourier certificates companion](https://github.com/openai/math/tree/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/preprints/Exact-Fourier-certificates-for-complex-Hadamard-matrices-of-order-six-September-24-2026) is a closer methodological match than its quantum subject suggests. Its verification section and included program use integer/rational identities and exact positivity checks. Modular elimination helps obtain candidate reconstruction data; final rational identities supply the certificate. The reasoning does not require every unknown moment to be rational. A checksum wrapper fixes the verifier's bytes, but the mathematical inequalities do the proving.

**Application to our project:** distinguish finding a proof from admitting it. Fast proposals may use heuristic choices, modular calculations, or approximate suggestions if the eventual checker validates the exact witness against the original problem. A compact certificate can retain the facts needed for replay while detailed search diagnostics stay in an archive. This is an established proof-production pattern, not a new principle invented in that paper or here.

For our scalar certificates, complete feasible-space coverage remains essential. The Fourier argument can safely omit some equations because its surviving identities already imply a contradiction; that does not authorize dropping required knapsack cells. Certificate simplification must preserve our own sufficiency argument. Before building another custom system, compare the adapter with the CP 2024 certifying-DP work and the existing VIPR/VeriPB options identified in the [novelty audit](Novelty-audit-2026-10-08.md).

## 3. A terminating certificate search need not be affordable

The [Computing the Random 3-SAT Threshold](https://github.com/openai/math/tree/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/preprints/Computing-the-Random-3-SAT-Threshold-September-27-2026) certificate and assembly sections combine computable lower bounds with enumerable upper-bound witnesses. Fair enumeration and strict interval-certified inequalities eventually produce a narrow enclosure under stated mathematical premises. The argument establishes termination, not an efficient running-time bound. I inspected this generic certificate-search argument, not every SAT-specific premise supplying its witnesses.

**Application to our project:** separate soundness, eventual completion, and resource limits. A stopped build may preserve sound partial bounds without certifying an optimum. Failure to find a witness before a cap is not evidence that one does not exist. Explicit statuses should retain that distinction and charge failed attempts and fallback. This strengthens the earlier partial-frontier discipline rather than requiring us to reproduce the SAT result.

The family's catalogue also explicitly credits Gaia Carenini's concurrent work for threshold-existence priority. That is a useful model for our novelty reporting: distinguish a first result, an alternative proof, an implementation, and a new measured advantage. This review does not independently adjudicate that priority.

## 4. Online cost theorems require a matching cost model

The [uniform k-server companion](https://github.com/openai/math/tree/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/preprints/Uniform-computation-of-the-squared-logarithmic-k-server-bound-September-24-2026) separates movement competitiveness from decision computation. Its introduction and scheduling section explicitly allow an enormous finite additive movement constant. Construction activates at `2^T_P - 1`, where `T_P` is the constructor's finite running time. Polynomial preprocessing and per-request bit bounds therefore do not guarantee useful activation on a practical horizon. The existence theorem is a mathematical dependency, not an independently re-proved result in this review.

**Application to our project:** a formal asymptotic statement can coexist with poor finite-sequence performance. Our cache renewal problem does not supply the same metric, adversary, or movement objective. We cannot import the k-server competitive ratio as a CPU guarantee. Keep the existing dense/sparse comparisons and account for preparation, required checker CPU, failed builds, renewals, and reuse checks. A proposed theorem must say what is charged and constrain any additive term.

The catalogue's one-sample matroid prophet result is also an unsuitable direct shortcut: it assumes independent nonnegative values and matroid feasibility. General knapsack feasibility and our signed, coordinated trajectories do not meet those assumptions. That judgment is based on the stated scope; its full proof was not reviewed.

## Consequences for the inquiry

The existing distinction between answer stability and certificate expiry remains productive. The new release strengthens the case for proving the connector and specifying its trust boundary before expanding the model or tuning more gates. It also suggests a practical engineering improvement: reduce discovery to compact exact witnesses, with versioned dependencies and explicit admission rules.

For model-independent theorem or checker updates, extend our model-epoch discipline to a dependency ledger: a receipt should identify the rules, definitions, verifier, and checked model it depends on. Hashes identify bytes; they do not establish correctness, authenticate an untrusted producer, or eliminate a semantic error in a dependency. A changed dependency needs an explicit compatibility argument or re-admission.

The most promising contribution remains the integrated interval-proof method under bounded construction and full verification accounting. A useful finding would demonstrate either a precise proof-format capability missing from close baselines, fewer checked proof steps/bytes with the same obligations, or a cost advantage under declared assumptions. Formalizing an elementary endpoint lemma improves assurance; it does not make that lemma mathematically novel.

The [proposed experiments 96–100](Roadmap-after-OpenAI-review.md) prioritize those questions. They preserve the fixed-feasibility signed-affine model and the existing strong baselines. The release does not provide a reason to abandon our trajectory, and this targeted review cannot establish world priority for it.
