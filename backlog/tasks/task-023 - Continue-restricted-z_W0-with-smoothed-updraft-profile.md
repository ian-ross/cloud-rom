---
id: TASK-023
title: Continue restricted z_W0 with smoothed updraft profile
status: In Progress
assignee:
  - '@pi'
created_date: '2026-06-17 11:03'
updated_date: '2026-06-17 11:41'
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
- [x] #1 A smoothed updraft profile is implemented and documented, including the smoothing formula, smoothing width, physical inverse conversions, and how it relates to the original piecewise Berton profile.
- [x] #2 The restricted 3D AUTO formulation reuses the validated TASK-019 state/residual scaling, including P=M/10 for mass arclength scaling, unless deviations are explicitly justified.
- [x] #3 z_W0 continuation is run over a documented range relevant to the paper steady/oscillatory distinction, with raw AUTO commands/constants and b/s/d artifacts preserved under episode 07.
- [x] #4 Accepted branch points are parsed into curated outputs with physical z/u/m, reconstructed M and P, smoothed updraft diagnostics, labels/special points/eigenvalue diagnostics where available, and convergence notes.
- [x] #5 Representative branch points are cross-checked with Python residuals and critical eigenvalues or a documented equivalent stability diagnostic.
- [x] #6 A companion note compares the restricted z_W0 result against TASK-019 W_a0, TASK-020 H_a3, and the original paper motivation, and states whether it supports a full-system z_W0 continuation attempt.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Read TASK-019 and TASK-020 first; use the validated restricted scaling (`Z`, `U`, `P=M/10`) and any H_a3-specific arclength lessons before introducing z_W0.
2. Implement a smoothed updraft profile in the restricted AUTO/Python diagnostic path, replacing the piecewise ramp/plateau kink with a documented smooth transition. Use a smoothing width that is physically interpretable and small relative to the atmospheric scale, and retain the original profile as the limiting/reference case.
3. Define the z_W0 continuation coordinate and scaling. Because z_W0 is in metres and may have weak sensitivity while the seed is on the updraft plateau, choose either raw z_W0 with appropriate DS/DSMAX or a scaled control `q_z=(z_W0-z_W0_seed)/z_scale`; document the physical mapping.
4. Build a new restricted AUTO variant under episode 07 without overwriting TASK-019/TASK-020 artifacts, preserving `P=M/10`, row-scaled residuals, and physical inverse conversions.
5. Cross-check the TASK-011/TASK-012 seed residual and local tangent in Python under the smoothed updraft profile; record how much smoothing perturbs the seed relative to the original profile.
6. Run z_W0 continuation over a range relevant to the paper steady/oscillatory updraft-altitude distinction, including ranges where the equilibrium approaches or crosses the smoothed ramp region.
7. Parse raw AUTO outputs into `outputs/task023/`, including accepted z_W0 range, physical z/u/m movement, P/M conversion, smoothed updraft diagnostics, labels/eigenvalues where available, and convergence notes.
8. Independently evaluate Python residuals and critical eigenvalues at representative branch points and any suspected stability transitions.
9. Write a companion note comparing restricted z_W0 behavior against TASK-019 W_a0 and TASK-020 H_a3, explaining whether smoothing avoids kink artifacts and whether the result motivates full-system z_W0 continuation.
10. Add tests for the smoothing formula, seed perturbation, scaling/inverse conversions, artifact coverage, Python cross-checks, and conservative conclusion language.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
- Added AUTO variant auto/berton_restricted_task023_zw0_smooth with TASK-019 Z/U/P=M/10 scaling, q_z=(z_W0-9000 m)/1000 m control, and softplus-smoothed updraft width 50 m.
- Ran bidirectional z_W0 AUTO. Upward branch reaches z_W0≈9710 m before DGEBAL/floating-point failure near the seed/ramp transition; downward branch reaches the paper oscillatory 7000 m setting and continues farther before MX.
- Curated outputs in outputs/task023 with branch parsing, smoothing diagnostics, seed perturbation, representative Python residual/eigenvalue checks, verdict JSON/CSV, notebook command record, and companion note.
- Verification: uv run pytest tests/test_episode07_restricted_task019.py tests/test_episode07_restricted_task020.py tests/test_episode07_restricted_task023.py (13 passed).
<!-- SECTION:NOTES:END -->
