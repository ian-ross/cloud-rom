---
id: TASK-009
title: Port full Berton RHS to AUTO-07p equilibrium problem
status: Done
assignee:
  - '@pi'
created_date: '2026-06-14 12:39'
updated_date: '2026-06-15 12:12'
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
- [x] #1 AUTO problem files compile/run under the installed AUTO-07p environment without requiring Julia.
- [x] #2 The RHS numerically matches the existing Python Berton RHS at selected state/parameter samples within documented tolerances.
- [x] #3 An initial equilibrium is obtained from either a Python steady solve or AUTO STPNT and its residual norm is reported.
- [x] #4 PVLS or equivalent auxiliary output reports the mechanism diagnostics selected in the design task.
- [x] #5 A Python-side validation script compares AUTO fixed-point residual/eigenvalue data against independent Python finite-difference Jacobian/eigenvalue calculations at the initial equilibrium.
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

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
- Implemented a genuine Fortran AUTO-07p problem in auto/berton_full/bertonfull.f90 for U=(z,u,w,m), with FUNC/STPNT/PVLS and a finite-difference Jacobian supplied to AUTO for meaningful eigenvalues.
- Added auto/berton_full/c.bertonfull and run_auto.sh; ran AUTO successfully and saved b/s/d.bertfull-zW0 outputs.
- Added scripts/berton_full_auto_task009_validate.py to compile a standalone Fortran RHS driver, compare against src/cloud_rom/berton2023.py samples, parse AUTO fixed-point/eigenvalue data, and compare with independent Python/Fortran finite-difference spectra.
- Added docs/berton_full_auto_task009_validation.md and pytest coverage in tests/test_berton_full_auto_task009_validate.py.

Repository reorganization note: TASK-009 full-model AUTO problem and validation artifacts moved to episodes/04-full-model-auto-equilibria/ (auto/, docs/, scripts/ subdirectories).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented the full Berton AUTO-07p equilibrium problem as Fortran.

Changes:
- Added auto/berton_full/bertonfull.f90 with a four-state AUTO problem U=(z,u,w,m), porting the Python Berton RHS physics: atmospheric profiles, thermodynamics, crystal geometry, drag/ventilation, radiation, and mass growth.
- Added AUTO constants/run files and saved reproducible AUTO outputs for z_W0 continuation.
- Added PVLS diagnostics for sigma_S, R_zeta, sigma_S+R_zeta, radiative correction, drag/ventilation, thermodynamic state, geometry, force/growth residuals, slope proxies, and reduced_det_proxy.
- Added a validation script that compiles the Fortran port, compares RHS samples against the Python reference, parses AUTO fixed-point residual/eigenvalues, and cross-checks spectra against independent finite-difference Jacobians.
- Documented commands, tolerances, initial equilibrium, residual norm, diagnostics, and validation output in docs/berton_full_auto_task009_validation.md.

Validation:
- bash auto/berton_full/run_auto.sh
- uv run python scripts/berton_full_auto_task009_validate.py
- uv run pytest tests/test_berton_full_auto_task009_validate.py
<!-- SECTION:FINAL_SUMMARY:END -->
