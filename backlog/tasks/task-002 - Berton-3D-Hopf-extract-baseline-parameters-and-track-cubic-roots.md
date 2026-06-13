---
id: TASK-002
title: 'Berton 3D Hopf: extract baseline parameters and track cubic roots'
status: To Do
assignee: []
created_date: '2026-06-13 20:21'
updated_date: '2026-06-13 20:21'
labels:
  - analysis
  - numpy
  - berton
  - hopf
dependencies:
  - TASK-001
references:
  - docs/berton_3d_hopf_briefing.md
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add the numerical cross-check for the reduced 3D Hopf analysis. Use the existing Berton numerical implementation only as the provenance for baseline coefficients and fixed-point/local-gradient values, then track the cubic roots over k to test whether a clean slow complex pair exists.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Representative values for k, beta, G, r_star, w_prime, sigma_S, R_r, and R_zeta are obtained from or justified against the existing numerical model and documented with provenance comments.
- [ ] #2 Numerical cubic coefficients are produced by substituting the baseline values into the symbolic a2, a1, and a0 expressions.
- [ ] #3 Roots are computed with numpy.roots for k = 1, 10, 100, 1000, and 1e4 s^-1 while holding slow physical parameters fixed.
- [ ] #4 The output prints the three roots at each k and tabulates the slow pair real and imaginary parts versus k.
- [ ] #5 The analysis explicitly reports whether one fast root tends to -k and whether the slow pair converges; if it does not converge, the script stops or flags the central reduction assumption as failed.
- [ ] #6 The limiting slow-pair frequency is converted to period and the real part is converted to a damping-rate/damping-ratio comparison against Berton's 7-10 hr period and zeta approximately 0.01-0.02.
<!-- AC:END -->
