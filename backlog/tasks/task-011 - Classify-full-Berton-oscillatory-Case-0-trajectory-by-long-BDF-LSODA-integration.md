---
id: TASK-011
title: >-
  Classify full Berton oscillatory Case-0 trajectory by long BDF/LSODA
  integration
status: Done
assignee:
  - '@pi'
created_date: '2026-06-14 12:39'
updated_date: '2026-06-15 14:25'
labels:
  - berton
  - integration
  - dynamics
  - notebook
dependencies:
  - TASK-010
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a new episode for the full Berton oscillatory-orbit investigation. Use notebook-driven long integrations of the canonical oscillatory Case-0 configuration after the failed z_W0 equilibrium Hopf screen to determine whether the reported oscillation is a finite-amplitude limit cycle or a damped transient/approach toward an equilibrium. Export the resulting trajectory or equilibrium estimate as a continuation-ready seed for follow-up AUTO experiments.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A new episode directory, e.g. episodes/05-full-model-oscillatory-orbit/, contains the notebook-first workflow and supporting outputs for the investigation.
- [x] #2 The canonical oscillatory Case-0 configuration is integrated with both BDF and LSODA for at least 200 h, with no explicit-Euler long integration used for classification.
- [x] #3 If late-time amplitude or period drift remains ambiguous, the workflow documents and performs an extension rule toward 500-1000 h or explains why extension was unnecessary.
- [x] #4 Late-time envelope, peak/trough, period, solver-agreement, and visual Matplotlib diagnostics classify the trajectory as limit-cycle-like, damped/equilibrium-like, or inconclusive.
- [x] #5 If the trajectory appears to settle, the notebook estimates the late-time equilibrium, RHS norm, and finite-difference eigenvalues, including whether complex eigenvalues explain the observed oscillations.
- [x] #6 Continuation seed artifacts are exported: one late-time sampled period for a limit-cycle classification, or a late-time equilibrium/state estimate plus eigenvalue diagnostics for an equilibrium/transient classification.
- [x] #7 A short companion note summarizes commands, solver settings/tolerances, generated files, plots, classification verdict, and residual risks.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Create episodes/05-full-model-oscillatory-orbit/ with README, notebooks/, outputs/task011/, and any lightweight helper/test locations needed for reproducibility.
2. Build a notebook-first workflow for canonical Berton Case 0 oscillatory settings: oscillatory=True, z_W0=9 km, W_a0=0.6 m/s, H_a3=0.61, eta override None, include_coriolis=False, and initial_state_for_case(0).
3. Run long integrations with SciPy BDF and LSODA for at least 200 h using documented tolerances and sampled diagnostic output; do not use explicit Euler for long-run classification.
4. Compute late-time envelope, extrema, period, mean/final state, RHS norm, solver-agreement, and optional extension diagnostics when drift remains ambiguous.
5. Generate Matplotlib plots and machine-readable summary tables under outputs/task011/.
6. If limit-cycle-like, export one late-time sampled period suitable for AUTO periodic-orbit seeding; if damped/equilibrium-like, export the late-time state/equilibrium estimate and finite-difference eigenvalue diagnostics.
7. Write a companion note documenting commands, files, classification verdict, and residual risks.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
- Created episodes/05-full-model-oscillatory-orbit/ with README, notebook, script, companion note, and curated TASK-011 outputs.
- Ran canonical no-Coriolis Case-0 BDF and LSODA integrations to 500 h after 200 h envelope remained nonzero.
- Classified trajectory as damped/equilibrium-like; exported equilibrium continuation seed and finite-difference eigenvalue diagnostics.
- Added pytest coverage for episode artifacts and classification diagnostics; full test suite passes.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented TASK-011 as a new episode for full-model oscillatory-orbit classification.

Changes:
- Added episodes/05-full-model-oscillatory-orbit/ with a notebook-first workflow, reproducible classification script, README, companion note, plots, CSV diagnostics, and continuation seed artifacts.
- Ran canonical Case-0 no-Coriolis BDF and LSODA integrations to 500 h after applying the documented extension rule from the required 200 h horizon.
- Classified the trajectory as damped/equilibrium-like: the 450-500 h envelope collapses to ~0.009 m versus ~19.2 m at 150-200 h, with close BDF/LSODA agreement.
- Exported a refined equilibrium/state seed plus finite-difference eigenvalues; the stable complex pair has ~10.19 h period and ~39.34 h e-folding time, explaining the decaying oscillation.
- Added tests covering episode artifacts, integration horizons, solver classification outputs, and equilibrium/eigenvalue diagnostics.

Validation:
- uv run python episodes/05-full-model-oscillatory-orbit/scripts/berton_full_task011_classify.py
- uv run pytest tests/test_episode05_full_oscillatory_orbit.py
- uv run pytest
<!-- SECTION:FINAL_SUMMARY:END -->
