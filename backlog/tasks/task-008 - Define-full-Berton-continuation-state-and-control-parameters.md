---
id: TASK-008
title: Define full Berton continuation state and control parameters
status: To Do
assignee: []
created_date: '2026-06-14 12:39'
labels:
  - berton
  - auto
  - design
dependencies:
  - TASK-007
references:
  - src/cloud_rom/berton2023.py
  - docs/berton_3d_hopf_analysis_summary.md
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Specify the full Berton 2023 ODE state vector, AUTO parameter vector, equilibrium equations, and primary continuation controls to use for Hopf analysis.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The report identifies the full-model state variables and maps them to AUTO's U vector.
- [ ] #2 The report identifies candidate continuation parameters, including updraft-base altitude, updraft amplitude, radiation-strength multiplier, and humidity/profile controls.
- [ ] #3 The report chooses an initial primary control parameter and justifies it relative to Berton's 10 km to 9 km transition.
- [ ] #4 The report lists auxiliary diagnostics to output during continuation, including sigma_S, R_zeta, sigma_S + R_zeta, radiative correction, fall-speed slope, and reduced determinant proxy where applicable.
<!-- AC:END -->
