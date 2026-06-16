---
id: TASK-017
title: Use W_a0 as full Berton continuation conditioning sanity check
status: In Progress
assignee:
  - '@pi'
created_date: '2026-06-15 19:47'
updated_date: '2026-06-16 11:24'
labels:
  - berton
  - auto
  - continuation
  - W_a0
dependencies:
  - TASK-013
  - TASK-015
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Use W_a0 continuation in the improved full Berton AUTO formulation as a sanity check for branch conditioning and local-equilibrium movement. This task is not primarily Hopf-seeking; it verifies that the reformulated problem can continue a branch for a control known from the Python probe to move the equilibrium smoothly while remaining stable.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Continuation starts from the TASK-011/TASK-012 equilibrium seed in the reformulated AUTO variables.
- [ ] #2 W_a0 continuation covers a documented range comparable to the TASK-012 Python probe where feasible, or explains any reduced range.
- [ ] #3 AUTO outputs show whether the branch moves the equilibrium altitude smoothly beyond the seed and no longer immediately fails at the first step.
- [ ] #4 Stability/eigenvalue diagnostics are reported and compared with the TASK-012 Python W_a0 probe expectation of stable equilibria.
- [ ] #5 The result is used to assess whether remaining H_a3 failures are control-specific or indicate broader formulation/conditioning problems.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Treat the existing TASK-015 log-mass W_a0 result as negative full-4D evidence, not as the final TASK-017 sanity check, because it still accepted only the seed.
2. Use the completed TASK-018 restricted/local 3D scaling diagnostics as the basis for TASK-017, and coordinate any needed implementation with TASK-019 rather than rerunning the failed TASK-015 setup unchanged.
3. Inspect TASK-012/TASK-015 W_a0 probe outputs and TASK-018 scaling recommendation to define the exact W_a0 range, seed translation, residual/state scalings, and stability diagnostics required for this sanity check.
4. If restricted 3D AUTO artifacts already exist, parse and synthesize them; otherwise create/run the minimal restricted W_a0 continuation path needed under episodes/07-restricted-equilibrium-auto without overwriting prior task artifacts.
5. Generate curated TASK-017 outputs documenting accepted W_a0 range or failure, equilibrium altitude/state movement, stability/eigenvalue diagnostics, AUTO commands/constants, and comparison with TASK-012/TASK-015 first-step failures.
6. Write a short companion note that explicitly answers whether W_a0 conditioning succeeds and what that implies for interpreting H_a3 failures as control-specific versus broader formulation/conditioning problems.
7. Add/update regression tests for the TASK-017 artifacts and conclusion language, run the relevant pytest selection, then mark acceptance criteria and final summary via backlog CLI.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
TASK-015 already attempted W_a0 on the log-mass full-4D formulation and still accepted only the seed. Follow-up W_a0 conditioning work should move to the restricted/scaled 3D formulation in TASK-018/TASK-019 rather than simply rerunning the TASK-015 setup.

Started TASK-017: set task In Progress and reassessed the existing plan against completed TASK-015/TASK-018. TASK-015 full-4D log-mass W_a0 remained seed-only, so the useful continuation check should now be based on the restricted/scaled 3D route from TASK-018/TASK-019.
<!-- SECTION:NOTES:END -->
