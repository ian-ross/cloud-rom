---
id: TASK-005
title: Classify Berton baseline fixed point as Hopf-capable or saddle
status: Done
assignee:
  - '@agent'
created_date: '2026-06-13 21:18'
updated_date: '2026-06-14 12:07'
labels: []
dependencies:
  - TASK-002
  - TASK-003
  - TASK-004
references:
  - docs/berton_3d_hopf_briefing.md
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Use the corrected symbolic algebra, derived radiative-gradient signs, and numerical root-tracking evidence to classify the baseline reduced 3D Berton fixed point and state the stability mechanism plainly.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The corrected Hopf locus k*(k*c + a + c^2) = -b*d is stated and tied to the corrected characteristic polynomial.
- [x] #2 The determinant relation a0 = k times the 2D determinant is stated and interpreted.
- [x] #3 The baseline fixed point is classified as Hopf-capable when a0 > 0 or saddle when a0 < 0, using the derived sign of sigma_S + R_zeta.
- [x] #4 If saddle, the report states what sign change or omitted feedback would be required to allow an oscillatory instability.
- [x] #5 If Hopf-capable, the report gives onset frequency, destabilising direction, and qualitative movement relative to the locus for the 10 km to 9 km transition.
- [x] #6 Any discrepancy between SymPy, root tracking, and the corrected hand derivation is surfaced explicitly.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Review TASK-001 through TASK-004 outputs/scripts for the final corrected polynomial, signs, root-tracking result, and singular-limit frequency expression.
2. Implement a concise classification script/report generator that imports the audited task helpers where useful, computes the baseline quantities, and prints the corrected Hopf locus, determinant relation, sign chain, root evidence, and singular-limit interpretation.
3. Classify the baseline as Hopf-capable or saddle strictly from derived sigma_S + R_zeta, a0, and root-tracking evidence; surface the known briefing r_star-power discrepancy explicitly.
4. Include the branch-specific discussion required by the ACs: for the actual Hopf-capable result, give onset-frequency structure, destabilising direction, and qualitative movement relative to the Hopf locus; also state what sign change would have produced a saddle / what omitted feedbacks could change the verdict.
5. Add tests asserting the classification, sign chain, Hopf-locus residual expression, determinant relation, and discrepancy reporting.
6. Run the classification script and targeted pytest suite, then update TASK-005 notes/ACs/final summary/status.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented TASK-005 classification in scripts/berton_3d_hopf_task005_classification.py.
- Consolidates corrected polynomial evidence: a2=k+c, a1=k*c+a, a0=a*c-b*d and Hopf residual a2*a1-a0=k*(k*c+a+c^2)+b*d.
- States and interprets a0=k*(2D determinant), with corrected primitive determinant G/r_star*(w*R_r - 2*beta*r_star*(sigma_S+R_zeta)).
- Surfaces the known briefing expanded-determinant discrepancy: the briefing candidate has r_star^2 in the second term, while the SymPy/TASK-001 derivation has one fewer power of r_star.
- Reuses TASK-003 baseline values/root tracking. Derived sigma_S+R_zeta=-5.640219674712e-05 m^-1 and d=-3.073061242928e-12 s^-1 m^-1.
- Classifies the baseline as HOPF-CAPABLE STABLE SPIRAL: a0(model k)=1.218837350209e-06 > 0, 2D determinant=5.630035864907e-08 > 0, and all swept roots have negative real parts.
- Gives the corrected destabilising direction: reduce positive RH residual toward zero by making b*d more negative, e.g. stronger negative d=(G/r*)(sigma_S+R_zeta), larger fall-speed slope B, or omitted feedbacks that reduce damping.
- States the counterfactual saddle condition: if sigma_S+R_zeta became positive, then d>0 and -b*d could drive a0<0.

Validation run:
- uv run python scripts/berton_3d_hopf_task005_classification.py
- uv run pytest tests/test_berton_3d_hopf_task001_symbolic.py tests/test_berton_3d_hopf_task002_rzeta_sign.py tests/test_berton_3d_hopf_task003_root_tracking.py tests/test_berton_3d_hopf_task004_singular_reduction.py tests/test_berton_3d_hopf_task005_classification.py tests/test_berton2023.py  # 34 passed
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented TASK-005 baseline stability classification for the corrected reduced Berton 3D fixed point.

Changes:
- Added scripts/berton_3d_hopf_task005_classification.py to consolidate TASK-001 through TASK-004 evidence into a plain-language verdict.
- Added tests/test_berton_3d_hopf_task005_classification.py covering corrected symbolic relations, determinant discrepancy reporting, baseline sign chain, root evidence, and k-free Eq. 119-like frequency structure.

Verdict:
- Baseline is a HOPF-CAPABLE STABLE SPIRAL, not a corrected-Jacobian saddle, for the fixed reduced parameters analyzed here.
- The decisive sign is sigma_S + R_zeta = -5.640219674712e-05 m^-1, so d < 0. Because b > 0, the corrected -b*d contribution raises a0 above zero.
- At the model instantaneous k, a0 = 1.218837350209e-06 > 0 and the 2D determinant a0/k = 5.630035864907e-08 > 0.
- Root tracking for k=[1,10,100,1000,1e4] s^-1 finds all max real parts negative, with one fast root near -k and a stable slow complex pair.

Mechanism:
- Corrected Hopf locus: k*(k*c+a+c^2) + b*d = 0.
- Destabilisation toward Hopf requires reducing the positive RH residual to zero, e.g. stronger negative d=(G/r*)(sigma_S+R_zeta), larger fall-speed slope B, or omitted feedbacks that reduce damping.
- If sigma_S+R_zeta became positive instead, d>0 and the corrected system could become a saddle through a0<0.

Discrepancy surfaced:
- SymPy/TASK-001 give one fewer power of r_star in the expanded determinant than the briefing candidate with r_star^2.

Tests:
- uv run python scripts/berton_3d_hopf_task005_classification.py
- uv run pytest tests/test_berton_3d_hopf_task001_symbolic.py tests/test_berton_3d_hopf_task002_rzeta_sign.py tests/test_berton_3d_hopf_task003_root_tracking.py tests/test_berton_3d_hopf_task004_singular_reduction.py tests/test_berton_3d_hopf_task005_classification.py tests/test_berton2023.py (34 passed)
<!-- SECTION:FINAL_SUMMARY:END -->
