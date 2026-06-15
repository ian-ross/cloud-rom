---
id: TASK-015
title: Reformulate full Berton AUTO variables for robust seed continuation
status: To Do
assignee: []
created_date: '2026-06-15 19:47'
updated_date: '2026-06-15 19:48'
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
- [ ] #1 AUTO formulation uses a better-conditioned cloud-size variable, e.g. log-mass or radius, with documented physical-state conversions.
- [ ] #2 Analytic DFDU and/or DFDP derivatives are implemented where practical, or remaining finite-difference pieces are explicitly justified.
- [ ] #3 The TASK-011 equilibrium seed is translated into the reformulated AUTO coordinates and its RHS residual/eigenvalues are cross-checked against Python diagnostics.
- [ ] #4 First-step convergence is retried for at least one non-z_W0 control and compared against the TASK-012 minimum-step failures.
- [ ] #5 Notebook/script documentation records commands, constants, scaling choices, accepted points or failure diagnostics, and residual numerical risks.
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
