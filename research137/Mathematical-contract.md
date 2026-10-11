# What sparse admission proves

Initial full admission checks an integral feasible flow x and an exact potential
pi against the whole fixed network. For every residual forward edge the reduced
cost c[e]+pi[a]-pi[z] is nonnegative; for every reverse residual edge it is
nonpositive. Summing reduced cost against any feasible flow difference cancels
the conserved potential terms and proves nonnegative objective difference.

With topology, bounds, balances, denominator, flow and potentials fixed, a
complete list of k changed costs only affects those k reduced costs. Check their
residual signs, and update the exact objective numerator by
sum((new-old)*x[e]). Unchanged inequalities continue to hold. Accepted admission
therefore takes O(k) arithmetic operations plus O(k) delta encoding, with
bit-length-dependent arithmetic costs; it does not call whole-model hashing,
full export or the full checker on the noncompacting accepted path.

This implementation captures caller data by copying at admission. It validates
all message entries and prepares the bounded journal record before committing
cost changes. Refused messages and sign-failed probes leave the admitted state
unchanged. A failed sign can mean an old potential failed even if the old plan
remains optimal. The route makes no further inference: it charges a fresh
NetworkX solve and exact certificate completion/admission for the changed model.

Model binding between snapshots consists of the admitted base plus sequenced
complete deltas in the same dependency context. A full exported certificate is
bound to the current concrete model's SHA-256 digest. A transient internal
captured proof does not pretend its base digest is the current model digest.
This is an owned state interface, not protection against arbitrary code that
reaches into Python internals or an omitted authoritative update.

Let B be the live serialized journal budget and J the sum of accepted delta
record bytes. Every overflow recaptures the complete admitted base, requiring
O(V+E) arithmetic/serialization work. With bounded-size records <= B, overflow
frequency is controlled by J/B up to endpoint slack; records larger than B
each force an immediate recapture. Failed admission also triggers full fallback.
The resulting conditional accounting is initial admission + accepted k-sized
checks + full recaptures + rejected probes/solver completions + demanded exports
and restart replay. There is no unconditional sublinear session guarantee.

The primary 4 KiB sessions never overflowed their live journal because recertifying
failed probes reset it first. The 64-byte controls do overflow: all 115 accepted
updates compact. Thus this experiment exercises compaction correctness/cost,
but does not identify a general budget crossover or optimal snapshot interval.
The evidence journal retains history on disk and is outside the live byte budget.

Restart first binds and fully checks the base, verifies every record's chain,
version, exact old cost and maintained sign/value conditions, then fully checks
the exported terminal proof. A trusted terminal (version, head) detects rollback
to an otherwise internally valid prefix. Without that external anchor a valid
prefix is indistinguishable from an intended earlier checkpoint. Hash chains are
integrity devices, not source authentication or new cryptographic results.

Residual optimality, sensitivity, simplex solving, hash chains and checkpointing
are established ingredients. This supplies a measured explicit interface and
its boundary controls, not a new general optimization theorem or a formal
verification of the Python implementation.
