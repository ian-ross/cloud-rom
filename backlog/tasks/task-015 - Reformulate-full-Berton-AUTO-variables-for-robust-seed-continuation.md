---
id: TASK-015
title: Reformulate full Berton AUTO variables for robust seed continuation
status: To Do
assignee: []
created_date: '2026-06-15 19:47'
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
