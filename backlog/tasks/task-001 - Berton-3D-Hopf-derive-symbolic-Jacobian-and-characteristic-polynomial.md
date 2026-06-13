---
id: TASK-001
title: 'Berton 3D Hopf: derive symbolic Jacobian and characteristic polynomial'
status: To Do
assignee:
  - 'null'
created_date: '2026-06-13 20:21'
updated_date: '2026-06-13 21:14'
labels:
  - analysis
  - sympy
  - berton
  - hopf
dependencies: []
references:
  - docs/berton_3d_hopf_briefing.md
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement the symbolic foundation for the reduced 3D Berton Hopf analysis. Build the RHS with SymPy Functions, differentiate from the equations, apply fixed-point conditions including s - R = 0, and verify the Jacobian, characteristic coefficients, and Routh-Hurwitz expression against the briefing reference without hard-coding results.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Symbols are declared with the briefing's assumptions for k, beta, G, r_star, w_prime, sigma_S, R_r, and R_zeta.
- [ ] #2 The Jacobian is derived by differentiating the symbolic reduced RHS and substituting fixed-point conditions, including an explicit demonstration that the dr_dot/dr cancellation from s - R = 0 occurs.
- [ ] #3 The derived Jacobian is printed and compared with the reference matrix using SymPy simplification/assertions.
- [ ] #4 The characteristic polynomial coefficients a2, a1, and a0 are extracted with SymPy, printed, and asserted equal to the reference coefficients after shorthand substitution.
- [ ] #5 The Routh-Hurwitz expression a2*a1 - a0 is simplified/factored, printed in physical and shorthand forms, and asserted against the reference Hopf expression.
<!-- AC:END -->
