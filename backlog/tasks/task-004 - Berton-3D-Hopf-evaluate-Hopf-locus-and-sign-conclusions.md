---
id: TASK-004
title: 'Berton 3D Hopf: evaluate Hopf locus and sign conclusions'
status: To Do
assignee: []
created_date: '2026-06-13 20:21'
updated_date: '2026-06-13 20:21'
labels:
  - analysis
  - berton
  - hopf
  - stability
dependencies:
  - TASK-001
  - TASK-002
  - TASK-003
references:
  - docs/berton_3d_hopf_briefing.md
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Use the confirmed symbolic and numerical results for the reduced Berton 3D model to state the Hopf condition in physical parameters, verify the radiative-cooling sign logic, and classify the baseline case relative to the Hopf locus.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The Hopf condition is printed in shorthand and expanded physical-parameter forms.
- [ ] #2 The script or report symbolically confirms that in the cooling regime eta_a < 1, R_r < 0 and c < 0, the k*c contribution reduces the Hopf-locus left-hand side and can make the locus reachable.
- [ ] #3 The onset-frequency positivity requirement Omega_0^2 = k*c + a > 0 is stated and translated to w_prime > -(G/r_star)*R_r = |c|.
- [ ] #4 Baseline parameters are used to report whether the system is below, at, or above the Hopf locus.
- [ ] #5 The analysis reports how lowering the updraft base/decreasing w_prime moves the system relative to instability and whether that matches Berton's 10 km to 9 km transition.
<!-- AC:END -->
