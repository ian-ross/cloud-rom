---
id: TASK-022
title: >-
  Validate restricted Berton AUTO Fortran residuals Jacobians and PVLS
  diagnostics
status: In Progress
assignee:
  - '@pi'
created_date: '2026-06-16 13:24'
updated_date: '2026-06-16 13:38'
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

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Use TASK-021 results to decide which restricted AUTO source/config is the primary validation target, while retaining TASK-017 as the baseline failing implementation for comparison.
2. Build a Python validation script that writes/compiles a standalone Fortran driver around the restricted AUTO source and calls STPNT, FUNC with IJAC=0 and IJAC=2, and PVLS outside AUTO.
3. Define validation samples: the exact seed, predictor-like off-seed states/parameters taken from TASK-017/TASK-021 diagnostics, and TASK-012 Python W_a0 probe equilibria translated into restricted/scaled coordinates for W_a0 values such as 0.5, 0.7, and 1.0.
4. Compare Fortran FUNC residuals against Python restricted/scaled residuals at all samples, including near-zero residual checks at Python probe equilibria and tolerance-separated reporting for absolute and relative errors.
5. Validate DFDU by comparing the Fortran-returned Jacobian with centered finite differences of the same Fortran FUNC and with Python finite differences where useful; report row/column discrepancies and whether they are large enough to explain AUTO Newton divergence.
6. Validate DFDP for W_a0 and any active continuation parameters used by TASK-017/TASK-021, explicitly checking AUTO/Python parameter indexing and finite-difference step sizes.
7. Validate PVLS ancillary PAR outputs against Python local diagnostics for the same physical states; identify diagnostics that are trustworthy, mismatched, or should be excluded from ICP/output lists.
8. Write curated CSV/JSON outputs and a companion note concluding which suspected failure modes remain plausible: residual mismatch, DFDU mismatch, DFDP/indexing mismatch, PVLS/ICP misuse, parameter scaling/arclength issues, or an AUTO-only issue.
9. Add regression tests for the validation driver, sample coverage, residual/Jacobian/DFDP/PVLS summary outputs, and final failure-mode conclusion; run the relevant pytest selection.
<!-- SECTION:PLAN:END -->
