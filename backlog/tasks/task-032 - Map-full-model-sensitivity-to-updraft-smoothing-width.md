---
id: TASK-032
title: Map full-model sensitivity to updraft smoothing width
status: To Do
assignee: []
created_date: '2026-06-17 21:23'
labels:
  - berton
  - continuation
  - python
  - zw0
  - smoothing
  - episode-10
dependencies:
  - TASK-029
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Extend the Episode 10 Python continuation workflow to treat updraft smoothing width as a scientific continuation/sensitivity parameter, not only a numerical staging aid. Use fixed-z_W0 smoothing continuation and two-parameter-style sampling in (z_W0, smoothing width) to determine whether the transition-region obstruction is branch geometry/fold-like behavior, a singular smoothing/nonsmoothness limit, scaling, or unresolved numerical failure.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Continuation experiments at fixed z_W0 anchors in the 9.6-10 km transition region vary smoothing width from easy values toward and below the TASK-023/TASK-024 50 m width when numerically reachable
- [ ] #2 A two-parameter-style sampling or continuation map over z_W0 and smoothing width records accepted equilibria, residuals, conditioning diagnostics, eigenvalue spectra, and rejected-step behavior
- [ ] #3 Diagnostics explicitly test for fold/turn or near-singular branch geometry using tangent components, fixed-control state Jacobian singular values, branch Jacobian singular values, or documented equivalent indicators
- [ ] #4 Results relate the z_W0 fragility to updraft-profile regularity and distinguish branch geometry, singular smoothing/nonsmoothness limit, scaling, and unresolved numerical failure without overstating inconclusive cases
<!-- AC:END -->
