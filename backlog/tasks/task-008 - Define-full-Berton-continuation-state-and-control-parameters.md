---
id: TASK-008
title: Define full Berton continuation state and control parameters
status: Done
assignee:
  - '@pi'
created_date: '2026-06-14 12:39'
updated_date: '2026-06-14 17:00'
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
- [x] #1 The report identifies the full-model state variables and maps them to AUTO's U vector.
- [x] #2 The report identifies candidate continuation parameters, including updraft-base altitude, updraft amplitude, radiation-strength multiplier, and humidity/profile controls.
- [x] #3 The report chooses an initial primary control parameter and justifies it relative to Berton's 10 km to 9 km transition.
- [x] #4 The report lists auxiliary diagnostics to output during continuation, including sigma_S, R_zeta, sigma_S + R_zeta, radiative correction, fall-speed slope, and reduced determinant proxy where applicable.
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

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
- Added docs/berton_full_auto_task008_design.md specifying the four-state full Berton AUTO mapping U=(z,u,w,m), omission of cyclic x, equilibrium residuals, PAR vector, physical continuation controls, z_W0 primary-control choice, and PVLS diagnostics.
- Validation/readback: rg confirmed the report includes U vector mapping, z_W0 primary continuation, candidate controls, sigma_S/R_zeta diagnostics, and reduced determinant proxy.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Defined the full Berton AUTO continuation design for TASK-009.

Changes:
- Added docs/berton_full_auto_task008_design.md with the full-model state vector U=(z,u,w,m), rationale for omitting cyclic x, equilibrium equations, scaling guidance, and mass/growth balance notes.
- Specified a stable AUTO PAR layout covering z_W0, W_a0, radiation multiplier, humidity/profile controls, eta controls, drag/habit controls, and fixed Berton constants/profile breakpoints.
- Selected z_W0 as the initial primary continuation parameter, continuing from the 10 km high-base steady case toward the 9 km oscillatory case.
- Listed PVLS diagnostics including sigma_S, R_zeta, sigma_S+R_zeta, radiative correction, fall-speed slope proxy, reduced determinant proxy, and physical branch diagnostics.

Validation:
- Read src/cloud_rom/berton2023.py, docs/berton2023-model-code.md, docs/berton_3d_hopf_analysis_summary.md, and docs/berton_3d_auto_task007_validation.md.
- Ran rg readback checks against docs/berton_full_auto_task008_design.md for required mappings, controls, primary parameter, and diagnostics.
<!-- SECTION:FINAL_SUMMARY:END -->
