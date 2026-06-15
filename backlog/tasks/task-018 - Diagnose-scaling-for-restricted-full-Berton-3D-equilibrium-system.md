---
id: TASK-018
title: Diagnose scaling for restricted full-Berton 3D equilibrium system
status: To Do
assignee: []
created_date: '2026-06-15 20:17'
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
Before retrying H_a3 AUTO continuation, formulate the local equilibrium equations with w=0 and unknowns such as z, u, and log(m/m_seed), then quantify Jacobian conditioning, residual-row scales, state-column scales, singular values, and smoothness/branch risks near the TASK-011 seed. Use the result to recommend concrete AUTO state/residual scalings rather than guessing.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A Python diagnostic script/notebook defines the restricted 3D equilibrium residual and maps it consistently to the full physical state.
- [ ] #2 The TASK-011 seed residual and eigenvalue/stability relationship are cross-checked against existing full-system diagnostics.
- [ ] #3 Jacobian row norms, column norms, singular values/condition estimates, and parameter sensitivity for W_a0 and H_a3 are reported for unscaled and candidate scaled variables.
- [ ] #4 Non-smooth or branch-dependent pieces such as profile segments, MAX guards, terminal-Re fallback, and geometry solve are identified at the seed.
- [ ] #5 A companion note recommends specific state/residual/parameter scalings or explains why the restricted system remains unsuitable for AUTO.
<!-- AC:END -->
