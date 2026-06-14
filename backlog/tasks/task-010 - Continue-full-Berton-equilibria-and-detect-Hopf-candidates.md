---
id: TASK-010
title: Continue full Berton equilibria and detect Hopf candidates
status: Done
assignee:
  - '@pi'
created_date: '2026-06-14 12:39'
updated_date: '2026-06-14 19:20'
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
- [x] #1 Continuation commands/configuration are checked in or documented so the run is reproducible.
- [x] #2 The equilibrium branch is continued across the Berton-relevant parameter interval, including the 10 km to 9 km updraft-base regime or chosen equivalent control range.
- [x] #3 AUTO special points are catalogued, including LP, HB, BP, or explicit absence of such detections.
- [x] #4 Eigenvalue/stability changes at detected or suspected Hopf points are cross-checked with independent Python Jacobian/eigenvalue calculations.
- [x] #5 A summary plot or table shows parameter value, equilibrium state, stability index, critical eigenvalues, and mechanism diagnostics along the branch.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Start from the validated AUTO full-model equilibrium problem from TASK-009.
2. Configure AUTO constants and stopping criteria for equilibrium continuation across the Berton-relevant primary-control interval.
3. Run continuation in both directions if needed to cover the 10 km to 9 km updraft-base regime or selected equivalent range.
4. Catalog AUTO special points, including LP, HB, BP, and any failed/ambiguous detections.
5. Extract branch data into a machine-readable table containing parameter value, equilibrium state, stability index, critical eigenvalues, and PVLS mechanism diagnostics.
6. Cross-check detected or suspected Hopf points with independent Python finite-difference Jacobian/eigenvalue calculations.
7. Generate a summary plot or table and write a concise continuation note describing branch structure, stability changes, and uncertainties.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
- Added notebook-driven TASK-010 workflow in notebooks/berton_full_auto_task010_continuation.ipynb.
- Added scripts/berton_full_auto_task010_analyze.py to parse AUTO b/s/d files, catalogue LP/HB/BP detections, cross-check labeled-solution eigenvalues with Python finite-difference Jacobians, and generate CSV/Markdown/PNG outputs under outputs/task010/.
- Documented results in docs/berton_full_auto_task010_continuation.md: no LP/HB/BP/Hopf detected over z_W0=10 km to 9 km; branch remains at z*=10178.504 m with one positive real eigenvalue and no complex critical pair.
- Added pytest coverage in tests/test_berton_full_auto_task010_analyze.py; full test suite passes.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Completed full Berton equilibrium continuation analysis for TASK-010.

Changes:
- Added a reproducible notebook workflow for the AUTO z_W0 continuation and analysis.
- Added scripts/berton_full_auto_task010_analyze.py to parse AUTO branch/solution/diagnostic files, catalogue LP/HB/BP detections, cross-check labeled equilibria with independent Python finite-difference Jacobians, and generate summary CSV/Markdown/PNG artifacts.
- Added documentation of the continuation interval, special-point catalogue, stability result, and implication for follow-up controls.
- Added tests for parser coverage, Berton 10 km to 9 km interval coverage, stability/eigenvalue cross-checks, and generated outputs.

Result:
- No LP, HB, or BP labels were detected on the first physical z_W0 branch.
- The 10 km to 9 km interval remains on the same saturated-updraft equilibrium at z*=10178.504 m with one positive real eigenvalue (AUTO/Python critical real part ~2.38933e-4 s^-1) and no Hopf candidate.

Validation:
- uv run python scripts/berton_full_auto_task010_analyze.py --run-auto
- uv run pytest
<!-- SECTION:FINAL_SUMMARY:END -->
