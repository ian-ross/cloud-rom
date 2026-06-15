---
id: TASK-020
title: Retry H_a3 Hopf-control continuation on scaled restricted 3D system
status: To Do
assignee: []
created_date: '2026-06-15 20:17'
labels:
  - berton
  - auto
  - hopf
  - continuation
dependencies:
  - TASK-019
  - TASK-016
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
After the restricted 3D W_a0 sanity check demonstrates acceptable conditioning, retry H_a3 as the Hopf-relevant control on the scaled restricted equilibrium formulation. Treat this as the successor to the direct full-4D H_a3 retry, which should not be trusted until the restricted formulation passes the W_a0 gate.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 H_a3 continuation uses the scaled restricted 3D AUTO formulation validated by the W_a0 sanity check, or explicitly documents why the gate was not met.
- [ ] #2 AUTO branch results are parsed for accepted points, LP/HB/BP labels, eigenvalue diagnostics, and user-defined control anchors over a documented H_a3 range.
- [ ] #3 Python diagnostics independently evaluate residuals and critical eigenvalues along representative accepted points or explain why this is impossible.
- [ ] #4 Results are compared against the TASK-012 Python H_a3 probe and the failed full-4D AUTO attempts.
- [ ] #5 A companion note states whether there is AUTO-supported evidence for a Hopf candidate, no crossing, or continued numerical inconclusiveness.
<!-- AC:END -->
