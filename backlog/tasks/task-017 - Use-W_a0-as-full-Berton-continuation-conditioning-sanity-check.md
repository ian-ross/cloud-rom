---
id: TASK-017
title: Use W_a0 as full Berton continuation conditioning sanity check
status: To Do
assignee: []
created_date: '2026-06-15 19:47'
updated_date: '2026-06-15 19:47'
labels:
  - berton
  - auto
  - continuation
  - W_a0
dependencies:
  - TASK-013
  - TASK-015
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Use W_a0 continuation in the improved full Berton AUTO formulation as a sanity check for branch conditioning and local-equilibrium movement. This task is not primarily Hopf-seeking; it verifies that the reformulated problem can continue a branch for a control known from the Python probe to move the equilibrium smoothly while remaining stable.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Continuation starts from the TASK-011/TASK-012 equilibrium seed in the reformulated AUTO variables.
- [ ] #2 W_a0 continuation covers a documented range comparable to the TASK-012 Python probe where feasible, or explains any reduced range.
- [ ] #3 AUTO outputs show whether the branch moves the equilibrium altitude smoothly beyond the seed and no longer immediately fails at the first step.
- [ ] #4 Stability/eigenvalue diagnostics are reported and compared with the TASK-012 Python W_a0 probe expectation of stable equilibria.
- [ ] #5 The result is used to assess whether remaining H_a3 failures are control-specific or indicate broader formulation/conditioning problems.
<!-- AC:END -->
