---
id: TASK-016
title: Retry H_a3 full Berton Hopf-control continuation after AUTO reformulation
status: Done
assignee:
  - '@pi'
created_date: '2026-06-15 19:47'
updated_date: '2026-06-17 11:51'
labels:
  - berton
  - auto
  - hopf
  - H_a3
dependencies:
  - TASK-013
  - TASK-015
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Using the improved full-model AUTO formulation, retry H_a3 as the primary local-stability/Hopf-control candidate suggested by the TASK-012 Python probe. Determine whether AUTO validates a nontrivial equilibrium branch and any Hopf or stability crossing near the canonical Case-0 seed.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Continuation starts from the TASK-011/TASK-012 equilibrium seed in the reformulated AUTO variables.
- [x] #2 H_a3 is varied in both relevant directions over a documented range that includes the canonical value 0.61 and probes the Python-predicted stability-crossing region.
- [x] #3 AUTO branch outputs report accepted parameter range, special points, stability index, eigenvalues, and any convergence failures.
- [x] #4 Detected or suspected Hopf/stability crossings are cross-checked with independent Python finite-difference or analytic Jacobian eigenvalues.
- [x] #5 Results clearly state whether H_a3 provides an AUTO-validated Hopf candidate, only a numerical hint, or a negative/inconclusive result.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Do not begin full-system H_a3 continuation until TASK-020 has produced a restricted H_a3 verdict and scaling recommendation; treat TASK-015 full-4D failures as obsolete negative evidence for the un-fixed scaling.
2. Review TASK-019 (`P=M/10` mass arclength fix), TASK-020 (H_a3-specific control/state scaling), and TASK-023 if available for any smoothed-profile or z_W0 lessons that affect full-model continuation.
3. Update or clone the full Berton AUTO formulation so its mass/arclength coordinate reflects the restricted lessons, with explicit physical inverse conversions and parser support for reconstructed physical mass.
4. Configure H_a3 as the full-system continuation parameter using the scaled-control approach validated in TASK-020, including bidirectional ranges around the TASK-012 predicted crossing near H_a3≈0.62.
5. Run full-system H_a3 continuation from the TASK-011/TASK-012 seed, preserving raw AUTO outputs under a distinct TASK-016 artifact path.
6. Parse branch, solution, and diagnostic files for accepted H_a3 range, state movement, LP/HB/BP/special labels, stability index/eigenvalues, and convergence failures.
7. Cross-check suspected stability transitions with independent Python finite-difference or analytic Jacobian eigenvalues at nearby branch points.
8. Compare the full-system result against TASK-012 Python H_a3 probe, restricted TASK-020 behavior, and previous failed full-4D attempts.
9. Write a companion note with a clear verdict: AUTO-validated Hopf candidate, numerical hint only, negative result, or inconclusive due to remaining convergence problems; explicitly state whether full-system z_W0 (TASK-024) is ready.
10. Add tests covering required artifacts, scaled coordinate/control mapping, H_a3 range coverage or documented failure, eigenvalue cross-checks, and non-overstated verdict language.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
TASK-015 showed the log-mass full-4D reformulation still fails the easier W_a0 sanity check with NaN/DGEBAL divergence. Do not treat a direct H_a3 retry on that formulation as a meaningful validation attempt until restricted-3D scaling work (TASK-018/TASK-019) provides a better-conditioned gate.

Update from TASK-022 follow-up: the restricted W_a0 failure appears fixable by arclength-scaling the mass coordinate as `P=M/10`, while keeping `M=log(m/m_seed)` physical reconstruction. Direct full-4D H_a3 work should remain deferred until TASK-019 validates this fixed restricted W_a0 gate and TASK-020 tests H_a3 in the fixed restricted formulation.

- Started TASK-016 and assigned to @pi. Reviewed dependencies and prerequisite tasks: TASK-013/TASK-015 are done; TASK-019 validated P=M/10; TASK-020 produced the restricted H_a3 verdict (downward branch LP near H_a3≈0.5971, upward Hopf-relevant direction inconclusive near H_a3≈0.611, no AUTO HB); TASK-023 supports staged smoothed z_W0 but does not change H_a3 verdict.
- The existing implementation plan is still applicable: port the TASK-019/TASK-020 scaling lessons into a distinct full-system H_a3 continuation attempt, preserve raw/curated TASK-016 artifacts, cross-check suspected stability with Python eigenvalues, and use conservative verdict language.

- Implemented a new episode 08 full-system TASK-016 variant at `episodes/08-full-model-auto-ha3/auto/berton_full_task016_ha3_scaled/`. The AUTO state starts at the TASK-011/TASK-012 seed and uses `Z=(z-z_seed)/1000`, `U=(u-u_seed)/5`, `W=w`, `P=log(m/m_seed)/10`; active control is `q_H=(H_a3-0.61)/0.001`.
- Ran bidirectional AUTO H_a3 continuations. Upward retries through small q_H steps but fails with NaN/DGEBAL/floating-point diagnostics before accepting point 2; downward records only seed plus MX/no movement. Accepted H_a3 range is therefore only the canonical 0.61.
- Curated outputs under `episodes/08-full-model-auto-ha3/outputs/task016/`, including branch summaries, convergence notes, AUTO eigenvalue diagnostics, config summary, representative points, Python finite-difference full eigenvalue checks, suspected-crossing cross-check anchors, verdict JSON, companion note, and notebook command record.
- Verdict: no AUTO-validated full-system H_a3 Hopf candidate. The TASK-012/TASK-020 H_a3 crossing remains a Python/restricted numerical hint only; full-system z_W0 is not ready on the basis of this H_a3 result.
- Verification: `uv run pytest tests/test_episode08_full_task016.py tests/test_episode07_restricted_task020.py tests/test_episode06_full_logm_reformulation.py` (11 passed), and `uv run pytest tests/test_episode08_full_task016.py` after removing transient AUTO build files (4 passed).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented the TASK-016 full-system scaled H_a3 AUTO retry in a new episode 08.

Changes:
- Added `episodes/08-full-model-auto-ha3/auto/berton_full_task016_ha3_scaled/` with a full 4D scaled equilibrium formulation: `Z=(z-z_seed)/1000`, `U=(u-u_seed)/5`, `W=w`, `P=log(m/m_seed)/10`, and `q_H=(H_a3-0.61)/0.001`.
- Ran bidirectional full-system H_a3 AUTO continuations and preserved raw `b/s/d` artifacts.
- Added a synthesis script, curated outputs, companion verdict note, notebook command record, and regression tests.
- Added independent Python finite-difference full-Jacobian checks for accepted AUTO points and the TASK-012 suspected H_a3 crossing anchors.

Result:
- AUTO starts at the TASK-011/TASK-012 seed, but accepts no nontrivial full-system H_a3 branch in either direction.
- Accepted H_a3 range is only the canonical seed value 0.61; upward fails before reaching the predicted H_a3≈0.62 crossing region, and downward records only seed plus MX/no movement.
- No HB/Hopf label is present. The H_a3 crossing remains a Python/restricted numerical hint only, not full-system AUTO evidence. Full-system z_W0 is not ready based on this H_a3 result.

Tests:
- `uv run pytest tests/test_episode08_full_task016.py tests/test_episode07_restricted_task020.py tests/test_episode06_full_logm_reformulation.py`
- `uv run pytest tests/test_episode08_full_task016.py`
<!-- SECTION:FINAL_SUMMARY:END -->
