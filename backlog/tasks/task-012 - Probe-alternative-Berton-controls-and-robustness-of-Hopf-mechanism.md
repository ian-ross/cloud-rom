---
id: TASK-012
title: Probe alternative Berton controls and robustness of Hopf mechanism
status: To Do
assignee: []
created_date: '2026-06-14 12:39'
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
