---
id: TASK-009
title: Port full Berton RHS to AUTO-07p equilibrium problem
status: In Progress
assignee:
  - '@pi'
created_date: '2026-06-14 12:39'
updated_date: '2026-06-14 17:08'
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

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Confirm TASK-008 design choices and the installed AUTO-07p build/interface to use.
2. Create the full Berton AUTO problem directory and implement FUNC, STPNT, and PVLS or their chosen AUTO-interface equivalents.
3. Port the existing Python RHS carefully, preserving units and profile branches; avoid changing the existing Python model except for optional pure helper extraction if needed.
4. Build a Python comparison harness that evaluates both the existing Python RHS and the AUTO-port RHS at selected sample states/parameters.
5. Obtain a reproducible initial equilibrium using a Python steady solve and/or AUTO STPNT, and record the residual norm.
6. Run AUTO at the initial point and export fixed-point/eigenvalue information.
7. Add validation tests or scripts comparing AUTO residuals/eigenvalues with an independent Python finite-difference Jacobian calculation.
8. Document build/run commands, tolerances, any scaling choices, and discrepancies.
<!-- SECTION:PLAN:END -->
