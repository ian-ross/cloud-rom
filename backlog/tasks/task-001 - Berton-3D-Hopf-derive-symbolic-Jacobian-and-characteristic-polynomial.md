---
id: TASK-001
title: 'Berton 3D Hopf: derive symbolic Jacobian and characteristic polynomial'
status: In Progress
assignee:
  - '@pi'
created_date: '2026-06-13 20:21'
updated_date: '2026-06-13 20:29'
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

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Locate the existing Berton numerical implementation and identify naming conventions for state variables, RHS helpers, and parameter constants so the symbolic script mirrors the model where practical.
2. Add a small SymPy analysis script for TASK-001 only: declare k, beta, G, r_star, w_prime, sigma_S as positive symbols and R_r, R_zeta as real symbols; define zeta, v, r, lambda, generic Functions W_a, V_f, s, and R.
3. Build the reduced RHS expressions from the equations, differentiate with respect to (zeta, v, r), and print the raw symbolic Jacobian before substitutions.
4. Substitute fixed-point identities: v_star = 0, W_a(zeta_star) = beta*r_star**2, V_f(r_star) = beta*r_star**2, s(zeta_star) - R(zeta_star, r_star) = 0, plus local derivatives W_a' = -w_prime, dV_f/dr = 2*beta*r_star, ds/dzeta = -sigma_S, dR/dr = R_r, dR/dzeta = R_zeta. Explicitly print dr_dot/dr before and after applying s - R = 0 to demonstrate the cancellation.
5. Define shorthand a = k*w_prime, b = 2*k*beta*r_star, c = (G/r_star)*R_r, and d = (G/r_star)*(sigma_S + R_zeta); construct the reference Jacobian from those shorthands only for comparison, print the derived and reference matrices, and assert simplify(derived - reference) is the zero matrix.
6. Compute the characteristic polynomial with SymPy, normalize/collect in lambda, extract a2, a1, and a0, print each coefficient in physical and shorthand forms, and assert equality against a2 = k + c, a1 = k*c + a, and a0 = a*c + b*d.
7. Compute and factor a2*a1 - a0, print the physical expression and shorthand expression, then assert it equals k*(k*c + a + c**2) - b*d.
8. Add a script entry point that prints all intermediate expressions with readable SymPy pretty-printing and fails loudly on any assertion mismatch.
9. Run the script and any targeted tests/format checks available, then mark all TASK-001 acceptance criteria complete and write a concise final summary only after verification.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
- Added scripts/berton_3d_hopf_task001_symbolic.py with SymPy derivation from the stated reduced RHS and all required intermediate pretty-prints.
- Added sympy dependency via uv add sympy.
- Added tests/test_berton_3d_hopf_task001_symbolic.py.
- Important result: deriving from v_dot = -k*(v - (W_a - V_f)), V_f = beta*r**2 gives J[1,2] = -2*k*beta*r_star, not the briefing hand-reference +2*k*beta*r_star. The script trusts the equation, asserts the equation-consistent Jacobian/coefs/RH expression, and prints the briefing discrepancies explicitly.
<!-- SECTION:NOTES:END -->
