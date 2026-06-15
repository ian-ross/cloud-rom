---
id: TASK-006
title: Write Berton 3D Hopf-or-saddle analysis summary
status: Done
assignee:
  - '@agent'
created_date: '2026-06-13 21:18'
updated_date: '2026-06-15 12:12'
labels: []
dependencies:
  - TASK-001
  - TASK-002
  - TASK-003
  - TASK-004
  - TASK-005
references:
  - docs/berton_3d_hopf_briefing.md
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Produce the concise Markdown report for the reduced 3D Berton fixed-point analysis, summarizing the symbolic derivation, radiative-gradient sign result, root tracking, slow reductions, and final Hopf-versus-saddle verdict.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Report includes the symbolic Jacobian with corrected -b entry, characteristic polynomial, and a0 = k times 2D determinant factorisation.
- [x] #2 Report highlights the derived signs of R_zeta and sigma_S + R_zeta.
- [x] #3 Report includes the root-tracking table and its Hopf-versus-saddle diagnosis.
- [x] #4 Report includes reduced slow-pair eigenvalues from Routes A and B and states whether they agree.
- [x] #5 If oscillatory, report compares the slow-pair frequency to Berton Eq. (119).
- [x] #6 Report ends with a clear go/no-go verdict on whether the baseline fixed point is Hopf-capable stable spiral or saddle, and states the sign dependency that controls the answer.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Review outputs/scripts from TASK-001 through TASK-005 and the existing briefing/review docs to identify the best location/name for the final concise Markdown report.
2. Draft a standalone Markdown summary with sections for corrected symbolic Jacobian/cubic, radiative-gradient signs, root-tracking evidence, singular-reduction agreement, Eq. (119) frequency comparison, and final verdict.
3. Include auditable numeric values from the validated scripts, including the root table and the determinant/r_star discrepancy.
4. Add lightweight tests/checks that the report contains the required formulas, signs, root-tracking rows, Route A/B agreement statement, Eq. (119)-style product, and final verdict.
5. Run the report checks and targeted pytest suite.
6. Update TASK-006 notes/ACs/final summary/status.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented TASK-006 final Markdown report in docs/berton_3d_hopf_analysis_summary.md.
- Report includes corrected symbolic Jacobian with -b entry, characteristic polynomial a2=k+c, a1=k*c+a, a0=a*c-b*d, determinant factorization a0/k=w*c-B*d, and corrected Hopf locus k*(k*c+a+c^2)=-b*d.
- Highlights derived signs: R_zeta=+1.867771726333e-05 m^-1, sigma_S+R_zeta=-5.640219674712e-05 m^-1, d=-3.073061242928e-12 s^-1 m^-1.
- Includes root-tracking table for k=[1,10,100,1000,10000] and diagnosis that all swept roots are stable, with a fast root near -k and a stable slow complex pair.
- Includes singular perturbation Route A and Route B reduced slow-pair eigenvalues, including q0=lambda^2+(w+c)lambda+(w*c-B*d), inertial correction h1, and the agreement statement.
- Compares oscillatory frequency with Berton Eq. (119)-style structure: dominant term -B*d=-2*beta*G*(sigma_S+R_zeta), with no spurious k dependence.
- Ends with clear go/no-go verdict: baseline is a Hopf-capable stable spiral, not a saddle; answer hinges on the negative sigma_S+R_zeta sign.
- Added tests/test_berton_3d_hopf_analysis_summary.py to check required report content.

Validation run:
- uv run pytest tests/test_berton_3d_hopf_analysis_summary.py  # 4 passed
- uv run pytest tests/test_berton_3d_hopf_task001_symbolic.py tests/test_berton_3d_hopf_task002_rzeta_sign.py tests/test_berton_3d_hopf_task003_root_tracking.py tests/test_berton_3d_hopf_task004_singular_reduction.py tests/test_berton_3d_hopf_task005_classification.py tests/test_berton_3d_hopf_analysis_summary.py tests/test_berton2023.py  # 38 passed

Repository reorganization note: TASK-006 reduced-model summary/review artifacts moved to episodes/02-reduced-model-cas/docs/.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Produced the final concise Markdown report for the reduced Berton 3D Hopf-or-saddle analysis.

Changes:
- Added docs/berton_3d_hopf_analysis_summary.md with the corrected symbolic Jacobian, characteristic polynomial, determinant factorization, radiative-gradient sign result, root-tracking table, singular-reduction comparison, Eq. (119)-style frequency structure, and final verdict.
- Added tests/test_berton_3d_hopf_analysis_summary.py to assert the report contains the required formulas, signs, root table, Route A/B agreement statement, Eq. (119)-style term, and go/no-go verdict.

Verdict summarized in report:
- Baseline is a Hopf-capable stable spiral, not a corrected-Jacobian saddle.
- Controlling sign: sigma_S + R_zeta = -5.640219674712e-05 m^-1 < 0, so d < 0 and -b*d raises a0 above zero.
- All swept roots for k=[1,10,100,1000,10000] have negative real parts.
- The leading slow-pair frequency is k-free; dominant Eq. (119)-like product is -B*d=-2*beta*G*(sigma_S+R_zeta).

Tests:
- uv run pytest tests/test_berton_3d_hopf_analysis_summary.py
- uv run pytest tests/test_berton_3d_hopf_task001_symbolic.py tests/test_berton_3d_hopf_task002_rzeta_sign.py tests/test_berton_3d_hopf_task003_root_tracking.py tests/test_berton_3d_hopf_task004_singular_reduction.py tests/test_berton_3d_hopf_task005_classification.py tests/test_berton_3d_hopf_analysis_summary.py tests/test_berton2023.py (38 passed)
<!-- SECTION:FINAL_SUMMARY:END -->
