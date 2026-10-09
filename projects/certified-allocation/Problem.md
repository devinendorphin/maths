# A larger problem: affordable, auditable allocation as needs change

**How can people keep a resource-allocation plan feasible, explainable and provably optimal for their stated priorities when costs, supplies and needs change—without paying for a complete new solve every time?**

The first application family is a network moving one kind of scarce unit from suppliers to recipients: food units, appointment slots with eligibility edges, transport capacity or another appropriately homogeneous resource. It can begin with a household-sized example, then move to a cooperative or public-service network. Those applications require their own modelling and stakeholder validation. Multiple coupled commodities, nutrition, staffing rules and scheduling can require a more general model; a simple flow formulation does not silently cover them.

People choose eligibility rules, service commitments, priorities and acceptable tradeoffs. Mathematics checks what follows from those choices. An optimum does not prove that an objective is fair, that the data are accurate, or that a plan ought to be imposed. Quantifying unmet need and returning a reason for failure can be as useful as finding a low-cost allocation.

## The tractable starting model

A directed graph has integer node supplies/demands `b`, lower commitments `l` and edge capacities `u`. A flow `x` must satisfy `l[e] <= x[e] <= u[e]` and outgoing minus incoming flow `= b[v]` at every node. Costs may be signed rational affine functions of several parameters. Minimize the sum of cost times flow. Integer data admit integral optimal flows in the ordinary network model; adding arbitrary extra fairness or multi-commodity constraints can lose that property.

Fairness begins as explicitly chosen service floors and eligibility rules. A later layer can examine max-min coverage, shortfall reporting and Pareto tradeoffs between policy objectives. That layer needs separate mathematical definitions and human evaluation; it is not implemented by relabelling a cost minimum “fair.” If commitments cannot be met, seek an independently checked cut/infeasibility witness or explicitly report the unsupported case. A rejected old flow is not itself an infeasibility proof.

## Why this follows from the existing inquiry

A feasible flow has a small optimality certificate: a potential for each node. Write `r[e] = c[e] + pi[tail] - pi[head]`. Check `r[e] >= 0` whenever the edge has forward residual capacity, and `r[e] <= 0` whenever it has reverse residual capacity. These signs imply that every feasible alternative has at least as much cost. [Mathematical-core.md](Mathematical-core.md) gives the argument.

For fixed flow, capacities and potentials, affine cost changes produce a convex region of certificate applicability. The plan's true optimality region can be larger: a different potential can certify the same plan. Changes in supplies or capacity can invalidate feasibility even if all cost inequalities look unchanged. This preserves the distinctions between answer stability, proof applicability and maintenance cost, while giving a polynomially solvable base problem with potentially practical scale.

Checking takes `O(V+E)` exact arithmetic operations and stores `O(V+E)` numbers; bit complexity depends on coefficient lengths. That is a mathematical operation count, not a measured runtime or memory claim. General minimum-cost flow is established. The research target is the **complete cost of maintaining applicable certificates and user commitments under explicit changes and resource limits**.

## The substantial research question

Develop and characterize a procedure that chooses among rechecking a captured certificate, repairing its potentials, repairing the flow, or solving afresh. Include feasibility changes, failed repair attempts, proof construction/checking, I/O, dependency scope, storage, and the human-readable account of unmet commitments. Under a stated update model, seek a bound or a reproducible regime where total maintenance is cheaper than repeated exact solving; also identify sequences where no saving is available.

The update model must be explicit: fixed graph with at most `k` declared changed edges/nodes per step, coefficient bit lengths, admission assumptions, certificate/cache budget and required assurance. Arbitrary adversarial updates may remove every reuse advantage. A bound for one class must not be advertised as a guarantee for all changing allocation problems.

There are four useful scales of contribution:

| Scale | Useful deliverable | Evidence required |
|---|---|---|
| A person learning or planning | A small example, exact explanation of tradeoffs, checker runnable with the Python standard library | Independent enumeration and invalid controls; clear distinction between explanation and policy recommendation |
| A cooperative or local service | Audited updates to a modest network, service-floor and shortage reporting | Separately agreed model/data, full solve/repair comparisons and resource budgets |
| Larger public networks | Efficient verified certificates and explicit fallback when updates exceed budget | Frozen larger suites, controlled deployments, meaningful external checking and memory/accounting coverage |
| Mathematical/computational research | A precise certificate-maintenance theorem, lower bound or reproducible empirical contribution | Primary-literature comparison, assumptions, independently inspectable proofs and replication |

## First bounded research stages

1. Establish the static exact-flow and potential checker against an independent solver, including false costs, flows, capacities, potentials and infeasibility controls. The supplied worked example is a four-edge illustration, not this general benchmark.
2. Freeze a modest graph suite with separately held-out update sequences. Compare full cold solving, warm solving, captured-potential recheck, potential repair and flow repair under identical feasibility/cost contracts.
3. Add human-specified service-floor changes and a distinct max-min or Pareto formulation. Account for incomplete/failed work; do not transfer a scalar-cost certificate to a different fairness objective without proof.
4. Derive an update/storage-dependent maintenance bound or counterexample. Compare with primary dynamic-flow, sensitivity, robust optimization and certificate-maintenance literature before making an originality claim.

No large benchmark or new general theorem is claimed today. [Worked-example.json](Worked-example.json), [worked_example.py](worked_example.py) and [applicability.png](applicability.png) make the starting question concrete. [Literature.md](Literature.md) records established ingredients and the remaining literature work.
