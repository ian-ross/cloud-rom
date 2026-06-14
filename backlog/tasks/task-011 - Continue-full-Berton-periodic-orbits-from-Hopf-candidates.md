---
id: TASK-011
title: Continue full Berton periodic orbits from Hopf candidates
status: To Do
assignee: []
created_date: '2026-06-14 12:39'
updated_date: '2026-06-14 13:00'
labels:
  - berton
  - auto
  - periodic-orbits
dependencies:
  - TASK-010
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
If equilibrium continuation finds one or more Hopf candidates, switch branches in AUTO-07p and continue the emerging periodic orbits to characterize amplitude, period, and stability.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 For each detected Hopf candidate, AUTO branch switching is attempted and success/failure is documented.
- [ ] #2 Continued periodic-orbit branches report period, amplitude in key state variables, stability, and parameter range.
- [ ] #3 The small-amplitude period near Hopf is compared against 2*pi/Im(lambda) from the equilibrium eigenvalues.
- [ ] #4 Periodic-orbit periods/amplitudes are compared qualitatively with Berton's reported oscillatory behavior.
- [ ] #5 If no Hopf candidates are found, the task records this as not applicable and documents any alternative instability mechanism indicated by equilibrium continuation.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Review TASK-010 special-point catalog and identify each Hopf candidate suitable for branch switching.
2. Configure AUTO periodic-orbit continuation from each Hopf point, including mesh, period handling, amplitude measures, and stability output.
3. Attempt branch switching for each Hopf candidate and document success/failure with AUTO labels and commands.
4. Continue any successful periodic-orbit branches over the relevant parameter range.
5. Extract period, amplitude in key state variables, stability, and parameter values along each orbit branch.
6. Compare near-Hopf periods with 2*pi/Im(lambda) from the equilibrium eigenvalues and compare larger-amplitude behavior with Berton oscillations.
7. If no Hopf exists or branch switching fails, document why and state what alternative mechanism TASK-010 suggests.
<!-- SECTION:PLAN:END -->
