---
id: TASK-008
title: Define full Berton continuation state and control parameters
status: To Do
assignee: []
created_date: '2026-06-14 12:39'
updated_date: '2026-06-14 13:00'
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

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Read src/cloud_rom/berton2023.py and identify the actual dynamical variables used by the full Berton implementation versus diagnostic/algebraic quantities.
2. Decide the AUTO state vector U and document units, variable ordering, scaling, and any algebraic quantities that should remain parameters or auxiliary outputs.
3. Inventory candidate continuation controls: updraft-base altitude, updraft amplitude, radiation-strength multiplier, humidity/profile controls, drag/fall-speed multiplier, and habit/geometry proxies.
4. Choose the initial primary control parameter, prioritizing the Berton 10 km to 9 km transition, and specify the intended continuation interval and direction.
5. Define the AUTO PAR vector, including physical constants, profile controls, and continuation/free parameters.
6. Define auxiliary diagnostics for PVLS/output: sigma_S, R_zeta, sigma_S+R_zeta, radiative correction, fall-speed slope, reduced determinant proxy, and critical physical state values.
7. Write the design document and include enough detail for TASK-009 to implement the AUTO problem without rediscovering the mapping.
<!-- SECTION:PLAN:END -->
