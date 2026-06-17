---
id: TASK-026
title: Build full-model Python pseudo-arclength continuation core
status: Done
assignee:
  - '@pi'
created_date: '2026-06-17 16:39'
updated_date: '2026-06-17 16:53'
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
- [x] #1 Continuation core follows equilibria of the full 4D Berton residual in scaled variables including altitude, horizontal velocity, vertical velocity, and log-mass coordinate
- [x] #2 Predictor/corrector iterations save residual norms, step sizes, tangent estimates, Jacobian condition diagnostics, and convergence/failure reasons
- [x] #3 Notebook or script reproduces a seed residual/eigenvalue cross-check against the TASK-011/TASK-012 equilibrium
- [x] #4 Tests or validation checks cover residual scaling, coordinate inverse transforms, and at least one local tangent/corrector step
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

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
- Implemented episodes/10-full-model-python-continuation/scripts/berton_full_task026_continuation.py with scaled z/u/w/log-mass coordinates, W_a0 control scaling, row-scaled full transformed RHS residuals, finite-difference branch Jacobian, SVD tangent extraction, and Newton pseudo-arclength correction.
- Generated curated TASK-026 outputs under episodes/10-full-model-python-continuation/outputs/task026/: seed/corrected residual table, eigenvalue table, corrector iteration diagnostics, tangent estimates, and JSON condition/step summary.
- Added docs/task026_python_continuation_core.md plus README pointers documenting coordinates, reproducibility command, diagnostics, and residual risks.
- Added tests/test_episode10_task026_python_continuation.py covering residual scaling, coordinate round-trips, local tangent/corrector convergence, and curated diagnostic outputs.
- Validation: uv run python episodes/10-full-model-python-continuation/scripts/berton_full_task026_continuation.py; uv run pytest tests/test_episode05_full_oscillatory_orbit.py tests/test_episode06_full_seed_continuation.py tests/test_episode06_full_logm_reformulation.py tests/test_episode10_task026_python_continuation.py; uv run pytest.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented the Episode 10 full-model Python pseudo-arclength continuation core.

Changes:
- Added a standalone TASK-026 continuation script using scaled altitude, horizontal velocity, vertical velocity, log-mass state, and scaled W_a0 control.
- Implemented full transformed Berton residual evaluation, row residual scaling, finite-difference branch Jacobians, SVD tangent estimates, predictor steps, and Newton pseudo-arclength correction with convergence/failure diagnostics.
- Generated curated outputs for the TASK-011/TASK-012 seed cross-check, one accepted local corrected point, physical eigenvalues, tangent estimates, corrector iterations, Jacobian singular values/condition diagnostics, residual norms, and step sizes.
- Documented reproducibility and residual risks in docs/task026_python_continuation_core.md and linked the artifacts from the Episode 10 README.
- Added regression tests for scaling, inverse coordinate transforms, seed residual/eigenvalue outputs, and a local tangent/corrector step.

Validation:
- uv run python episodes/10-full-model-python-continuation/scripts/berton_full_task026_continuation.py
- uv run pytest tests/test_episode05_full_oscillatory_orbit.py tests/test_episode06_full_seed_continuation.py tests/test_episode06_full_logm_reformulation.py tests/test_episode10_task026_python_continuation.py
- uv run pytest
<!-- SECTION:FINAL_SUMMARY:END -->
