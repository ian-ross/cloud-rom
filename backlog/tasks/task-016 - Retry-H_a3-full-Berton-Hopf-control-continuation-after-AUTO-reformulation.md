---
id: TASK-016
title: Retry H_a3 full Berton Hopf-control continuation after AUTO reformulation
status: To Do
assignee: []
created_date: '2026-06-15 19:47'
labels:
  - berton
  - auto
  - hopf
  - H_a3
dependencies:
  - TASK-013
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
