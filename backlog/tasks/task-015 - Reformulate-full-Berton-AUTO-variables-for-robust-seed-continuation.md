---
id: TASK-015
title: Reformulate full Berton AUTO variables for robust seed continuation
status: Done
assignee:
  - '@pi'
created_date: '2026-06-15 19:47'
updated_date: '2026-06-15 20:01'
labels:
  - berton
  - auto
  - continuation
  - scaling
dependencies:
  - TASK-013
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Rework the full Berton AUTO continuation formulation to improve first-step convergence from the TASK-011/TASK-012 equilibrium seed. Replace raw/scaled mass with a better-conditioned variable such as log-mass or radius, and add analytic DFDU/DFDP derivatives where practical so alternate-control continuation can proceed beyond the seed.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 AUTO formulation uses a better-conditioned cloud-size variable, e.g. log-mass or radius, with documented physical-state conversions.
- [x] #2 Analytic DFDU and/or DFDP derivatives are implemented where practical, or remaining finite-difference pieces are explicitly justified.
- [x] #3 The TASK-011 equilibrium seed is translated into the reformulated AUTO coordinates and its RHS residual/eigenvalues are cross-checked against Python diagnostics.
- [x] #4 First-step convergence is retried for at least one non-z_W0 control and compared against the TASK-012 minimum-step failures.
- [x] #5 Notebook/script documentation records commands, constants, scaling choices, accepted points or failure diagnostics, and residual numerical risks.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Review TASK-012 AUTO files, failure diagnostics, and the TASK-013 report to identify the scaling/conditioning bottlenecks around the late-time equilibrium seed.
2. Choose the reformulated cloud-size coordinate, preferring radius or log-mass based on algebraic simplicity, physical positivity, and AUTO conditioning; document the forward/inverse transforms and units.
3. Create a new episode-06 AUTO variant rather than overwriting TASK-012 outputs, with updated Fortran state definitions, constants, STPNT seed translation, and output naming.
4. Implement analytic DFDU/DFDP entries where tractable for the transformed RHS; explicitly document any derivatives left to AUTO finite differences.
5. Add a Python-side seed translation/cross-check script that evaluates the reformulated RHS, maps eigenvalues back to the physical-state interpretation, and compares against TASK-011/TASK-012 diagnostics.
6. Retry first-step continuation for at least one non-z_W0 control, ideally W_a0 first as a conditioning sanity check and optionally H_a3 if W_a0 succeeds.
7. Generate branch/convergence tables and a companion note summarizing scaling choices, commands, accepted points or failures, and residual risks.
8. Add lightweight tests that verify seed translation, output artifacts, and that the new result is compared explicitly against TASK-012 minimum-step failures.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
- Created TASK-015 log-mass AUTO variant under episodes/06-full-model-auto-seed-continuation/auto/berton_full_task015 with U(4)=log(m/kg), transformed m_dot/m RHS, analytic kinematic DFDU row, and explicit finite-difference policy for remaining DFDU/DFDP pieces.
- Ran AUTO W_a0 plus/minus retries and parsed outputs; log-mass cross-check residual/eigenvalue diagnostics pass, but nontrivial first-step continuation still fails with NaN/DGEBAL divergence.
- Added script/notebook/doc/output artifacts and repository tests; full pytest passes.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented the TASK-015 log-mass reformulation and documented the resulting AUTO retry evidence.

Changes:
- Added a new TASK-015 AUTO variant using `U(4)=log(m/kg)` with physical-state conversion comments, transformed `dlog(m)/dt=m_dot/m`, an analytic kinematic Jacobian row, and explicit centered finite-difference handling for the remaining coupled derivatives/active parameters.
- Added a reproducible Python diagnostic script, notebook, curated outputs, and documentation for seed translation, RHS/eigenvalue cross-checks, W_a0 retry diagnostics, and comparison against TASK-012 minimum-step failures.
- Updated episode indexes/README entries and added tests for the new artifacts.

Result:
- The TASK-011 seed translates cleanly (`log(m/kg)=-20.6460924183`), with transformed residual ~2.0e-13 and Fortran/Python RHS agreement ~2.5e-16; eigenvalues match the physical-coordinate diagnostics.
- W_a0 plus/minus AUTO retries still accept only the seed; the failure mode now surfaces Newton/NaN/DGEBAL divergence rather than robust nontrivial continuation, so the remaining risk is documented explicitly.

Tests:
- `uv run pytest tests/test_episode06_full_logm_reformulation.py`
- `uv run pytest tests/test_episode06_full_seed_continuation.py tests/test_episode06_full_report.py tests/test_episode06_full_logm_reformulation.py`
- `uv run pytest`
<!-- SECTION:FINAL_SUMMARY:END -->
