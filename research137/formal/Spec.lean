import Flow

/-- Explicit contract: every competitor obeys the same node balances and bounds.
    The statement uses the named incidence/balance definitions, not an assumed
    equality between objective values or an assumed potential-cancellation law. -/
def ExpectedCertificateSoundness : Prop :=
  ∀ (nodes edges : Nat) (src dst : Nat → Nat)
    (lower upper supply cost candidate prices : Nat → Rat),
    (∀ e, e < edges → src e < nodes) →
    (∀ e, e < edges → dst e < nodes) →
    (∀ e, e < edges → lower e ≤ candidate e ∧ candidate e ≤ upper e) →
    (∀ v, v < nodes → Allocation.balance edges src dst candidate v = supply v) →
    (∀ e, e < edges →
      (candidate e < upper e → 0 ≤ cost e + prices (src e) - prices (dst e)) ∧
      (lower e < candidate e → cost e + prices (src e) - prices (dst e) ≤ 0)) →
    ∀ alternative : Nat → Rat,
      (∀ e, e < edges → lower e ≤ alternative e ∧ alternative e ≤ upper e) →
      (∀ v, v < nodes → Allocation.balance edges src dst alternative v = supply v) →
      Allocation.value edges cost candidate ≤ Allocation.value edges cost alternative

theorem checked_contract : ExpectedCertificateSoundness := by
  intro n m src dst lo hi b cost x pi ht hh bounds balances signs y ybounds ybalances
  exact Allocation.certificate_sound n m src dst lo hi b cost x pi ht hh
    ⟨bounds, balances⟩ signs y ⟨ybounds, ybalances⟩

/-- Without reverse signs, x=1 can be worse than y=0 on a positive-cost edge. -/
theorem missing_reverse_counterexample :
    ¬((1 : Rat) < 1) ∧ 0 ≤ 0 ∧ 0 ≤ 1 ∧ (1 : Rat)*(0-1) < 0 := by grind

/-- Different balances invalidate cancellation: c=-1, pi_tail=1, pi_head=0,
    reduced cost zero, but increasing the flow from 0 to 1 reduces cost. -/
theorem missing_balance_counterexample :
    (-1 : Rat)+1-0 = 0 ∧ (-1 : Rat)*1 < (-1)*0 := by grind

/-- c=(0,2); separately changing c1 to 2 or c2 to 0 ties; both loses. -/
theorem independent_ranges_do_not_compose :
    (2 : Rat) ≤ 2 ∧ 0 ≤ 0 ∧ ¬(2 ≤ 0) := by decide

#print axioms checked_contract
#print axioms missing_reverse_counterexample
#print axioms missing_balance_counterexample
#print axioms independent_ranges_do_not_compose
