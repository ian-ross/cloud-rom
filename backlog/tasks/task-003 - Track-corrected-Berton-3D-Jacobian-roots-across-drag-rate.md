---
id: TASK-003
title: Track corrected Berton 3D Jacobian roots across drag rate
status: Done
assignee:
  - '@agent'
created_date: '2026-06-13 21:18'
updated_date: '2026-06-14 11:11'
labels: []
dependencies:
  - TASK-001
  - TASK-002
references:
  - docs/berton_3d_hopf_briefing.md
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement the numerical root-tracking cross-check for the corrected 3D characteristic polynomial across representative drag rates, using parameters and fixed-point derivatives from the existing numerical Berton model where possible.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 k, beta, G, r_star, w_prime, sigma_S, R_r, and R_zeta are obtained from the existing model or derived fixed point with provenance documented.
- [x] #2 Corrected a2, a1, and a0 coefficients are evaluated numerically for each selected drag rate.
- [x] #3 numpy.roots is run for k in [1, 10, 100, 1000, 1e4] s^-1 while holding slow physical parameters fixed.
- [x] #4 Roots are printed in a readable table for every k value.
- [x] #5 The output diagnoses saddle versus Hopf-capable behavior based on root real parts and consistency with the sign of a0.
- [x] #6 The symbolic Jacobian evaluated at the fixed point is compared against a finite-difference Jacobian from the existing reduced RHS to finite-difference accuracy.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Re-read TASK-001/TASK-002 scripts and the briefing to pin down corrected coefficient formulas and reusable derivative values.
2. Inspect existing Berton model APIs for local diagnostics, fixed-point state construction, drag-rate inputs, and reduced RHS components.
3. Implement an auditable root-tracking script that holds slow physical parameters fixed at the TASK-002 baseline while sweeping k = [1, 10, 100, 1000, 1e4] s^-1.
4. Compute corrected a2/a1/a0 coefficients, run numpy.roots, and print a readable table with saddle/Hopf-capable diagnostics and a0 sign consistency.
5. Add a reduced-RHS finite-difference Jacobian check against the symbolic Jacobian at the baseline fixed point.
6. Add tests covering coefficient construction, root table sign behavior, and symbolic-vs-finite-difference Jacobian agreement.
7. Run the new script and targeted pytest suite, then update TASK-003 acceptance criteria, notes, final summary, and status.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented TASK-003 root-tracking cross-check in scripts/berton_3d_hopf_task003_root_tracking.py.
- Solves local reduced growth balance s(z*)=R(z*,r*) for D_i*=131 um, giving z*=9618.062976835217 m.
- Derives beta from force balance W_a(z*)=beta*r*^2 and G from the existing mass-growth law converted to dr/dt=(G/r)*(S_i-1-R).
- Derives w_prime, sigma_S, R_r, and R_zeta from existing atmosphere/thermodynamic/radiative formulas with explicit provenance.
- Evaluates corrected a2=k+c, a1=k*c+a, a0=a*c-b*d and runs numpy.roots for k=[1,10,100,1000,1e4] s^-1.
- Result: all swept k have a0>0 and all root real parts negative; one fast root near -k plus a stable slow complex pair. This is not the saddle outcome for the fixed slow parameters, but the sweep alone is not a Hopf proof because no parameter is tuned through a crossing.
- Added finite-difference Jacobian check from reduced RHS against corrected symbolic Jacobian at the model instantaneous k.

Key signs at the fixed reduced baseline:
- R_r > 0, R_zeta > 0, sigma_S + R_zeta < 0, d < 0.
- w_prime = 0 because the solved z* lies above the Case 0 updraft ramp, where W_a is constant.

Validation run:
- uv run python scripts/berton_3d_hopf_task003_root_tracking.py
- uv run pytest tests/test_berton_3d_hopf_task001_symbolic.py tests/test_berton_3d_hopf_task002_rzeta_sign.py tests/test_berton_3d_hopf_task003_root_tracking.py tests/test_berton2023.py  # 26 passed
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented the TASK-003 corrected-Jacobian root-tracking analysis.

Changes:
- Added scripts/berton_3d_hopf_task003_root_tracking.py to derive baseline slow parameters from the existing Berton model, sweep drag rates, compute corrected cubic coefficients, run numpy.roots, and print saddle/Hopf-capable diagnostics.
- Added a finite-difference reduced-RHS Jacobian check against the corrected symbolic Jacobian.
- Added tests in tests/test_berton_3d_hopf_task003_root_tracking.py covering fixed-point consistency, coefficient/characteristic-polynomial agreement, root-sweep behavior, and finite-difference Jacobian agreement.

Baseline result:
- The local reduced fixed point is z*=9618.062976835217 m for D_i*=131 um.
- R_r > 0, R_zeta > 0, sigma_S + R_zeta < 0, so d < 0.
- For k=[1,10,100,1000,1e4] s^-1, a0>0 and all roots have negative real parts: one fast root near -k and a stable slow complex pair.
- Therefore the cheap root check does not show the corrected-Jacobian saddle outcome for this baseline; it shows Hopf-capable sign structure, though no Hopf bifurcation is proven because no control parameter is tuned through a crossing.

Tests:
- uv run python scripts/berton_3d_hopf_task003_root_tracking.py
- uv run pytest tests/test_berton_3d_hopf_task001_symbolic.py tests/test_berton_3d_hopf_task002_rzeta_sign.py tests/test_berton_3d_hopf_task003_root_tracking.py tests/test_berton2023.py (26 passed)
<!-- SECTION:FINAL_SUMMARY:END -->
