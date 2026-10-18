import Std

namespace Allocation

/-- Explicit finite sum: no external algebra library or opaque optimization oracle. -/
def total : Nat → (Nat → Rat) → Rat
  | 0, _ => 0
  | n+1, f => total n f + f n

theorem total_congr (n : Nat) (f g : Nat → Rat)
    (h : ∀ i, i < n → f i = g i) : total n f = total n g := by
  induction n with
  | zero => rfl
  | succ n ih =>
    simp only [total]
    rw [ih (by intro i hi; exact h i (by omega)), h n (by omega)]

theorem total_add (n : Nat) (f g : Nat → Rat) :
    total n (fun i => f i + g i) = total n f + total n g := by
  induction n with
  | zero => simp only [total]; grind
  | succ n ih => simp only [total]; rw [ih]; grind

theorem total_sub (n : Nat) (f g : Nat → Rat) :
    total n (fun i => f i - g i) = total n f - total n g := by
  induction n with
  | zero => simp only [total]; grind
  | succ n ih => simp only [total]; rw [ih]; grind

theorem total_mul (n : Nat) (a : Rat) (f : Nat → Rat) :
    total n (fun i => a * f i) = a * total n f := by
  induction n with
  | zero => simp only [total]; grind
  | succ n ih => simp only [total]; rw [ih]; grind

theorem total_zero (n : Nat) : total n (fun _ => 0) = 0 := by
  induction n <;> simp_all only [total] <;> grind

theorem total_swap (n m : Nat) (f : Nat → Nat → Rat) :
    total n (fun i => total m (f i)) = total m (fun j => total n (fun i => f i j)) := by
  induction n with
  | zero => simp only [total]; rw [total_zero]
  | succ n ih =>
    simp only [total]
    rw [total_add, ih]

theorem total_spike (n k : Nat) (p : Nat → Rat) (hk : k < n) :
    total n (fun v => if k = v then p v else 0) = p k := by
  induction n with
  | zero => omega
  | succ n ih =>
    simp only [total]
    by_cases h : k = n
    · subst k
      have hz : total n (fun v => if n = v then p v else 0) = 0 := by
        rw [total_congr n _ (fun _ => 0) (by intro i hi; simp [show n ≠ i by omega])]
        exact total_zero n
      simp only [hz]; grind
    · rw [ih (by omega)]
      simp only [if_neg h]; grind

def incidence (tail head : Nat → Nat) (v e : Nat) : Rat :=
  (if tail e = v then 1 else 0) - (if head e = v then 1 else 0)

def balance (m : Nat) (tail head : Nat → Nat) (x : Nat → Rat) (v : Nat) : Rat :=
  total m (fun e => incidence tail head v e * x e)

def value (m : Nat) (cost x : Nat → Rat) : Rat := total m (fun e => cost e * x e)

def Feasible (n m : Nat) (tail head : Nat → Nat) (lo hi b x : Nat → Rat) : Prop :=
  (∀ e, e < m → lo e ≤ x e ∧ x e ≤ hi e) ∧
  (∀ v, v < n → balance m tail head x v = b v)

def Signs (m : Nat) (tail head : Nat → Nat) (lo hi cost x pi : Nat → Rat) : Prop :=
  ∀ e, e < m →
    (x e < hi e → 0 ≤ cost e + pi (tail e) - pi (head e)) ∧
    (lo e < x e → cost e + pi (tail e) - pi (head e) ≤ 0)

theorem incidence_potential (n : Nat) (tail head : Nat → Nat) (pi : Nat → Rat)
    (e : Nat) (ht : tail e < n) (hh : head e < n) :
    total n (fun v => pi v * incidence tail head v e) = pi (tail e) - pi (head e) := by
  have ht' := total_spike n (tail e) pi ht
  have hh' := total_spike n (head e) pi hh
  have h : total n (fun v => pi v * incidence tail head v e) =
      total n (fun v => (if tail e = v then pi v else 0) -
        (if head e = v then pi v else 0)) := by
    apply total_congr
    intro v _
    simp only [incidence]
    split <;> split <;> grind
  rw [h, total_sub, ht', hh']

theorem potential_cancels (n m : Nat) (tail head : Nat → Nat) (x y pi : Nat → Rat)
    (ht : ∀ e, e < m → tail e < n) (hh : ∀ e, e < m → head e < n)
    (hb : ∀ v, v < n → balance m tail head x v = balance m tail head y v) :
    total m (fun e => (pi (tail e) - pi (head e)) * (y e - x e)) = 0 := by
  have h1 : total m (fun e => (pi (tail e) - pi (head e)) * (y e - x e)) =
      total m (fun e => total n (fun v => pi v * (incidence tail head v e * (y e - x e)))) := by
    apply total_congr
    intro e he
    rw [← incidence_potential n tail head pi e (ht e he) (hh e he)]
    have h := total_mul n (y e - x e) (fun v => pi v * incidence tail head v e)
    have hc : total n (fun v => pi v * (incidence tail head v e * (y e - x e))) =
        total n (fun v => (y e - x e) * (pi v * incidence tail head v e)) := by
      apply total_congr; intro v _; grind
    rw [hc, h]; grind
  rw [h1, total_swap]
  have h2 : total n (fun v => total m (fun e => pi v * (incidence tail head v e * (y e - x e)))) = 0 := by
    rw [total_congr n _ (fun _ => 0) (by
      intro v hv
      rw [total_mul]
      have hd : total m (fun e => incidence tail head v e * (y e - x e)) =
          balance m tail head y v - balance m tail head x v := by
        unfold balance
        rw [← total_sub]
        apply total_congr; intro e _; grind
      rw [hd, ← hb v hv]; grind)]
    exact total_zero n
  exact h2

theorem sign_term (l u c x y : Rat) (hy : l ≤ y ∧ y ≤ u)
    (hf : x < u → 0 ≤ c) (hr : l < x → c ≤ 0) : 0 ≤ c * (y-x) := by
  by_cases h : x < y
  · have hc := hf (by grind)
    exact Rat.mul_nonneg hc (by grind)
  · by_cases h' : y < x
    · have hc := hr (by grind)
      have hmul := Rat.mul_nonneg (show 0 ≤ -c by grind) (show 0 ≤ x-y by grind)
      grind
    · have : x = y := by grind
      rw [this]; grind

theorem total_nonneg (n : Nat) (f : Nat → Rat) (h : ∀ i, i < n → 0 ≤ f i) :
    0 ≤ total n f := by
  induction n with
  | zero => simp only [total]; grind
  | succ n ih =>
    have h1 := ih (by intro i hi; exact h i (by omega))
    have h2 := h n (by omega)
    simp only [total]; grind

/-- Any admitted residual-potential certificate proves a global rational optimum. -/
theorem certificate_sound (n m : Nat) (tail head : Nat → Nat)
    (lo hi b cost x pi : Nat → Rat)
    (ht : ∀ e, e < m → tail e < n) (hh : ∀ e, e < m → head e < n)
    (hx : Feasible n m tail head lo hi b x)
    (hs : Signs m tail head lo hi cost x pi) :
    ∀ y, Feasible n m tail head lo hi b y → value m cost x ≤ value m cost y := by
  intro y hy
  have hc := potential_cancels n m tail head x y pi ht hh
    (by intro v hv; rw [hx.2 v hv, hy.2 v hv])
  have hn := total_nonneg m
    (fun e => (cost e + pi (tail e) - pi (head e)) * (y e - x e))
    (by intro e he; exact sign_term _ _ _ _ _ (hy.1 e he) (hs e he).1 (hs e he).2)
  have hid : total m (fun e => (cost e + pi (tail e) - pi (head e)) * (y e - x e)) =
      value m cost y - value m cost x +
      total m (fun e => (pi (tail e) - pi (head e)) * (y e - x e)) := by
    unfold value
    rw [← total_sub, ← total_add]
    apply total_congr; intro e _; grind
  rw [hid, hc] at hn
  grind

/-- Changed costs need signs only at the declared set; all other costs are identical. -/
theorem delta_signs (m : Nat) (tail head : Nat → Nat)
    (lo hi oldCost newCost x pi : Nat → Rat) (changed : Nat → Prop)
    (oldSigns : Signs m tail head lo hi oldCost x pi)
    (unchanged : ∀ e, e < m → ¬ changed e → newCost e = oldCost e)
    (patched : ∀ e, e < m → changed e →
      (x e < hi e → 0 ≤ newCost e + pi (tail e) - pi (head e)) ∧
      (lo e < x e → newCost e + pi (tail e) - pi (head e) ≤ 0)) :
    Signs m tail head lo hi newCost x pi := by
  intro e he
  by_cases hc : changed e
  · exact patched e he hc
  · rw [unchanged e he hc]; exact oldSigns e he

theorem delta_optimal (n m : Nat) (tail head : Nat → Nat)
    (lo hi b oldCost newCost x pi : Nat → Rat) (changed : Nat → Prop)
    (ht : ∀ e, e < m → tail e < n) (hh : ∀ e, e < m → head e < n)
    (hx : Feasible n m tail head lo hi b x)
    (oldSigns : Signs m tail head lo hi oldCost x pi)
    (unchanged : ∀ e, e < m → ¬ changed e → newCost e = oldCost e)
    (patched : ∀ e, e < m → changed e →
      (x e < hi e → 0 ≤ newCost e + pi (tail e) - pi (head e)) ∧
      (lo e < x e → newCost e + pi (tail e) - pi (head e) ≤ 0)) :
    ∀ y, Feasible n m tail head lo hi b y → value m newCost x ≤ value m newCost y := by
  exact certificate_sound n m tail head lo hi b newCost x pi ht hh hx
    (delta_signs m tail head lo hi oldCost newCost x pi changed oldSigns unchanged patched)

theorem objective_update (m : Nat) (oldCost newCost x : Nat → Rat) :
    value m newCost x = value m oldCost x + total m (fun e => (newCost e-oldCost e)*x e) := by
  unfold value
  rw [← total_add]
  apply total_congr
  intro e _
  grind

#print axioms delta_optimal
#print axioms objective_update
#print axioms certificate_sound
#print axioms delta_signs
end Allocation
