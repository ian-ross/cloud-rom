---
id: TASK-012
title: Probe alternative Berton controls and robustness of Hopf mechanism
status: To Do
assignee: []
created_date: '2026-06-14 12:39'
updated_date: '2026-06-14 13:00'
labels:
  - berton
  - auto
  - robustness
dependencies:
  - TASK-010
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
After a baseline continuation exists, test whether the Hopf/saddle verdict is robust to alternative controls and uncertain feedbacks suggested by the reduced analysis.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 At least two secondary continuation controls are tested, selected from radiation-strength multiplier, humidity-gradient/profile parameters, updraft amplitude, drag/fall-speed multiplier, or crystal-geometry/habit proxy.
- [ ] #2 For each control, the continuation records whether Hopf points, folds, or other stability changes appear.
- [ ] #3 Mechanism diagnostics track how sigma_S + R_zeta and related determinant proxies move relative to the reduced-model Hopf-capable/saddle sign boundary.
- [ ] #4 The report identifies which controls most efficiently move the system toward or away from the Hopf locus.
- [ ] #5 Any evidence for nonsmooth or global mechanisms rather than local Hopf is stated explicitly.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Use the baseline full-model continuation setup from TASK-010 as the reference case.
2. Select at least two secondary controls motivated by the reduced analysis, such as radiation-strength multiplier, humidity-gradient/profile parameter, updraft amplitude, drag/fall-speed multiplier, or habit/geometry proxy.
3. For each selected control, define parameter ranges, starting equilibria, and AUTO continuation settings.
4. Run continuation and catalog HB, LP, BP, stability changes, and failed/ambiguous detections.
5. Extract mechanism diagnostics along each branch, especially sigma_S+R_zeta and reduced determinant/Hopf-residual proxies.
6. Compare controls by how efficiently they move the system toward/away from the Hopf locus or saddle boundary.
7. Write a robustness note identifying robust conclusions, parameter-sensitive conclusions, and any evidence for nonsmooth/global rather than local Hopf behavior.
<!-- SECTION:PLAN:END -->
