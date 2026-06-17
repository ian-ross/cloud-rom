---
id: TASK-023
title: Continue restricted z_W0 with smoothed updraft profile
status: To Do
assignee: []
created_date: '2026-06-17 11:03'
labels:
  - berton
  - auto
  - continuation
  - z_W0
  - smoothing
dependencies:
  - TASK-019
  - TASK-020
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add a restricted 3D AUTO continuation experiment for the updraft-altitude control z_W0 using the validated TASK-019 P=M/10 formulation and a smoothed updraft profile. This should test the paper-faithful updraft-altitude control without the unphysical piecewise kink/step causing continuation artifacts, and compare the restricted equilibrium/stability branch against prior W_a0/H_a3 lessons.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A smoothed updraft profile is implemented and documented, including the smoothing formula, smoothing width, physical inverse conversions, and how it relates to the original piecewise Berton profile.
- [ ] #2 The restricted 3D AUTO formulation reuses the validated TASK-019 state/residual scaling, including P=M/10 for mass arclength scaling, unless deviations are explicitly justified.
- [ ] #3 z_W0 continuation is run over a documented range relevant to the paper steady/oscillatory distinction, with raw AUTO commands/constants and b/s/d artifacts preserved under episode 07.
- [ ] #4 Accepted branch points are parsed into curated outputs with physical z/u/m, reconstructed M and P, smoothed updraft diagnostics, labels/special points/eigenvalue diagnostics where available, and convergence notes.
- [ ] #5 Representative branch points are cross-checked with Python residuals and critical eigenvalues or a documented equivalent stability diagnostic.
- [ ] #6 A companion note compares the restricted z_W0 result against TASK-019 W_a0, TASK-020 H_a3, and the original paper motivation, and states whether it supports a full-system z_W0 continuation attempt.
<!-- AC:END -->
