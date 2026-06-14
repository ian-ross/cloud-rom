---
id: TASK-005
title: Classify Berton baseline fixed point as Hopf-capable or saddle
status: In Progress
assignee:
  - '@agent'
created_date: '2026-06-13 21:18'
updated_date: '2026-06-14 12:03'
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

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Review TASK-001 through TASK-004 outputs/scripts for the final corrected polynomial, signs, root-tracking result, and singular-limit frequency expression.
2. Implement a concise classification script/report generator that imports the audited task helpers where useful, computes the baseline quantities, and prints the corrected Hopf locus, determinant relation, sign chain, root evidence, and singular-limit interpretation.
3. Classify the baseline as Hopf-capable or saddle strictly from derived sigma_S + R_zeta, a0, and root-tracking evidence; surface the known briefing r_star-power discrepancy explicitly.
4. Include the branch-specific discussion required by the ACs: for the actual Hopf-capable result, give onset-frequency structure, destabilising direction, and qualitative movement relative to the Hopf locus; also state what sign change would have produced a saddle / what omitted feedbacks could change the verdict.
5. Add tests asserting the classification, sign chain, Hopf-locus residual expression, determinant relation, and discrepancy reporting.
6. Run the classification script and targeted pytest suite, then update TASK-005 notes/ACs/final summary/status.
<!-- SECTION:PLAN:END -->
