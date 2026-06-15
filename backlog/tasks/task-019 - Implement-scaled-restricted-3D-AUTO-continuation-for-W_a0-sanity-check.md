---
id: TASK-019
title: Implement scaled restricted 3D AUTO continuation for W_a0 sanity check
status: To Do
assignee: []
created_date: '2026-06-15 20:17'
labels:
  - berton
  - auto
  - continuation
  - scaling
dependencies:
  - TASK-018
  - TASK-017
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Use the TASK-018 scaling diagnosis to build a restricted 3D AUTO equilibrium problem for the full Berton local balances, with w fixed to zero and unknowns such as scaled altitude, scaled horizontal velocity, and scaled log-mass or radius. First validate the formulation on W_a0 before attempting Hopf-focused H_a3 continuation.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A new episode AUTO variant is added for the restricted 3D equilibrium system without overwriting TASK-012 or TASK-015 artifacts.
- [ ] #2 State, residual, and parameter scalings follow TASK-018 recommendations and are documented with physical inverse conversions.
- [ ] #3 The TASK-011 seed is translated into restricted 3D AUTO coordinates and residuals/eigenvalues or equivalent stability diagnostics are cross-checked in Python.
- [ ] #4 W_a0 continuation is run at least in the easier sanity-check direction and compared against TASK-012/TASK-015 first-step failures.
- [ ] #5 Accepted points or failure diagnostics, AUTO commands/constants, and residual numerical risks are recorded in notebook/script/docs outputs.
<!-- AC:END -->
