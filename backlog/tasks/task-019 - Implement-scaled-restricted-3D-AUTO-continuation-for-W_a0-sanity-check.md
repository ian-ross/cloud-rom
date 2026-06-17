---
id: TASK-019
title: Implement scaled restricted 3D AUTO continuation for W_a0 sanity check
status: In Progress
assignee:
  - '@pi'
created_date: '2026-06-15 20:17'
updated_date: '2026-06-17 07:42'
labels:
  - berton
  - auto
  - continuation
  - scaling
dependencies:
  - TASK-018
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
In the new episode episodes/07-restricted-equilibrium-auto/, use the TASK-018 scaling diagnosis to build a restricted 3D AUTO equilibrium problem for local Berton balances, with w fixed to zero and unknowns such as scaled altitude, scaled horizontal velocity, and scaled log-mass or radius. First validate the formulation on W_a0 before attempting Hopf-focused H_a3 continuation.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A new episode AUTO variant is added for the restricted 3D equilibrium system without overwriting TASK-012 or TASK-015 artifacts.
- [ ] #2 State, residual, and parameter scalings follow TASK-018 recommendations and are documented with physical inverse conversions.
- [ ] #3 The TASK-011 seed is translated into restricted 3D AUTO coordinates and residuals/eigenvalues or equivalent stability diagnostics are cross-checked in Python.
- [ ] #4 W_a0 continuation is run at least in the easier sanity-check direction and compared against TASK-012/TASK-015 first-step failures.
- [ ] #5 Accepted points or failure diagnostics, AUTO commands/constants, and residual numerical risks are recorded in notebook/script/docs outputs.
- [ ] #6 The restricted W_a0 gate applies the TASK-022 arclength fix by continuing in P=M/10, where M=log(m/m_seed), and reports physical M and m via the inverse conversion.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Use the TASK-022 arclength-scaling finding as the primary implementation fix: replace AUTO state `U(3)=M=log(m/m_seed)` with `U(3)=P=M/10`, and map back with `log(m)=log(m_seed)+10*P`.
2. Start from the restricted/scaled TASK-017/TASK-021 residual, not the failed full-4D TASK-015 variant; keep `Z=(z-z_seed)/100 m`, `U=(u-u_seed)/(1 m/s)`, and the TASK-018 row-scaled residuals.
3. Update Fortran comments, `unames`, PVLS/physical-output conversion, parser logic, and tests so branch outputs report both the AUTO coordinate `P_log_ratio_over_10` and physical `M=10P`/`m=m_seed*exp(10P)`.
4. Adjust any supplied DFDU finite-difference step or analytic derivative for the `P` coordinate by the chain-rule factor of 10; if using AUTO finite differences first, document that `P` is the arclength-scaled mass coordinate.
5. Configure `W_a0` continuation from the TASK-011/TASK-012 seed with conservative initial steps; the scratch TASK-022 follow-up showed the `P=M/10` variant reaches `W_a0=1.2`, so use that as the expected gate target.
6. Run at least the upward W_a0 sanity direction and preserve raw AUTO `b/s/d` outputs under a distinct TASK-019 name without overwriting TASK-017/TASK-021 artifacts.
7. Parse branch files into `outputs/task019/`, including accepted W_a0 range, physical altitude/u/m movement, `P` and reconstructed `M`, stability/eigenvalue diagnostics where available, and convergence notes.
8. Compare explicitly against TASK-017/TASK-021 seed-only failures and the TASK-012 Python W_a0 probe expectation of smooth stable movement.
9. Write a notebook/script/doc record of commands, constants, the `P=M/10` arclength fix, accepted points, residual risks, and whether this clears the W_a0 gate for TASK-020.
10. Add tests for output artifacts, seed translation/cross-checks, `P<->M` conversion, W_a0 range coverage, and conservative gate conclusion for TASK-020.
<!-- SECTION:PLAN:END -->
