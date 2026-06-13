---
id: TASK-005
title: 'Berton 3D Hopf: connect symbolic Jacobian to numerical RHS'
status: To Do
assignee: []
created_date: '2026-06-13 20:21'
updated_date: '2026-06-13 20:21'
labels:
  - analysis
  - validation
  - berton
  - hopf
dependencies:
  - TASK-001
  - TASK-002
references:
  - docs/berton_3d_hopf_briefing.md
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add the independent validation bridge between the symbolic reduced analysis and the existing Berton numerical implementation by comparing the symbolic Jacobian evaluated at the baseline fixed point with a finite-difference Jacobian from the numerical RHS.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A reduced numerical RHS is identified or implemented using the same naming and state order (zeta, v, r) as the symbolic analysis and existing Berton code.
- [ ] #2 The symbolic Jacobian is evaluated numerically at the selected fixed point using the same parameter values used for root tracking.
- [ ] #3 A finite-difference Jacobian is computed from the numerical RHS at the same state and parameter values with documented step-size choices.
- [ ] #4 The symbolic and finite-difference Jacobians are printed side by side and compared with tolerances appropriate for finite differences.
- [ ] #5 Any mismatch beyond tolerance is surfaced as a transcription or reduction error instead of being silently ignored.
<!-- AC:END -->
