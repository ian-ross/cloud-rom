---
id: TASK-022
title: >-
  Validate restricted Berton AUTO Fortran residuals Jacobians and PVLS
  diagnostics
status: In Progress
assignee:
  - '@pi'
created_date: '2026-06-16 13:24'
updated_date: '2026-06-16 15:24'
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
1. Keep TASK-017 as the validation target because it is the failing implementation with user DFDU/DFDP and PVLS; use TASK-021 only as the stripped-control comparison proving the failure persists without those callbacks.
2. Build a Python-driven standalone Fortran validation harness that copies/compiles the TASK-017 restricted AUTO source with a generated driver, calls STPNT, FUNC with IJAC=0 and IJAC=2, and PVLS outside AUTO, and captures residuals, DFDU, DFDP, and selected PVLS PAR outputs.
3. Define validation samples from the seed, an implicit-tangent predictor-like point near W_a0=0.601, and TASK-012 Python W_a0 probe equilibria at W_a0=0.5, 0.7, and 1.0 translated into restricted/scaled coordinates.
4. Add a Python local branch-derivative check: compute DF/DU, DF/DW_a0, the implicit tangent dU/dW_a0, and compare the tangent prediction against nearby TASK-012 Python branch movement.
5. Add a minimal linear/affine surrogate continuation test using the validated local linear residual F(U,W)=A U + b(W-W0), with the same restricted coordinate and W_a0 control, to separate AUTO setup/tangent behavior from nonlinear Berton residual behavior.
6. Compare Fortran FUNC residuals against Python restricted/scaled residuals at all samples, including near-zero checks at Python probe equilibria and absolute/max-error summaries.
7. Validate TASK-017 DFDU against centered finite differences of Python/Fortran-equivalent residuals and validate DFDP for active controls W_a0, z_W0, H_a3, plus the TASK-017 diagnostic ICP slots where relevant to parameter-indexing risk.
8. Validate PVLS-written ancillary PAR diagnostics against Python local diagnostics for z/u/m and selected physical diagnostics; document whether PVLS remains plausible as a cause or should stay excluded from ICP lists.
9. Write curated CSV/JSON outputs and a companion note concluding which failure modes remain plausible: residual mismatch, DFDU mismatch, DFDP/indexing mismatch, PVLS/ICP misuse, parameter scaling/arclength/tangent issue, nonlinear residual issue, or AUTO-only setup issue.
10. Add regression tests for the validation driver, sample coverage, tangent check, linear surrogate outcome, residual/Jacobian/DFDP/PVLS summaries, and final failure-mode conclusion; run the relevant pytest selection.
<!-- SECTION:PLAN:END -->
