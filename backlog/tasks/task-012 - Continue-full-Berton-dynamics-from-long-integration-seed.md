---
id: TASK-012
title: Continue full Berton dynamics from long-integration seed
status: In Progress
assignee:
  - '@iross'
created_date: '2026-06-14 12:39'
updated_date: '2026-06-15 15:41'
labels:
  - berton
  - auto
  - continuation
  - dynamics
dependencies:
  - TASK-011
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Use the classified long-integration result from TASK-011 as the starting object for the next continuation experiment. If TASK-011 identifies a finite-amplitude limit cycle, attempt AUTO periodic-orbit continuation from the exported sampled orbit. If TASK-011 identifies damped convergence to an equilibrium, initialize continuation from the late-time equilibrium/state estimate and probe a control or branch that changes the local equilibrium conditions rather than repeating the insensitive z_W0 steady branch.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The TASK-011 classification verdict and exported seed artifacts are reviewed and recorded as the basis for the continuation setup.
- [x] #2 If TASK-011 is limit-cycle-like, AUTO periodic-orbit continuation is attempted from the sampled late-time orbit, with mesh/period/amplitude initialization and success or failure documented.
- [x] #3 If TASK-011 is equilibrium/transient-like, equilibrium continuation is initialized from the late-time state/equilibrium estimate and uses at least one control expected to affect the local equilibrium, not the previously insensitive z_W0 branch alone.
- [x] #4 Continuation outputs report parameter range, stability or failure diagnostics, periods/amplitudes for periodic orbits, or eigenvalue/special-point diagnostics for equilibrium branches.
- [x] #5 Seed quality, solver/tolerance sensitivity, AUTO convergence issues, and any evidence for finite-amplitude/global/nonsmooth mechanisms are stated explicitly.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Review TASK-011 notebook outputs, classification verdict, and seed files.
2. Choose the continuation path based on the verdict: periodic-orbit continuation for a limit-cycle-like trajectory, or alternate equilibrium continuation for a damped/equilibrium-like trajectory.
3. Translate the TASK-011 seed into the appropriate AUTO initialization format and document scaling, phase/period handling, and state/parameter mapping.
4. Run the selected AUTO continuation experiment and preserve commands, constants, labels, and output files.
5. Extract branch diagnostics: periods, amplitudes, stability, parameter ranges, eigenvalues, special points, and failure modes as applicable.
6. Compare the continuation result with the long-integration classification and note whether it supports a finite-amplitude/global mechanism, an equilibrium-branch explanation, or remains inconclusive.
7. Write a continuation note with reproducibility commands, plots/tables, seed-quality assessment, and residual risks.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
- Reviewed TASK-011 damped/equilibrium-like verdict and copied exported equilibrium seed into TASK-012 outputs.
- Created episode 06 with notebook-first workflow, AUTO setup, docs, curated outputs, and regression tests.
- Initialized AUTO equilibrium continuation from the TASK-011 seed using W_a0 and H_a3 controls; periodic-orbit continuation was not applicable because no limit-cycle seed was exported.
- AUTO accepted the seed and reproduced the stable complex eigenpair, but all first continuation steps ended at minimum-step MX failures; documented convergence diagnostics.
- Added an independent Python equilibrium-control probe showing W_a0 shifts stable equilibrium altitude and H_a3 affects the critical eigenvalue, identifying follow-up scaling/log-mass AUTO work.
<!-- SECTION:NOTES:END -->
