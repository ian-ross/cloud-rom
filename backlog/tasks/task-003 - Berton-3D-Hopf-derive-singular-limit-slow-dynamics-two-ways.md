---
id: TASK-003
title: 'Berton 3D Hopf: derive singular-limit slow dynamics two ways'
status: To Do
assignee: []
created_date: '2026-06-13 20:21'
labels:
  - analysis
  - sympy
  - asymptotics
  - berton
  - hopf
dependencies: []
references:
  - docs/berton_3d_hopf_briefing.md
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement the k -> infinity singular-perturbation analysis for the reduced Berton 3D Hopf model after the numerical root-tracking sanity check. Derive the slow-pair frequency independently from cubic asymptotics and from a corrected slow-fast reduction, then reconcile the two routes.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Route A substitutes k = 1/eps into the cubic, assumes lam = lam0 + eps*lam1 + ..., prints the collected orders, and solves explicitly for the slow-root expansion.
- [ ] #2 Route A extracts and prints the reduced quadratic and Omega_0^2, noting any correction to the hand-derived expectation.
- [ ] #3 Route B treats v as the fast variable, retains the first-order correction v = W_a - V_f + eps*v_1 + ..., derives the corrected slow dynamics to O(eps), and prints the resulting oscillator.
- [ ] #4 Route B extracts and prints Omega_0^2 from the corrected slow system.
- [ ] #5 The two Omega_0^2 expressions are compared with SymPy simplification/assertions and any disagreement is surfaced as a blocking discrepancy.
- [ ] #6 The final expression is checked structurally against Berton's Eq. 119 expectation: slow microphysical rate times gravity/fall term times supersaturation-gradient structure, with k absent.
<!-- AC:END -->
