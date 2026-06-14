---
id: TASK-006
title: Write Berton 3D Hopf-or-saddle analysis summary
status: In Progress
assignee:
  - '@agent'
created_date: '2026-06-13 21:18'
updated_date: '2026-06-14 12:12'
labels: []
dependencies:
  - TASK-001
  - TASK-002
  - TASK-003
  - TASK-004
  - TASK-005
references:
  - docs/berton_3d_hopf_briefing.md
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Produce the concise Markdown report for the reduced 3D Berton fixed-point analysis, summarizing the symbolic derivation, radiative-gradient sign result, root tracking, slow reductions, and final Hopf-versus-saddle verdict.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Report includes the symbolic Jacobian with corrected -b entry, characteristic polynomial, and a0 = k times 2D determinant factorisation.
- [ ] #2 Report highlights the derived signs of R_zeta and sigma_S + R_zeta.
- [ ] #3 Report includes the root-tracking table and its Hopf-versus-saddle diagnosis.
- [ ] #4 Report includes reduced slow-pair eigenvalues from Routes A and B and states whether they agree.
- [ ] #5 If oscillatory, report compares the slow-pair frequency to Berton Eq. (119).
- [ ] #6 Report ends with a clear go/no-go verdict on whether the baseline fixed point is Hopf-capable stable spiral or saddle, and states the sign dependency that controls the answer.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Review outputs/scripts from TASK-001 through TASK-005 and the existing briefing/review docs to identify the best location/name for the final concise Markdown report.
2. Draft a standalone Markdown summary with sections for corrected symbolic Jacobian/cubic, radiative-gradient signs, root-tracking evidence, singular-reduction agreement, Eq. (119) frequency comparison, and final verdict.
3. Include auditable numeric values from the validated scripts, including the root table and the determinant/r_star discrepancy.
4. Add lightweight tests/checks that the report contains the required formulas, signs, root-tracking rows, Route A/B agreement statement, Eq. (119)-style product, and final verdict.
5. Run the report checks and targeted pytest suite.
6. Update TASK-006 notes/ACs/final summary/status.
<!-- SECTION:PLAN:END -->
