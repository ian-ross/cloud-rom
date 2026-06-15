---
id: TASK-016
title: Retry H_a3 full Berton Hopf-control continuation after AUTO reformulation
status: To Do
assignee: []
created_date: '2026-06-15 19:47'
updated_date: '2026-06-15 20:18'
labels:
  - berton
  - auto
  - hopf
  - H_a3
dependencies:
  - TASK-013
  - TASK-015
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Using the improved full-model AUTO formulation, retry H_a3 as the primary local-stability/Hopf-control candidate suggested by the TASK-012 Python probe. Determine whether AUTO validates a nontrivial equilibrium branch and any Hopf or stability crossing near the canonical Case-0 seed.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Continuation starts from the TASK-011/TASK-012 equilibrium seed in the reformulated AUTO variables.
- [ ] #2 H_a3 is varied in both relevant directions over a documented range that includes the canonical value 0.61 and probes the Python-predicted stability-crossing region.
- [ ] #3 AUTO branch outputs report accepted parameter range, special points, stability index, eigenvalues, and any convergence failures.
- [ ] #4 Detected or suspected Hopf/stability crossings are cross-checked with independent Python finite-difference or analytic Jacobian eigenvalues.
- [ ] #5 Results clearly state whether H_a3 provides an AUTO-validated Hopf candidate, only a numerical hint, or a negative/inconclusive result.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Wait for TASK-015 to provide the improved/reformulated AUTO setup and confirm the seed translation/eigenvalue cross-check passes.
2. Clone or parameterize the TASK-015 AUTO variant for H_a3 as the principal continuation parameter, preserving the canonical Case-0 seed at H_a3=0.61.
3. Define bidirectional H_a3 continuation ranges informed by the TASK-012 Python probe, including the canonical value and the region where the critical real part changed sign.
4. Run AUTO continuation in both H_a3 directions with documented constants, step controls, UZR anchors, and any scaling choices inherited from TASK-015.
5. Parse branch, solution, and diagnostic files to catalogue accepted parameter range, LP/HB/BP/special labels, stability index, eigenvalues, and convergence failures.
6. For any suspected or detected stability crossing, run independent Python Jacobian/eigenvalue cross-checks at nearby labeled or sampled branch points.
7. Generate plots/tables for H_a3 versus equilibrium state, critical eigenvalues, stability index, and special points.
8. Write a companion note giving a clear verdict: AUTO-validated Hopf candidate, numerical hint only, negative result, or inconclusive due to remaining convergence problems; include residual risks and follow-up recommendations.
9. Add tests covering required artifacts, H_a3 range coverage or documented failure, special-point/eigenvalue diagnostics, and non-overstated verdict language.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
TASK-015 showed the log-mass full-4D reformulation still fails the easier W_a0 sanity check with NaN/DGEBAL divergence. Do not treat a direct H_a3 retry on that formulation as a meaningful validation attempt until restricted-3D scaling work (TASK-018/TASK-019) provides a better-conditioned gate.
<!-- SECTION:NOTES:END -->
