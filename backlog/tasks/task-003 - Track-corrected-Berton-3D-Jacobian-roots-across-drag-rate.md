---
id: TASK-003
title: Track corrected Berton 3D Jacobian roots across drag rate
status: In Progress
assignee:
  - '@agent'
created_date: '2026-06-13 21:18'
updated_date: '2026-06-14 11:07'
labels: []
dependencies:
  - TASK-001
  - TASK-002
references:
  - docs/berton_3d_hopf_briefing.md
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement the numerical root-tracking cross-check for the corrected 3D characteristic polynomial across representative drag rates, using parameters and fixed-point derivatives from the existing numerical Berton model where possible.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 k, beta, G, r_star, w_prime, sigma_S, R_r, and R_zeta are obtained from the existing model or derived fixed point with provenance documented.
- [ ] #2 Corrected a2, a1, and a0 coefficients are evaluated numerically for each selected drag rate.
- [ ] #3 numpy.roots is run for k in [1, 10, 100, 1000, 1e4] s^-1 while holding slow physical parameters fixed.
- [ ] #4 Roots are printed in a readable table for every k value.
- [ ] #5 The output diagnoses saddle versus Hopf-capable behavior based on root real parts and consistency with the sign of a0.
- [ ] #6 The symbolic Jacobian evaluated at the fixed point is compared against a finite-difference Jacobian from the existing reduced RHS to finite-difference accuracy.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Re-read TASK-001/TASK-002 scripts and the briefing to pin down corrected coefficient formulas and reusable derivative values.
2. Inspect existing Berton model APIs for local diagnostics, fixed-point state construction, drag-rate inputs, and reduced RHS components.
3. Implement an auditable root-tracking script that holds slow physical parameters fixed at the TASK-002 baseline while sweeping k = [1, 10, 100, 1000, 1e4] s^-1.
4. Compute corrected a2/a1/a0 coefficients, run numpy.roots, and print a readable table with saddle/Hopf-capable diagnostics and a0 sign consistency.
5. Add a reduced-RHS finite-difference Jacobian check against the symbolic Jacobian at the baseline fixed point.
6. Add tests covering coefficient construction, root table sign behavior, and symbolic-vs-finite-difference Jacobian agreement.
7. Run the new script and targeted pytest suite, then update TASK-003 acceptance criteria, notes, final summary, and status.
<!-- SECTION:PLAN:END -->
