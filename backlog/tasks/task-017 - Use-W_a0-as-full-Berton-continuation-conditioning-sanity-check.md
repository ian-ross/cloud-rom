---
id: TASK-017
title: Use W_a0 as full Berton continuation conditioning sanity check
status: In Progress
assignee:
  - '@pi'
created_date: '2026-06-15 19:47'
updated_date: '2026-06-16 11:23'
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
1. Wait for TASK-015 to provide the improved/reformulated AUTO setup and confirm the seed translation/eigenvalue cross-check passes.
2. Configure W_a0 as the continuation parameter in the reformulated AUTO problem, using the TASK-011/TASK-012 equilibrium seed at W_a0=0.6 m/s.
3. Choose bidirectional W_a0 ranges guided by the TASK-012 Python probe, aiming toward 0.1-1.2 m/s where feasible, with UZR anchors and conservative step controls.
4. Run AUTO continuation in both W_a0 directions and preserve raw branch/solution/diagnostic files under a distinct episode-06 output path.
5. Parse accepted branch points to report W_a0 range, equilibrium altitude/state movement, stability index, eigenvalues, and any LP/HB/BP/special labels or convergence failures.
6. Compare AUTO branch trends against the TASK-012 Python W_a0 probe, especially smooth altitude shift and stable critical real parts.
7. Use the result as a conditioning diagnostic: distinguish successful formulation behavior from broader first-step failures, and state what it implies for interpreting H_a3 continuation outcomes.
8. Write a short companion note with commands, constants, branch plots/tables, comparison to TASK-012, and residual risks.
9. Add tests verifying required outputs, nontrivial W_a0 movement or documented failure, stability diagnostics, and the explicit conditioning-sanity-check conclusion.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
TASK-015 already attempted W_a0 on the log-mass full-4D formulation and still accepted only the seed. Follow-up W_a0 conditioning work should move to the restricted/scaled 3D formulation in TASK-018/TASK-019 rather than simply rerunning the TASK-015 setup.
<!-- SECTION:NOTES:END -->
