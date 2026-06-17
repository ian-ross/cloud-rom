---
id: TASK-024
title: Continue full Berton z_W0 with smoothed updraft profile
status: To Do
assignee: []
created_date: '2026-06-17 11:03'
labels:
  - berton
  - auto
  - continuation
  - z_W0
  - full-model
  - smoothing
dependencies:
  - TASK-016
  - TASK-023
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Use the lessons from the restricted z_W0 continuation and the H_a3 scaling work to run a full-system AUTO continuation in the updraft-altitude control z_W0 with a smoothed updraft profile. This is the full-model counterpart to the paper-motivated steady-versus-oscillatory updraft-altitude experiment and should not proceed until the restricted smoothed z_W0 gate is understood.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The full-system AUTO formulation uses a smoothed updraft profile consistent with the restricted z_W0 task, with smoothing parameters and physical interpretation documented.
- [ ] #2 The full-model state, mass/arclength, parameter scaling, and continuation constants incorporate lessons from TASK-019, TASK-020, TASK-023, and TASK-016, or explicitly justify any deviations.
- [ ] #3 z_W0 continuation starts from the TASK-011/TASK-012 seed and covers a documented range relevant to the paper steady/oscillatory transition.
- [ ] #4 AUTO branch outputs are parsed for accepted parameter range, state movement, LP/HB/BP/special labels, stability index/eigenvalue diagnostics, and convergence failures.
- [ ] #5 Detected or suspected stability transitions are cross-checked with independent Python finite-difference or analytic Jacobian eigenvalues at representative branch points.
- [ ] #6 A companion note states whether full-system z_W0 provides AUTO-supported evidence for a Hopf/oscillatory transition, no crossing, or continued numerical inconclusiveness, without overstating results.
<!-- AC:END -->
