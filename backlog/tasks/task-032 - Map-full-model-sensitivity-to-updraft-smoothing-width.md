---
id: TASK-032
title: Map full-model sensitivity to updraft smoothing width
status: In Progress
assignee:
  - '@pi'
created_date: '2026-06-17 21:23'
updated_date: '2026-06-18 10:58'
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

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Review TASK-029 script/outputs and recap note to identify reusable smoothed-updraft functions, z_W0 scaling, accepted branch anchors, rejected-step patterns, and existing diagnostics for branch/state Jacobian conditioning.
2. Design the smoothing-width continuation coordinate, using a positive transform such as log(width_m/50 m) or an affine width scale, and add physical inverse mappings so widths above, at, and below 50 m are recorded clearly.
3. Implement fixed-z_W0 continuation experiments at transition-region anchors, initially z_W0=9600, 9700, 9800, 9900, and near the TASK-029 obstruction around 9930 m, continuing smoothing width from easy values (e.g. 300/150/100 m) toward 50 m and below when reachable.
4. Implement a two-parameter-style sampling map over (z_W0, smoothing width), seeded from known TASK-029 accepted points where possible, with Newton refinement at grid/anchor points and explicit accepted/rejected classifications.
5. Add fold/turn/near-singular diagnostics for each accepted point: branch tangent components, fixed-control state-Jacobian singular values/condition estimates, branch-Jacobian singular values, residual norms, eigenvalue spectra, stable counts, and correction/rejection metadata.
6. Curate outputs under episodes/10-full-model-python-continuation/outputs/task032/ and write a companion doc explaining whether the obstruction is best interpreted as fold-like branch geometry, a singular smoothing/nonsmoothness limit, scaling, or unresolved numerical failure.
7. Add regression tests for smoothing-width mappings, fixed-anchor coverage, two-parameter map schema, diagnostic completeness, and conservative verdict language; run the TASK-032 script/tests plus relevant TASK-029 and episode-10 tests.
8. After validation, update TASK-032 notes, check satisfied acceptance criteria, write a PR-style final summary, and mark the task done.
<!-- SECTION:PLAN:END -->
