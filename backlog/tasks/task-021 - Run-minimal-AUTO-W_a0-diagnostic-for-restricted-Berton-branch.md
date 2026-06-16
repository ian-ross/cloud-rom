---
id: TASK-021
title: Run minimal AUTO W_a0 diagnostic for restricted Berton branch
status: To Do
assignee: []
created_date: '2026-06-16 13:23'
labels:
  - berton
  - auto
  - continuation
  - diagnostics
dependencies:
  - TASK-017
  - TASK-018
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Run the fastest diagnostic for the restricted/scaled Berton W_a0 continuation failure: strip the AUTO setup to the smallest possible equilibrium continuation problem and test whether AUTO can follow the known-smooth W_a0 branch when diagnostic parameters, user functions, and supplied Jacobians are removed. This should distinguish a physical/model branch issue from AUTO metadata/Jacobian/PVLS bookkeeping problems.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A minimal restricted/scaled AUTO config is added without overwriting TASK-017 artifacts, using only W_a0 as ICP and no diagnostic/PVLS parameters in the continuation parameter list.
- [ ] #2 The minimal run disables special-point/eigenvalue detection where practical and runs with AUTO finite-difference Jacobians first, e.g. ISP=0 and JAC=0 or documented equivalents.
- [ ] #3 The run is executed in at least one W_a0 direction from the TASK-011/TASK-012 seed and records whether any nontrivial branch points are accepted beyond W_a0=0.6.
- [ ] #4 Results are compared against TASK-017 restricted/scaled failure and the TASK-012 Python W_a0 probe expectation of smooth stable movement.
- [ ] #5 A short note states whether the failure is likely due to AUTO metadata/Jacobian/PVLS bookkeeping or persists even in the stripped configuration, with raw AUTO diagnostics and commands recorded.
<!-- AC:END -->
