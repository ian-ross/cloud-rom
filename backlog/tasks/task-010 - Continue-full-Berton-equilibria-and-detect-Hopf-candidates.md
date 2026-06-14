---
id: TASK-010
title: Continue full Berton equilibria and detect Hopf candidates
status: To Do
assignee: []
created_date: '2026-06-14 12:39'
labels:
  - berton
  - auto
  - hopf
dependencies:
  - TASK-009
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Run AUTO-07p equilibrium continuation for the full Berton model over the selected control parameter and identify folds, Hopf points, and stability changes.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Continuation commands/configuration are checked in or documented so the run is reproducible.
- [ ] #2 The equilibrium branch is continued across the Berton-relevant parameter interval, including the 10 km to 9 km updraft-base regime or chosen equivalent control range.
- [ ] #3 AUTO special points are catalogued, including LP, HB, BP, or explicit absence of such detections.
- [ ] #4 Eigenvalue/stability changes at detected or suspected Hopf points are cross-checked with independent Python Jacobian/eigenvalue calculations.
- [ ] #5 A summary plot or table shows parameter value, equilibrium state, stability index, critical eigenvalues, and mechanism diagnostics along the branch.
<!-- AC:END -->
