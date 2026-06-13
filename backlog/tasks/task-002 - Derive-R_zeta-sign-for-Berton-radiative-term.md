---
id: TASK-002
title: Derive R_zeta sign for Berton radiative term
status: To Do
assignee: []
created_date: '2026-06-13 21:17'
labels: []
dependencies: []
references:
  - docs/berton_3d_hopf_briefing.md
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Derive the altitude derivative of the closed-form radiative term R(zeta, r) = Phi(T(zeta)) * (eta_a(zeta) - 1) * r using Berton profile definitions, and determine the sign of R_zeta and sigma_S + R_zeta at the baseline operating point.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Closed-form R(zeta, r) is represented symbolically with Phi(T(zeta)), eta_a(zeta), and r.
- [ ] #2 Berton eta_a(z) and T(z) profiles from the briefing/paper equations are encoded for the relevant altitude layer.
- [ ] #3 R_zeta = dR/dzeta is derived symbolically and all non-trivial intermediate expressions are printed.
- [ ] #4 Baseline numerical values for R_zeta and sigma_S + R_zeta are computed with documented provenance for every parameter.
- [ ] #5 The signs of R_zeta and sigma_S + R_zeta are reported prominently without presupposing Hopf or saddle.
- [ ] #6 Any piecewise-profile branch assumptions for the baseline altitude are made explicit and validated.
<!-- AC:END -->
