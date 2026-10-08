# Conditional guarantees for experiments 86–95

These are elementary deductions about declared models, stated before running the experiments. Their originality is assessed separately in the novelty audit; these arguments do not reconstruct Allen Brooks's unpublished work. A finite test checks an implementation or assumption; the arguments below, rather than those tests, justify the general statements. Independent numerical checks and VIPR are not themselves claimed formally verified.

## 1. Affine endpoint certificates extend over an interval

Let F be one fixed nonempty feasible set, and let f(x,t)=p(x)+t v(x). Fix a feasible candidate x and interval [a,b], a<b. Suppose verified endpoint upper bounds U_a,U_b bound every feasible objective, with candidate endpoint gaps δ_a=U_a−f(x,a) and δ_b=U_b−f(x,b), both nonnegative.

For t=(1−λ)a+λb, every competitor y satisfies

f(y,t)−f(x,t) = (1−λ)[f(y,a)−f(x,a)] + λ[f(y,b)−f(x,b)] ≤ (1−λ)δ_a+λδ_b.

Taking the maximum over y proves the additive-regret bound for x throughout the interval. The uniform bound max(δ_a,δ_b) follows. If both gaps vanish, x is exactly optimal throughout; ties are allowed. This does not require the same endpoint solver to select x, provided x is feasible and attains the verified bound at each endpoint.

The feasible set and the affine coefficients must describe the same model at both endpoints and in between. This guarantee does not follow merely from similar labels, approximate numerical equality, or point proofs for different models. It extends to affine dependence on several parameters when the parameter region is a known convex hull and matching bounds are available at every vertex, with barycentric-weighted gaps. That multiparameter extension is stated algebraically, not benchmarked in this batch.

## 2. A bound survives a known restriction of feasibility

At a fixed objective/time, suppose a verified upper bound U holds on F and x∈F attains U. For a new feasible set F'⊆F, if x∈F', every competitor in F' still has objective≤U, and x remains optimal.

For fixed nonnegative integer weights and unchanged profits/slopes, lowering capacity establishes the subset relation directly. Checking that the candidate still fits is essential. Raising capacity establishes no such relation and can introduce a better packing. The experiment uses a dedicated capacity-subset connector; ordinary exact-model cache matching remains conservative and rejects changed models.

Across a time interval, subset transfer additionally needs the candidate to remain feasible at every time and a valid original interval certificate. Endpoint feasibility by itself is insufficient for arbitrary interior capacity changes. The implemented tests are fixed-time transfers, not a generic proof for changing constraints over a continuum.

## 3. Bounded curvature gives an error bound, not automatic exact reuse

For quadratic objectives f(x,t)=p(x)+t v(x)+t² a(x), each binary packing selects items with coefficients a_i. Let S=Σ|a_i|. For any competitor y and candidate x, the quadratic coefficient of d_y(t)=f(y,t)−f(x,t) is Σ a_i(y_i−x_i)≥−S. Thus

d_y(t) ≤ (1−λ)d_y(a)+λd_y(b)+S(t−a)(b−t).

Verified endpoint gaps imply the uniform-in-competitor bound

max_y f(y,t)−f(x,t) ≤ (1−λ)δ_a+λδ_b+S(t−a)(b−t).

For a=b use the point bound; this batch uses positive-length intervals. The added curvature term has maximum S(b−a)²/4. The exact uniform maximum of the combined concave quadratic can be found at its vertex or an endpoint.

If certified endpoint margins m_a,m_b bound every *other* competitor below x, replace endpoint gaps by −m_a,−m_b in the expression. If its maximum over the interval is≤0, x is exactly optimal throughout. This sufficient criterion can be conservative. The batch computes margins exhaustively on small instances and independently checks all competing quadratic extrema.

A counterexample has capacity one, candidate value1 and competitor8t−4t² on [0,2]. The candidate wins at both endpoints but loses by3 at t=1. S=4 bounds that interior loss by4. With candidate value10, endpoint margins10 make the same curvature correction sufficient to certify exact reuse. These examples establish why the affine argument cannot simply be applied to a nonlinear model.

The inequality more generally follows if every difference has second derivative≥−2S; the batch only implements explicit quadratics, not arbitrary nonlinear functions or automatic curvature estimation.

## 4. Certificate failure can precede loss of optimality

The unchanged native scalar certificate partitions feasible binary packings into cells with fixed/free masks, residual capacity r and rational nonnegative price a/b. At integer time t each cell has numerator

N(t)=b Σ_fixed q_i(t)+a r+Σ_free max(0,b q_i(t)−a w_i).

Its floor N(t)/b bounds every feasible packing in that cell. Complete disjoint coverage and candidate feasibility make the certificate sufficient whenever every cell bound is≤candidate value.

Each difference N(t)−b f(x,t) is convex piecewise affine. Its valid sublevel set containing0 is an interval. A nonpositive eventual slope gives validity for every nonnegative integer time; otherwise the first failure is found by exact exponential/binary search. A complete cover cannot continue certifying x after a feasible competitor strictly beats x. Therefore first certificate failure≤first strict answer loss whenever a strict loss exists.

For an initially optimal candidate with intercept P and slope V, each competitor A+tB with B>V first strictly beats it at floor((P−A)/(B−V))+1. The minimum over a complete feasible-line set is the true integer loss time; no such competitor means no future strict loss. Ties do not count as loss. The batch independently enumerates all feasible competitors and reprices all cells at observation and boundary times.

Proof failure and answer loss are different. In particular, multiplying the whole objective by a positive common factor preserves its optimizer forever, while an unnecessarily fixed scalar price can cease to certify it. Scaling the proof appropriately can avoid that failure; the fixed-price experiment measures a particular certificate, not an inherent need to rebuild all proofs.

## 5. Reuse saves work only under a cost inequality

Given a complete affine envelope with M positive-length optimal intervals covering [a,b], there are M+1 distinct endpoints. With a checked objective bound cached at each endpoint, feasibility/value checks can support both neighboring packings at a shared boundary. This counts point-bound checks; it does not eliminate discovering the envelope or proving each new bound.

Let B be all preparation/discovery/proof/checking cost and R_j all incremental lookup, integrity, primal and output cost for observation j. Let C_j be a complete independent solve/proof/check cost for that observation. Reuse is cheaper on that sequence exactly when B+Σ R_j<Σ C_j, under a common accounting boundary. If costs are fixed R,C and C>R, the break-even number of observations is the smallest integer N with N>B/(C−R). Variable-cost measurements cannot be turned into that constant-cost guarantee without the extra assumptions.

The experiments charge curve discovery, native construction/cleanup/disposal, proof translation and file writing, required checker child CPU, metadata/hashing, feasibility/value checks and output construction. Independent validation, result JSON, deliberately invalid proof tests and archive work are outside the algorithm timing. CPU sums across parent/child processes are measured work, not wall latency. Deduplicating archived proof bytes does not share algorithm state between workers or skip their required checker executions.

For q_i(t)=(1+αt)p_i with a positive factor throughout the interval, a verified base optimum remains optimal by multiplying every competitor inequality by that positive factor. The guarded `factor` method uses this established shortcut where applicable and otherwise performs the ordinary envelope method. A zero or negative factor anywhere rejects this shortcut; it does not authorize carrying a maximum proof through a sign reversal. This is an implementation/performance control, not a new test of the invariance theorem.

Exact envelopes and native proof generation can still be expensive, with exponential complexity on general knapsack inputs. The conditional cost inequality provides no universal inexpensive optimizer.

## 6. Integrity and mathematical applicability are separate checks

The guarded point receipt records the declared model, exact time, objective/primal, SHA-256 of proof bytes and frozen checker binary, and a hash seal of those metadata fields. Its narrow adapter accepts a canonical original-problem prefix before checking the proof. Reuse confirms the context, primal feasibility/value, metadata seal, unchanged bytes and checker identity, and the original problem prefix.

A receipt seal is a consistency checksum, not a signature. The contract trusts admission and the fixed checker snapshot; it does not authenticate an adversarially compromised process or caller. Explicit rewrites of metadata plus its seal are also tested against the actual proof's problem prefix. Concurrent replacement and signed provenance are not covered. Model epochs invalidate ordinary cache entries; returning to an exactly identical model/time may safely find its old entry.
