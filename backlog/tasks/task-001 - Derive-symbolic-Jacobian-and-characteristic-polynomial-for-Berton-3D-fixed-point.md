---
id: TASK-001
title: >-
  Derive symbolic Jacobian and characteristic polynomial for Berton 3D fixed
  point
status: Done
assignee:
  - '@agent'
created_date: '2026-06-13 21:17'
updated_date: '2026-06-15 12:12'
labels: []
dependencies: []
references:
  - docs/berton_3d_hopf_briefing.md
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement the symbolic SymPy linearization for the reduced 3D Berton fixed point using state order (zeta, v, r). Build the Jacobian from the reduced RHS with symbolic functions, substitute fixed-point conditions, and verify the corrected reference algebra without hard-coding the final matrix.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Symbols are declared with known assumptions and R_r/R_zeta signs left free.
- [x] #2 Jacobian is derived from symbolic RHS functions and fixed-point substitutions, including symbolic demonstration that the (s - R) term cancels in dr_dot/dr.
- [x] #3 Derived Jacobian is printed and asserted equal to the corrected reference matrix with the [v_dot, r] entry equal to -b.
- [x] #4 Characteristic polynomial coefficients a2, a1, a0 are printed, extracted, and asserted equal to corrected reference expressions.
- [x] #5 a0 is factored and asserted equal to k times the corresponding 2D determinant.
- [x] #6 a2*a1 - a0 is simplified/factored, printed in both symbolic forms, and asserted equal to the corrected Routh-Hurwitz expression.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect the existing repository layout to identify where Berton analysis scripts live and choose an appropriate location/name for the symbolic analysis script without modifying unrelated code.
2. Create or update a focused Python script for TASK-001 that imports SymPy and defines the reduced RHS symbolically with state order (zeta, v, r), using W_a(zeta), V_f(r), s(zeta), and R(zeta, r) as SymPy expressions/functions.
3. Declare all scalar symbols with assumptions from the briefing: k, beta, G, r_star, w_prime positive; sigma_S positive; R_r and R_zeta real/free sign; define shorthand a, b, c, d only after deriving the raw Jacobian.
4. Differentiate the RHS with respect to (zeta, v, r) to form the raw Jacobian, then substitute fixed-point conditions v*=0, W_a(zeta*)=beta*r_star**2, s(zeta*)=R(zeta*, r_star), and derivative substitutions for W_a, V_f, s, and R.
5. Explicitly demonstrate the dr_dot/dr cancellation from the fixed-point condition s - R = 0 by printing the pre- and post-substitution expression, rather than assuming the simplified form.
6. Build the corrected reference Jacobian using a = k*w_prime, b = 2*k*beta*r_star, c = (G/r_star)*R_r, and d = (G/r_star)*(sigma_S + R_zeta); print both matrices and assert symbolic equality, with special emphasis that the [v_dot, r] entry is -b.
7. Compute the characteristic polynomial det(lambda*I - J), collect it as lambda**3 + a2*lambda**2 + a1*lambda + a0, print the coefficients, and assert equality to the corrected reference coefficients a2=k+c, a1=k*c+a, a0=a*c-b*d.
8. Factor a0 into dimensional primitives and assert it equals k*(G/r_star)*(w_prime*R_r - 2*beta*r_star**2*(sigma_S + R_zeta)), documenting this as k times the 2D determinant.
9. Compute, simplify, factor, and print a2*a1 - a0; assert it equals k*(k*c + a + c**2) + b*d and print the equivalent Hopf-locus rearrangement for later tasks.
10. Add loud assertion failures and readable SymPy pretty-print output for every non-trivial symbolic step so later tasks can trust the script as an auditable artifact.
11. Run the TASK-001 script locally, fix any algebra/extraction issues, and record the command/output summary in Implementation Notes once approved.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented TASK-001 symbolic audit script at scripts/berton_3d_hopf_task001_symbolic.py.
- Builds RHS from SymPy Functions and differentiates the Jacobian rather than typing it in.
- Demonstrates dr_dot/dr cancellation after applying s(zeta*) = R(zeta*, r*).
- Asserts the corrected Jacobian, including [v_dot, r] = -2*k*beta*r_star = -b.
- Extracts and asserts a2, a1, a0 and the corrected Routh-Hurwitz expression.
- Added regression coverage in tests/test_berton_3d_hopf_task001_symbolic.py.
- Surfaced a discrepancy: a0/k derived from a*c-b*d gives a determinant term -2*beta*r_star*(sigma_S + R_zeta) inside the G/r_star factor, whereas the briefing text also contains an expanded -2*beta*r_star**2 form. The script warns instead of hiding this mismatch.

Validation run:
- uv run python scripts/berton_3d_hopf_task001_symbolic.py
- uv run pytest tests/test_berton_3d_hopf_task001_symbolic.py tests/test_berton2023.py  # 12 passed

Repository reorganization note: TASK-001 artifacts moved to episodes/02-reduced-model-cas/ (script: scripts/berton_3d_hopf_task001_symbolic.py within that episode).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented the TASK-001 symbolic linear-stability audit for the reduced Berton 3D fixed point.

Changes:
- Added scripts/berton_3d_hopf_task001_symbolic.py to derive the Jacobian directly from the reduced RHS with SymPy Functions, apply fixed-point and derivative substitutions, and print each intermediate algebraic step.
- Verified the corrected Jacobian, including the negative [v_dot, r] entry (-b), extracted the cubic coefficients, asserted a0 = a*c - b*d, and asserted the corrected Routh-Hurwitz expression.
- Explicitly demonstrates the dr_dot/dr cancellation from s(zeta*) = R(zeta*, r*).
- Added a regression test that imports and runs the derivation.
- Added SymPy as a project dependency.

Important finding:
- The script surfaces a mismatch in the briefing text: deriving a0/k from a*c-b*d gives the 2D determinant term with -2*beta*r_star*(sigma_S + R_zeta) inside the G/r_star factor, not the expanded -2*beta*r_star**2 form also stated in the briefing. The implemented assertions trust the internally consistent SymPy derivation and corrected a*c-b*d coefficients, and print the residual as a warning for follow-up.

Tests:
- uv run python scripts/berton_3d_hopf_task001_symbolic.py
- uv run pytest tests/test_berton_3d_hopf_task001_symbolic.py tests/test_berton2023.py (12 passed)
<!-- SECTION:FINAL_SUMMARY:END -->
