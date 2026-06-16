---
id: TASK-019
title: Implement scaled restricted 3D AUTO continuation for W_a0 sanity check
status: To Do
assignee: []
created_date: '2026-06-15 20:17'
updated_date: '2026-06-16 20:22'
labels:
  - berton
  - auto
  - continuation
  - scaling
dependencies:
  - TASK-018
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
In the new episode episodes/07-restricted-equilibrium-auto/, use the TASK-018 scaling diagnosis to build a restricted 3D AUTO equilibrium problem for local Berton balances, with w fixed to zero and unknowns such as scaled altitude, scaled horizontal velocity, and scaled log-mass or radius. First validate the formulation on W_a0 before attempting Hopf-focused H_a3 continuation.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A new episode AUTO variant is added for the restricted 3D equilibrium system without overwriting TASK-012 or TASK-015 artifacts.
- [ ] #2 State, residual, and parameter scalings follow TASK-018 recommendations and are documented with physical inverse conversions.
- [ ] #3 The TASK-011 seed is translated into restricted 3D AUTO coordinates and residuals/eigenvalues or equivalent stability diagnostics are cross-checked in Python.
- [ ] #4 W_a0 continuation is run at least in the easier sanity-check direction and compared against TASK-012/TASK-015 first-step failures.
- [ ] #5 Accepted points or failure diagnostics, AUTO commands/constants, and residual numerical risks are recorded in notebook/script/docs outputs.
- [ ] #6 The restricted W_a0 gate applies the TASK-022 arclength fix by continuing in P=M/10, where M=log(m/m_seed), and reports physical M and m via the inverse conversion.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Start from the TASK-018 recommended restricted residual and scalings in `episodes/07-restricted-equilibrium-auto/`, not the full-4D TASK-015 AUTO variant.
2. Implement a new AUTO problem under `episodes/07-restricted-equilibrium-auto/auto/`, with three unknowns and physical inverse conversion helpers documented in comments.
3. Translate the TASK-011 seed into the scaled restricted coordinates; verify the Fortran restricted residual against the Python diagnostic residual.
4. Configure `W_a0` as the continuation parameter with conservative steps and UZR/UZSTOP anchors guided by TASK-012/TASK-018.
5. Run at least the easier W_a0 direction first; only run the opposite direction if the first direction accepts nontrivial points or yields useful diagnostics.
6. Parse AUTO branch/solution/diagnostic files into `outputs/task019/`, including accepted parameter range, state movement, stability/eigenvalue diagnostics where available, and failure notes.
7. Compare explicitly against TASK-012/TASK-015 first-step failures and the TASK-012 Python W_a0 probe expectation of smooth stable equilibrium movement.
8. Write a notebook/script/doc record of commands, constants, scaling choices, accepted points or failure diagnostics, and residual risks.
9. Add tests for output artifacts, seed translation/cross-checks, W_a0 comparison, and the conditioning-gate conclusion for TASK-020.
<!-- SECTION:PLAN:END -->
