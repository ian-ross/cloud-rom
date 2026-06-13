---
id: TASK-006
title: Write Berton 3D Hopf-or-saddle analysis summary
status: To Do
assignee: []
created_date: '2026-06-13 21:18'
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
