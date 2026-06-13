---
id: TASK-005
title: Classify Berton baseline fixed point as Hopf-capable or saddle
status: To Do
assignee: []
created_date: '2026-06-13 21:18'
labels: []
dependencies:
  - TASK-002
  - TASK-003
  - TASK-004
references:
  - docs/berton_3d_hopf_briefing.md
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Use the corrected symbolic algebra, derived radiative-gradient signs, and numerical root-tracking evidence to classify the baseline reduced 3D Berton fixed point and state the stability mechanism plainly.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The corrected Hopf locus k*(k*c + a + c^2) = -b*d is stated and tied to the corrected characteristic polynomial.
- [ ] #2 The determinant relation a0 = k times the 2D determinant is stated and interpreted.
- [ ] #3 The baseline fixed point is classified as Hopf-capable when a0 > 0 or saddle when a0 < 0, using the derived sign of sigma_S + R_zeta.
- [ ] #4 If saddle, the report states what sign change or omitted feedback would be required to allow an oscillatory instability.
- [ ] #5 If Hopf-capable, the report gives onset frequency, destabilising direction, and qualitative movement relative to the locus for the 10 km to 9 km transition.
- [ ] #6 Any discrepancy between SymPy, root tracking, and the corrected hand derivation is surfaced explicitly.
<!-- AC:END -->
