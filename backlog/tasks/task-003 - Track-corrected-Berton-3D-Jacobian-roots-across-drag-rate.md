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
