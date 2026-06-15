---
id: TASK-004
title: Derive singular perturbation reduction for Berton 3D fixed point
status: Done
assignee:
  - '@agent'
created_date: '2026-06-13 21:18'
updated_date: '2026-06-15 12:12'
labels: []
dependencies:
  - TASK-001
  - TASK-003
references:
  - docs/berton_3d_hopf_briefing.md
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Derive and reconcile the k -> infinity slow dynamics of the corrected reduced 3D Berton system using both asymptotic cubic factorisation and direct slow-fast reduction with O(eps) inertial correction.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Route A substitutes k = 1/eps into the cubic, seeks slow roots as an eps series, prints collected orders, and extracts the reduced quadratic and slow-pair eigenvalues.
- [x] #2 Route B performs the Tikhonov/Fenichel slow-fast reduction with v quasi-steady plus the O(eps) inertial correction, not just the bare 2D collapse.
- [x] #3 The slow eigenvalues from Routes A and B are compared with an explicit symbolic simplify(A - B) == 0 check.
- [x] #4 The reduction reports whether the slow pair is genuinely k-independent and flags any residual k dependence.
- [x] #5 If the slow pair is oscillatory, its frequency is compared against the structure of Berton Eq. (119) and checked for cancellation of spurious k dependence.
- [x] #6 All intermediate series expansions, reduced dynamics, and eigenvalue expressions are printed readably.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Re-read TASK-001/TASK-003 scripts and the briefing sections on the corrected cubic and Berton Eq. (119).
2. Implement an auditable symbolic script for Route A: substitute k=1/eps in the corrected cubic, expand slow roots/slow factor in eps, print collected orders, and derive the limiting reduced quadratic/eigenvalues.
3. Implement Route B symbolically: introduce the slow manifold v = W(zeta,r) plus the O(eps) inertial correction, derive the corrected two-dimensional slow Jacobian, and print the reduced dynamics.
4. Add explicit SymPy comparisons that simplify Route A minus Route B to zero for the slow quadratic/eigenvalues and report any residual k dependence.
5. Compare oscillatory slow-pair frequency structure with Berton Eq. (119), explicitly checking cancellation of any spurious drag-rate k factors.
6. Add tests that import the symbolic helpers and assert the Route A/Route B equivalences, k-independence, and expected frequency structure.
7. Run the new script and targeted pytest suite, then update TASK-004 notes/ACs/final summary/status.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented TASK-004 singular-perturbation analysis in scripts/berton_3d_hopf_task004_singular_reduction.py.
- Route A substitutes k=1/eps into the corrected cubic with a=k*w and b=k*B, prints eps*P(lambda)=q0+eps*q1, derives q0=lambda^2+(w+c)lambda+(w*c-B*d), prints leading slow eigenvalues, and derives mu1=-q1(mu0)/q0'(mu0).
- Route B performs the slow-fast reduction eps*v_dot=F-v with F=-w*zeta-B*r and g=-d*zeta-c*r. It retains the O(eps) inertial correction h1=-D F dot [F,g], yielding M1=[[-(w^2+B*d), -B*(w+c)], [0,0]].
- Reconciled routes with SymPy: q0_A-q0_B simplifies to zero; q1_A-q1_B has zero remainder modulo q0; the numerator of mu1_A-mu1_B also has zero remainder modulo q0(mu0).
- Confirmed the leading slow pair is genuinely k/eps independent: q0 free symbols are only B,c,d,lambda,w.
- Printed oscillatory frequency structure omega0^2=det-trace^2/4=-(4*B*d+c^2-2*c*w+w^2)/4. In primitive gradients, the dominant Eq. 119-like product is -B*d=-2*beta*G*(sigma_S+R_zeta), with r_star and k canceled.

Validation run:
- uv run python scripts/berton_3d_hopf_task004_singular_reduction.py
- uv run pytest tests/test_berton_3d_hopf_task001_symbolic.py tests/test_berton_3d_hopf_task002_rzeta_sign.py tests/test_berton_3d_hopf_task003_root_tracking.py tests/test_berton_3d_hopf_task004_singular_reduction.py tests/test_berton2023.py  # 30 passed

Repository reorganization note: TASK-004 artifacts moved to episodes/02-reduced-model-cas/ (script: scripts/berton_3d_hopf_task004_singular_reduction.py within that episode).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented the TASK-004 symbolic singular-perturbation reduction for the corrected Berton 3D fixed point.

Changes:
- Added scripts/berton_3d_hopf_task004_singular_reduction.py with two independent derivations of the k -> infinity slow dynamics.
- Route A expands the corrected cubic after k=1/eps, extracts q0, q1, leading slow eigenvalues, and the O(eps) slow-root correction.
- Route B derives the Tikhonov/Fenichel slow manifold with O(eps) inertial correction, not just the bare 2D collapse.
- Added explicit SymPy reconciliation checks: leading quadratics match, O(eps) corrections agree modulo q0, and slow eigenvalue corrections agree modulo q0(mu0).
- Added the k-free frequency-structure check against Berton Eq. (119): the dominant oscillatory term is -B*d = -2*beta*G*(sigma_S + R_zeta), with spurious k and r_star factors canceled.
- Added tests in tests/test_berton_3d_hopf_task004_singular_reduction.py.

Result:
- The leading slow eigenvalues are the roots of lambda^2 + (w+c)lambda + (w*c-B*d)=0.
- The leading slow pair is genuinely k-independent.
- If oscillatory, omega0^2 = (w*c-B*d) - (w+c)^2/4 = -(4*B*d+c^2-2*c*w+w^2)/4.

Tests:
- uv run python scripts/berton_3d_hopf_task004_singular_reduction.py
- uv run pytest tests/test_berton_3d_hopf_task001_symbolic.py tests/test_berton_3d_hopf_task002_rzeta_sign.py tests/test_berton_3d_hopf_task003_root_tracking.py tests/test_berton_3d_hopf_task004_singular_reduction.py tests/test_berton2023.py (30 passed)
<!-- SECTION:FINAL_SUMMARY:END -->
