import Endpoint

/-- Independently written contract; no free definition holes or added assumptions. -/
def ExpectedIntervalRegret : Prop :=
  ∀ {A : Type} (feasible : A → Prop) (base slope : A → Rat)
    (candidate : A), feasible candidate →
    ∀ (left right query leftGap rightGap : Rat),
    left < right → left ≤ query → query ≤ right →
    (∀ competitor, feasible competitor →
      base competitor+left*slope competitor ≤ base candidate+left*slope candidate+leftGap) →
    (∀ competitor, feasible competitor →
      base competitor+right*slope competitor ≤ base candidate+right*slope candidate+rightGap) →
    ∀ competitor, feasible competitor →
      base competitor+query*slope competitor-(base candidate+query*slope candidate)
        ≤ (1-(query-left)/(right-left))*leftGap+((query-left)/(right-left))*rightGap

theorem checked_contract : ExpectedIntervalRegret :=
  TemporalProof.affine_interval_regret

-- Two excluded hypotheses have concrete counterexamples, proved by kernel computation.
theorem nonlinear_counterexample :
    (1 : Rat) > 0 ∧ 1 > 8*2-4*2*2 ∧ 1 < 8*1-4*1*1 := by decide
def variesFeasible (competitor : Bool) (t : Rat) : Prop :=
  competitor = false ∨ t = 1
def variesValue (competitor : Bool) : Rat := if competitor then 2 else 1
theorem changed_feasibility_counterexample :
    (∀ y, variesFeasible y 0 → variesValue y ≤ variesValue false) ∧
    (∀ y, variesFeasible y 2 → variesValue y ≤ variesValue false) ∧
    variesFeasible true 1 ∧ variesValue false < variesValue true := by
  constructor
  · intro y hy; cases y <;> simp [variesFeasible, variesValue] at *
    <;> decide
  · constructor
    · intro y hy; cases y <;> simp [variesFeasible, variesValue] at *
      <;> decide
    · simp [variesFeasible, variesValue]; decide

#print axioms checked_contract
#print axioms nonlinear_counterexample
#print axioms changed_feasibility_counterexample
