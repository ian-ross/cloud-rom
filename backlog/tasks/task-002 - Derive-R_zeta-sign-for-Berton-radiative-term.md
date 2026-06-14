---
id: TASK-002
title: Derive R_zeta sign for Berton radiative term
status: Done
assignee:
  - '@agent'
created_date: '2026-06-13 21:17'
updated_date: '2026-06-14 10:53'
labels: []
dependencies: []
references:
  - docs/berton_3d_hopf_briefing.md
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Derive the altitude derivative of the closed-form radiative term R(zeta, r) = Phi(T(zeta)) * (eta_a(zeta) - 1) * r using Berton profile definitions, and determine the sign of R_zeta and sigma_S + R_zeta at the baseline operating point.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Closed-form R(zeta, r) is represented symbolically with Phi(T(zeta)), eta_a(zeta), and r.
- [x] #2 Berton eta_a(z) and T(z) profiles from the briefing/paper equations are encoded for the relevant altitude layer.
- [x] #3 R_zeta = dR/dzeta is derived symbolically and all non-trivial intermediate expressions are printed.
- [x] #4 Baseline numerical values for R_zeta and sigma_S + R_zeta are computed with documented provenance for every parameter.
- [x] #5 The signs of R_zeta and sigma_S + R_zeta are reported prominently without presupposing Hopf or saddle.
- [x] #6 Any piecewise-profile branch assumptions for the baseline altitude are made explicit and validated.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect the existing Berton model and docs for the exact profile implementations and parameter defaults relevant to Task 1b: Atmosphere.temperature (Eqs. 75-76), relative_humidity_profile (Eqs. 78-79), atmospheric_eta/eta (Eqs. 80-81 / Case 0 behavior), and radiative_correction.
2. Add a focused TASK-002 script, likely scripts/berton_3d_hopf_task002_rzeta_sign.py, that mirrors TASK-001 style: clear banners, SymPy pretty-printing, loud assertions, and explicit provenance comments.
3. Represent the closed-form reduced radiative term symbolically as R(z, r) = Phi(T(z)) * (eta_a(z) - 1) * r, derive R_zeta = r*(Phi_T(T)*T_z*(eta_a - 1) + Phi(T)*eta_z), and print the general derivative before substituting any branch.
4. Encode the relevant piecewise-linear profile branches from the existing Atmosphere defaults: T(z) over 8-14 km, eta_a(z) below 9 km / 9-10 km / above 10 km, and humidity H_a(z) over 4-10 km and neighboring branches needed for baseline validation. Make branch intervals explicit.
5. Define Phi(T) numerically from the same closed-form factors used by radiative_correction at fixed crystal habit: A/(4*pi*C*K_a(T)*T) * sigma*T**4 * (L_s/(R_v*T)-1), with A/C proportional to r so that R is linear in r; use the existing model to compute/check the geometric proportionality at the baseline crystal habit.
6. Determine the baseline operating point for the cooling regime from existing model data rather than guessing: use Case 0 oscillatory settings, locate/approximate the reduced fixed point satisfying W_a(z*) = beta*r*^2 and S_i(z*) - 1 = R(z*, r*) if feasible, and document every fallback if the full fixed point cannot be uniquely recovered inside TASK-002.
7. Compute sigma_S = -d(S_i - 1)/dz at the same altitude using the ambient humidity, pressure, and saturation-pressure formulas already implemented in src/cloud_rom/berton2023.py; use symbolic branch derivatives where practical and finite-difference cross-checks against the existing functions.
8. Evaluate R_zeta and sigma_S + R_zeta numerically at the baseline operating point, including branch validation that z* lies in the stated T/eta/H intervals and noting discontinuity/kink risks near z=9 km or 10 km.
9. Print a prominent sign report for R_zeta and sigma_S + R_zeta, with units/scale notes and no Hopf/saddle conclusion beyond what TASK-002 is scoped to establish.
10. Add tests that exercise the profile branch formulas against the existing Atmosphere methods at representative altitudes and verify the script returns finite signs for the chosen baseline.
11. Run the TASK-002 script and targeted pytest tests, then update implementation notes, check completed ACs, and record any residual ambiguity for downstream TASK-003/TASK-005.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented TASK-002 radiative-gradient sign audit in scripts/berton_3d_hopf_task002_rzeta_sign.py.
- Represents R(z,r)=Phi(T(z))*(eta_a(z)-1)*r symbolically and prints dR/dz.
- Encodes Berton profile branches used at the baseline point: T 8--14 km, eta_a 9--10 km, H_l 4--10 km.
- Uses Case 0 oscillatory atmosphere and the paper's limiting operating point z*=9.63 km, D_i*=131 um; geometry factor A/(4*pi*C*r*) comes from existing LocalDiagnostics.
- Computes R_zeta analytically from branch formulas and cross-checks it by finite differencing the reduced R(z,r*) expression.
- Computes sigma_S=-d(S_i-1)/dz from existing Berton thermodynamics by finite difference.

Key numerical sign result at z*=9.63 km:
- R_zeta = +1.867397081546e-05 per m (POSITIVE).
- sigma_S = -7.510543575961e-05 per m (NEGATIVE at this baseline branch, contrary to the briefing's stated >0 assumption).
- sigma_S + R_zeta = -5.643146494416e-05 per m (NEGATIVE).

Validation run:
- uv run python scripts/berton_3d_hopf_task002_rzeta_sign.py
- uv run pytest tests/test_berton_3d_hopf_task001_symbolic.py tests/test_berton_3d_hopf_task002_rzeta_sign.py tests/test_berton2023.py  # 22 passed
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented the TASK-002 R_zeta sign derivation and baseline evaluation.

Changes:
- Added scripts/berton_3d_hopf_task002_rzeta_sign.py to derive R_zeta from R(z,r)=Phi(T(z))*(eta_a(z)-1)*r, print the symbolic derivative, substitute Berton profile branches, and evaluate the baseline signs.
- Encoded and tested the relevant piecewise-linear branches for T(z), eta_a(z), and H_l(z) against the existing Atmosphere implementation.
- Reused existing Berton thermodynamics and LocalDiagnostics to document provenance for the Case 0 oscillatory operating point and geometry factor.
- Added tests in tests/test_berton_3d_hopf_task002_rzeta_sign.py.

Baseline sign result at z*=9.63 km, D_i*=131 um:
- R_zeta is POSITIVE: +1.867397081546e-05 m^-1.
- sigma_S is NEGATIVE on this branch: -7.510543575961e-05 m^-1.
- sigma_S + R_zeta is NEGATIVE: -5.643146494416e-05 m^-1.

Note:
- The negative sigma_S follows directly from the existing Case 0 humidity/thermodynamic profile at 9.63 km, so it contradicts the briefing's stated sigma_S > 0 assumption. The script reports this plainly for downstream stability classification.

Tests:
- uv run python scripts/berton_3d_hopf_task002_rzeta_sign.py
- uv run pytest tests/test_berton_3d_hopf_task001_symbolic.py tests/test_berton_3d_hopf_task002_rzeta_sign.py tests/test_berton2023.py (22 passed)
<!-- SECTION:FINAL_SUMMARY:END -->
