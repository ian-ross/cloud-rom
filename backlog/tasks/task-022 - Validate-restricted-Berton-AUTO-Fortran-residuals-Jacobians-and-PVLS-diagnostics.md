---
id: TASK-022
title: >-
  Validate restricted Berton AUTO Fortran residuals Jacobians and PVLS
  diagnostics
status: To Do
assignee: []
created_date: '2026-06-16 13:24'
labels:
  - berton
  - auto
  - fortran
  - validation
  - diagnostics
dependencies:
  - TASK-017
  - TASK-021
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Systematically validate the restricted/scaled Berton AUTO Fortran implementation used for W_a0 continuation. Compile a standalone Fortran driver around the AUTO source and compare FUNC residuals, DFDU, DFDP, and PVLS ancillary diagnostics against Python finite differences and local diagnostics at the seed, off-seed predictor-like points, and TASK-012 Python W_a0 probe equilibria.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A standalone validation script compiles/calls the restricted AUTO Fortran source outside AUTO, including STPNT, FUNC with IJAC=2, and PVLS.
- [ ] #2 Fortran restricted/scaled FUNC residuals are compared with Python residuals at the seed, predictor-like off-seed points, and selected TASK-012 W_a0 probe equilibria such as W_a0=0.5, 0.7, and 1.0.
- [ ] #3 Fortran DFDU is compared against centered finite differences of the Fortran FUNC itself and/or Python finite differences, with tolerances and any discrepancies reported.
- [ ] #4 Fortran DFDP for W_a0, and any other active continuation parameters used by recent runs, is compared against centered finite differences in PAR values, with special attention to parameter indexing.
- [ ] #5 PVLS-written ancillary PAR diagnostics are compared against Python local diagnostics for the same physical states, or any unvalidated diagnostics are explicitly removed from continuation ICP lists and documented.
- [ ] #6 The report concludes which of the suspected failure modes remains plausible: residual mismatch, DFDU mismatch, DFDP/indexing mismatch, PVLS/ICP misuse, parameter scaling, or an AUTO issue not reproduced by standalone checks.
<!-- AC:END -->
