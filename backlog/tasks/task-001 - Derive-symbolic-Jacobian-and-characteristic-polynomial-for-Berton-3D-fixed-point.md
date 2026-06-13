---
id: TASK-001
title: >-
  Derive symbolic Jacobian and characteristic polynomial for Berton 3D fixed
  point
status: In Progress
assignee:
  - '@agent'
created_date: '2026-06-13 21:17'
updated_date: '2026-06-13 21:19'
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
- [ ] #1 Symbols are declared with known assumptions and R_r/R_zeta signs left free.
- [ ] #2 Jacobian is derived from symbolic RHS functions and fixed-point substitutions, including symbolic demonstration that the (s - R) term cancels in dr_dot/dr.
- [ ] #3 Derived Jacobian is printed and asserted equal to the corrected reference matrix with the [v_dot, r] entry equal to -b.
- [ ] #4 Characteristic polynomial coefficients a2, a1, a0 are printed, extracted, and asserted equal to corrected reference expressions.
- [ ] #5 a0 is factored and asserted equal to k times the corresponding 2D determinant.
- [ ] #6 a2*a1 - a0 is simplified/factored, printed in both symbolic forms, and asserted equal to the corrected Routh-Hurwitz expression.
<!-- AC:END -->
