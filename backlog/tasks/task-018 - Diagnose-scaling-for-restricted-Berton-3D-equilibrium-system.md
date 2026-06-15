---
id: TASK-018
title: Diagnose scaling for restricted Berton 3D equilibrium system
status: To Do
assignee: []
created_date: '2026-06-15 20:17'
updated_date: '2026-06-15 20:20'
labels:
  - berton
  - auto
  - scaling
  - diagnostics
dependencies:
  - TASK-015
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Start a new episode, episodes/07-restricted-equilibrium-auto/, for restricted/local Berton equilibrium continuation work. Before retrying H_a3 AUTO continuation, formulate the local equilibrium equations with w=0 and unknowns such as z, u, and log(m/m_seed), then quantify Jacobian conditioning, residual-row scales, state-column scales, singular values, and smoothness/branch risks near the TASK-011 seed. Use the result to recommend concrete AUTO state/residual scalings rather than guessing.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A Python diagnostic script/notebook defines the restricted 3D equilibrium residual and maps it consistently to the full physical state.
- [ ] #2 The TASK-011 seed residual and eigenvalue/stability relationship are cross-checked against existing full-system diagnostics.
- [ ] #3 Jacobian row norms, column norms, singular values/condition estimates, and parameter sensitivity for W_a0 and H_a3 are reported for unscaled and candidate scaled variables.
- [ ] #4 Non-smooth or branch-dependent pieces such as profile segments, MAX guards, terminal-Re fallback, and geometry solve are identified at the seed.
- [ ] #5 A companion note recommends specific state/residual/parameter scalings or explains why the restricted system remains unsuitable for AUTO.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Create/use the new episode directory `episodes/07-restricted-equilibrium-auto/` with README, `notebooks/`, `scripts/`, `docs/`, and `outputs/task018/` as needed.
2. Reuse the Python physical RHS and TASK-011 seed artifacts from episodes 04-06, but define the restricted local equilibrium residual as three balances at `w=0` rather than the full 4D ODE equilibrium.
3. Choose initial restricted coordinates to diagnose, at minimum physical `(z,u,log(m/kg))` and centered/scaled `(Z,U,M=log(m/m_seed))`; document inverse conversions to physical state.
4. Evaluate the TASK-011 seed residual and relate the restricted residual/Jacobian stability information back to the existing full-system residual and eigenvalues.
5. Compute finite-difference Jacobians and parameter sensitivities for `W_a0` and `H_a3`; report row norms, column norms, singular values, condition estimates, and effects of candidate diagonal state/residual scalings.
6. Inspect active profile/updraft/humidity/radiation/drag/geometry branches at the seed and identify non-smooth pieces or guards that could make AUTO finite differences unreliable.
7. Write a companion note with a concrete scaling recommendation for TASK-019, or a clear stop recommendation if the restricted 3D system remains badly conditioned.
8. Add lightweight tests that verify the diagnostic artifacts exist, the seed residual is small, conditioning metrics are reported, and the note does not overstate continuation readiness.
<!-- SECTION:PLAN:END -->
