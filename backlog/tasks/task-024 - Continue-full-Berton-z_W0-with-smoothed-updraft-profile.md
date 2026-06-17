---
id: TASK-024
title: Continue full Berton z_W0 with smoothed updraft profile
status: To Do
assignee: []
created_date: '2026-06-17 11:03'
updated_date: '2026-06-17 11:06'
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

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Begin only after TASK-023 restricted smoothed z_W0 and TASK-016 full-system H_a3 have produced scaling/profile recommendations; do not run full-system z_W0 directly from the old kinked profile.
2. Port the TASK-023 smoothed updraft profile into the full Berton AUTO/Python diagnostic formulation, documenting the smoothing formula, width, and relationship to the original paper profile.
3. Incorporate full-system mass/arclength and parameter-control scaling lessons from TASK-019, TASK-020, TASK-023, and TASK-016, including physical inverse conversions and parser support.
4. Define the z_W0 continuation range from the paper steady/oscillatory updraft-altitude experiment and from TASK-023 restricted behavior; include anchors near the canonical seed and expected transition regions.
5. Run bidirectional full-system z_W0 continuation from the TASK-011/TASK-012 seed with documented AUTO constants and preserved raw `b/s/d` outputs under a distinct TASK-024 artifact path.
6. Parse branch outputs for accepted z_W0 range, physical state movement, LP/HB/BP/special labels, stability index/eigenvalues, periodic-orbit-relevant Hopf candidates, and convergence failures.
7. Cross-check representative branch points and any suspected stability transitions with independent Python full-system residuals and finite-difference/analytic Jacobian eigenvalues.
8. Compare the full-system z_W0 results against TASK-023 restricted z_W0, TASK-016 H_a3, TASK-012 Python probes, and the original paper steady/oscillatory motivation.
9. Write a companion verdict note stating whether smoothed full-system z_W0 provides AUTO-supported evidence for a Hopf/oscillatory transition, no crossing, or continued numerical inconclusiveness, and whether periodic-orbit continuation should be attempted next.
10. Add tests for smoothing consistency, coordinate/control scaling, artifact coverage, z_W0 range/anchor coverage, independent eigenvalue checks, and conservative verdict language.
<!-- SECTION:PLAN:END -->
