---
id: TASK-012
title: Continue full Berton dynamics from long-integration seed
status: To Do
assignee: []
created_date: '2026-06-14 12:39'
updated_date: '2026-06-15 14:07'
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
- [ ] #1 The TASK-011 classification verdict and exported seed artifacts are reviewed and recorded as the basis for the continuation setup.
- [ ] #2 If TASK-011 is limit-cycle-like, AUTO periodic-orbit continuation is attempted from the sampled late-time orbit, with mesh/period/amplitude initialization and success or failure documented.
- [ ] #3 If TASK-011 is equilibrium/transient-like, equilibrium continuation is initialized from the late-time state/equilibrium estimate and uses at least one control expected to affect the local equilibrium, not the previously insensitive z_W0 branch alone.
- [ ] #4 Continuation outputs report parameter range, stability or failure diagnostics, periods/amplitudes for periodic orbits, or eigenvalue/special-point diagnostics for equilibrium branches.
- [ ] #5 Seed quality, solver/tolerance sensitivity, AUTO convergence issues, and any evidence for finite-amplitude/global/nonsmooth mechanisms are stated explicitly.
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
