---
id: TASK-009
title: Port full Berton RHS to AUTO-07p equilibrium problem
status: To Do
assignee: []
created_date: '2026-06-14 12:39'
labels:
  - berton
  - auto
  - continuation
dependencies:
  - TASK-008
references:
  - src/cloud_rom/berton2023.py
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement the full Berton 2023 model RHS as an AUTO-07p continuation problem using the state/parameter mapping from the design task, with a reproducible initial equilibrium.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 AUTO problem files compile/run under the installed AUTO-07p environment without requiring Julia.
- [ ] #2 The RHS numerically matches the existing Python Berton RHS at selected state/parameter samples within documented tolerances.
- [ ] #3 An initial equilibrium is obtained from either a Python steady solve or AUTO STPNT and its residual norm is reported.
- [ ] #4 PVLS or equivalent auxiliary output reports the mechanism diagnostics selected in the design task.
- [ ] #5 A Python-side validation script compares AUTO fixed-point residual/eigenvalue data against independent Python finite-difference Jacobian/eigenvalue calculations at the initial equilibrium.
<!-- AC:END -->
