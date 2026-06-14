---
id: TASK-004
title: Derive singular perturbation reduction for Berton 3D fixed point
status: In Progress
assignee:
  - '@agent'
created_date: '2026-06-13 21:18'
updated_date: '2026-06-14 11:36'
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
- [ ] #1 Route A substitutes k = 1/eps into the cubic, seeks slow roots as an eps series, prints collected orders, and extracts the reduced quadratic and slow-pair eigenvalues.
- [ ] #2 Route B performs the Tikhonov/Fenichel slow-fast reduction with v quasi-steady plus the O(eps) inertial correction, not just the bare 2D collapse.
- [ ] #3 The slow eigenvalues from Routes A and B are compared with an explicit symbolic simplify(A - B) == 0 check.
- [ ] #4 The reduction reports whether the slow pair is genuinely k-independent and flags any residual k dependence.
- [ ] #5 If the slow pair is oscillatory, its frequency is compared against the structure of Berton Eq. (119) and checked for cancellation of spurious k dependence.
- [ ] #6 All intermediate series expansions, reduced dynamics, and eigenvalue expressions are printed readably.
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
