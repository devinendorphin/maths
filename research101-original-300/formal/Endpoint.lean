import Std

namespace TemporalProof

/-- The coefficients and feasible predicate stay fixed throughout the interval. -/
theorem affine_endpoint_regret {α : Type} (F : α → Prop) (p v : α → Rat)
    (x : α) (_hx : F x) (a b da db l : Rat)
    (h0 : 0 ≤ l) (h1 : l ≤ 1)
    (ha : ∀ y, F y → p y + a * v y ≤ p x + a * v x + da)
    (hb : ∀ y, F y → p y + b * v y ≤ p x + b * v x + db) :
    ∀ y, F y →
      p y + ((1-l)*a+l*b)*v y - (p x + ((1-l)*a+l*b)*v x)
        ≤ (1-l)*da+l*db := by
  intro y hy
  have h01 : 0 ≤ 1-l := by grind
  have hL := Rat.mul_le_mul_of_nonneg_left (ha y hy) h01
  have hR := Rat.mul_le_mul_of_nonneg_left (hb y hy) h0
  have hsum : (1-l)*(p y+a*v y)+l*(p y+b*v y)
      ≤ (1-l)*(p x+a*v x+da)+l*(p x+b*v x+db) := by grind
  have iy : p y+((1-l)*a+l*b)*v y = (1-l)*(p y+a*v y)+l*(p y+b*v y) := by grind
  have ix : p x+((1-l)*a+l*b)*v x+(1-l)*da+l*db
      = (1-l)*(p x+a*v x+da)+l*(p x+b*v x+db) := by grind
  grind only

theorem affine_endpoint_optimal {α : Type} (F : α → Prop) (p v : α → Rat)
    (x : α) (hx : F x) (a b l : Rat) (h0 : 0 ≤ l) (h1 : l ≤ 1)
    (ha : ∀ y, F y → p y+a*v y ≤ p x+a*v x)
    (hb : ∀ y, F y → p y+b*v y ≤ p x+b*v x) :
    ∀ y, F y → p y+((1-l)*a+l*b)*v y ≤ p x+((1-l)*a+l*b)*v x := by
  have h := affine_endpoint_regret F p v x hx a b 0 0 l h0 h1
    (by intro y hy; have := ha y hy; grind)
    (by intro y hy; have := hb y hy; grind)
  intro y hy
  have := h y hy
  grind

theorem affine_interval_regret {α : Type} (F : α → Prop) (p v : α → Rat)
    (x : α) (hx : F x) (a b t da db : Rat)
    (hab : a < b) (hat : a ≤ t) (htb : t ≤ b)
    (ha : ∀ y, F y → p y+a*v y ≤ p x+a*v x+da)
    (hb : ∀ y, F y → p y+b*v y ≤ p x+b*v x+db) :
    ∀ y, F y → p y+t*v y-(p x+t*v x)
      ≤ (1-(t-a)/(b-a))*da+((t-a)/(b-a))*db := by
  let l := (t-a)/(b-a)
  have hp : 0 < b-a := by grind
  have hn : b-a ≠ 0 := by grind
  have hm : l*(b-a)=t-a := Rat.div_mul_cancel hn
  have h0 : 0 ≤ l := by
    apply Rat.le_of_mul_le_mul_left (c := b-a) (hc := hp)
    grind
  have h1 : l ≤ 1 := by
    apply Rat.le_of_mul_le_mul_left (c := b-a) (hc := hp)
    grind
  have ht : (1-l)*a+l*b=t := by grind
  have h := affine_endpoint_regret F p v x hx a b da db l h0 h1 ha hb
  rw [ht] at h
  exact h

theorem affine_interval_optimal {α : Type} (F : α → Prop) (p v : α → Rat)
    (x : α) (hx : F x) (a b t : Rat)
    (hab : a < b) (hat : a ≤ t) (htb : t ≤ b)
    (ha : ∀ y, F y → p y+a*v y ≤ p x+a*v x)
    (hb : ∀ y, F y → p y+b*v y ≤ p x+b*v x) :
    ∀ y, F y → p y+t*v y ≤ p x+t*v x := by
  have h := affine_interval_regret F p v x hx a b t 0 0 hab hat htb
    (by intro y hy; have := ha y hy; grind)
    (by intro y hy; have := hb y hy; grind)
  intro y hy
  have := h y hy
  grind

/-- Exact positive-denominator scalar translation used by point certificates. -/
theorem scaled_affine (P V N D : Rat) (hD : 0 < D) :
    (D*P+N*V)/D = P+(N/D)*V := by
  have hn : D ≠ 0 := by grind
  have hi := Rat.mul_inv_cancel D hn
  simp only [Rat.div_def]
  grind

#print axioms affine_endpoint_regret
#print axioms affine_endpoint_optimal
#print axioms affine_interval_regret
#print axioms affine_interval_optimal
#print axioms scaled_affine
end TemporalProof
