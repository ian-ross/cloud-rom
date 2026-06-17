---
id: TASK-026
title: Build full-model Python pseudo-arclength continuation core
status: To Do
assignee: []
created_date: '2026-06-17 16:39'
updated_date: '2026-06-17 16:39'
labels:
  - berton
  - continuation
  - python
  - episode-10
dependencies:
  - TASK-025
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement a reproducible Python pseudo-arclength continuation core for full Berton equilibria in episode 10, using scaled full-system variables and transparent predictor/corrector diagnostics so branch-following can be debugged outside AUTO.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Continuation core follows equilibria of the full 4D Berton residual in scaled variables including altitude, horizontal velocity, vertical velocity, and log-mass coordinate
- [ ] #2 Predictor/corrector iterations save residual norms, step sizes, tangent estimates, Jacobian condition diagnostics, and convergence/failure reasons
- [ ] #3 Notebook or script reproduces a seed residual/eigenvalue cross-check against the TASK-011/TASK-012 equilibrium
- [ ] #4 Tests or validation checks cover residual scaling, coordinate inverse transforms, and at least one local tangent/corrector step
<!-- AC:END -->
