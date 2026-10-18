import Flow
-- Deliberate false claims; the reproduction harness requires compilation failure.
theorem missing_reverse_is_safe : (0 : Rat) ≤ 1*(0-1) := by decide
theorem independent_intervals_compose : (2 : Rat) ≤ 0 := by decide
