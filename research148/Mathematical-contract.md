# Conditional admission and repair contract

A model has directed arcs with integer lower/upper bounds, costs and balanced
node supplies. Parallel arcs have distinct stable indices and self-loop balance
contributions cancel. Lower-bound transformation subtracts a lower bound from
the tail supply, adds it at the head, and adds its cost to the constant objective.
Both cold implementations receive the same transformed model.

A valid transaction changes the stored mathematical model only after all field
identities, types, old values, bounds and final supply sum pass. Its version
advances once. An invalid transaction raises rejection before either model or
version changes; caller messages and returned snapshots are detached copies.
This is in-process atomicity, not a distributed transaction or crash protocol.
The supplied complete update is trusted; version/model binding cannot discover
a change omitted from an external system. No packet changes arc endpoints,
counts, priorities' meaning or the unit denominator.

For a retained flow, clamping to each new interval yields a bound-respecting
candidate. Its imbalance is new supply minus current outflow plus inflow.
A supersource joins positive imbalances; negative ones join a supersink.
Original residual arcs permit increasing/decreasing flow within the new bounds.
An augmenting maximum flow repairs all imbalances when feasible. If it cannot
send the required amount, its reachable original-node set is a shortage witness.
Admission checks supply on that set exceeds outgoing upper capacity minus
incoming lower bounds. The checker, not the producer's status, decides admission.

A feasible integer flow is admitted as optimal only with integer potentials
whose forward residual reduced costs are nonnegative and backward residual
reduced costs are nonpositive. With reduced cost c + pi(tail) - pi(head), every
feasible circulation difference has nonnegative objective change; potential
terms cancel by node balance. Thus this exact sign witness certifies the cost
minimum over the stated finite model, including negative costs and self-loops.
Negative-cycle cancellation is an established way to obtain such a witness,
not a claimed new algorithm. Its declared finite guard can interrupt optimization;
that triggers a charged cold solve and independently admitted output.

The full guard attempts these same checks on the old flow/potentials after
rebinding to the new model and recomputing its exact cost. It must include changed
balances and newly opened residual directions when lower/upper bounds change.
An old optimum or old potential alone is insufficient. Guard failure admits
nothing and its work remains charged. Shortage cuts are not silently reused:
each new model is solved/checked. A pre-shortage feasible flow can be retained
only as a repair hint, never as a certificate for the infeasible model.

This proof contract concerns feasibility and explicit integer cost priorities.
It provides no consent, fairness, policy validity, power-loss durability, bounded
worst-case speed advantage or optimizer-tree maintenance guarantee.

Admission applies to a produced exact witness; producer completion is established
for the executed streams and controls. The checker allows arbitrary Python
integer supplies, while the native cold binding accepts signed 64-bit supplies.
Its measured inputs fit that range. The present bridge does not promise native
completion for every model in the wider checker domain, or suppress external
solver/input exceptions as successful answers.
