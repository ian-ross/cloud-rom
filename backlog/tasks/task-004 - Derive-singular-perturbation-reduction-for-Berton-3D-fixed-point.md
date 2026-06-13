---
id: TASK-004
title: Derive singular perturbation reduction for Berton 3D fixed point
status: To Do
assignee: []
created_date: '2026-06-13 21:18'
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
