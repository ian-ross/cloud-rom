---
id: TASK-026
title: Build full-model Python pseudo-arclength continuation core
status: In Progress
assignee:
  - '@pi'
created_date: '2026-06-17 16:39'
updated_date: '2026-06-17 16:48'
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

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect existing full-model RHS/Jacobian utilities and TASK-011/TASK-015 seed artifacts to reuse the validated physical residual, log-mass transform, and eigenvalue cross-check conventions.
2. Add an Episode 10 standalone continuation module/script implementing scaled coordinates x = [(z-z_ref)/z_scale, (u-u_ref)/u_scale, (w-w_ref)/w_scale, log(m/kg)-log_m_ref] plus inverse transforms, row-scaled full 4D residuals, finite-difference Jacobians, tangent estimation, and Newton pseudo-arclength correction.
3. Persist transparent diagnostics for each prediction/correction attempt: residual norms, arclength/control step sizes, tangent vectors, Jacobian singular values/condition estimates, iteration histories, accept/reject status, and failure reasons.
4. Add a reproducible notebook or notebook-generation script for TASK-026 that loads the TASK-011/TASK-012 equilibrium seed, checks residual/eigenvalues in physical and scaled/log-mass coordinates, runs at least one local pseudo-arclength tangent/corrector step, and writes curated CSV/JSON outputs under episodes/10-full-model-python-continuation/outputs/task026/.
5. Add repository tests covering residual scaling behavior, coordinate round-trips including log-mass inverse transforms, seed residual/eigenvalue output availability, and at least one local tangent/corrector diagnostic step.
6. Run the targeted Episode 10 tests and relevant existing Berton/full-model tests; then update implementation notes, acceptance criteria, final summary, and task status via backlog CLI.
<!-- SECTION:PLAN:END -->
