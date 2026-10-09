# What the checked statements mean

An optimality certificate binds a concrete model digest, frozen dependency
context, integer flow, node potentials and exact cost numerator. The positive
integer model denominator determines the rational objective. The independent
checker checks bounds, balances, objective and all residual reduced-cost signs.
A cut certificate checks b(S) > sum(u on outgoing edges) - sum(l on incoming
edges). Summing conservation across S proves that no feasible flow can meet such
a condition. Finite capacities prevent unbounded objectives in this domain.

The checker admits only the explicit network schema. It rejects nonlinear
objectives and noninteger flows/bounds. Signed rational costs are represented as
integer cost units divided by a common denominator. It does not handle arbitrary
side constraints, changing code semantics or coupled commodities. Model/data
truth and policy desirability are outside optimality admission.

Native feasibility repair clips a prior flow to current bounds and sends residual
imbalances through an auxiliary max-flow network. Optimization cancels negative
residual cycles; a final exact shortest-distance pass supplies potentials.
NetworkX supplies a different optimization algorithm. Its cold answers receive
separately constructed potentials, and its infeasibility answers receive native
cut completion. Those completion costs are charged; these are not certificates
emitted by NetworkX. Invalid controls rebind changed models where appropriate so
capacity/balance controls do not rely only on stale digests.

The audit independently reimplements flow/cut evaluation and network-simplex
encoding, and exhaustively enumerates static/fairness fixtures. It is an
algorithmically separate audit, not independent human authorship, a proof
assistant verification, or an independent dependency installation. Larger test
graphs rely on NetworkX plus certificate checking; exhaustive enumeration is
confined to tiny cases. The prior Lean endpoint lemma does not formally verify
this Python code.

Admission is immutable captured evidence in a specified context. A changed model
is explicitly rechecked or recertified. Startup source hashes and a preflight
reference-module hash check detect mismatches at those points. A dependency-ID
control tests refusal of a different context. This does not continuously monitor
external files or arbitrary runtime code changes. Inter-query hidden changes
outside the trusted model/delta interface are outside the contract.

Fairness bundle admission covers the fixed two-supplier/three-recipient schema:
all strictly higher attainable coverage candidates have valid infeasibility cuts,
and the selected floor has a valid minimum-cost flow. Because integral service
ratios are among {i/d[r]}, exhaustive descending candidates certify the maximum
minimum ratio. The final scalar certificate certifies cost only *within that
floor*. A scalar certificate for the original problem alone does not establish
max-min optimality. This is max-minimum coverage with a cost tie-break, not full
lexicographic max-min fairness, stakeholder consent or a generic fairness claim.

Replication retains every logical field, source/model/dependency/proof digest,
primal and potential, cut, operation count, failed probe, eviction decision and
exit state. Replication.json lists the excluded timing/kernel observations and
their reason. Both numerical measurement sets remain archived. No meaningful
disagreement was excluded; all compared mathematical records matched exactly.
