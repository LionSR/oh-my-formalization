/-
Copyright (c) 2026 The MyProject contributors. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: A. Author
-/
import Mathlib.Analysis.SpecialFunctions.Pow.Real

/-!
# A first result

The starter theorem: the square of a real number is nonnegative. Replace it
with your first real result; the blueprint's Chapter 1 cites it, so keep the
`\lean{}` tag there in sync when you rename it.
-/

/-- The square of a real number is nonnegative. -/
theorem MyProject.sq_nonneg (x : ℝ) : 0 ≤ x ^ 2 := by positivity
