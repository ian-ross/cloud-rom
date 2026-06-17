---
id: TASK-024
title: Continue full Berton z_W0 with smoothed updraft profile
status: Done
assignee:
  - '@pi'
created_date: '2026-06-17 11:03'
updated_date: '2026-06-17 12:07'
labels:
  - berton
  - auto
  - continuation
  - z_W0
  - full-model
  - smoothing
dependencies:
  - TASK-016
  - TASK-023
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Use the lessons from the restricted z_W0 continuation and the H_a3 scaling work to run a full-system AUTO continuation in the updraft-altitude control z_W0 with a smoothed updraft profile. This is the full-model counterpart to the paper-motivated steady-versus-oscillatory updraft-altitude experiment and should not proceed until the restricted smoothed z_W0 gate is understood.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The full-system AUTO formulation uses a smoothed updraft profile consistent with the restricted z_W0 task, with smoothing parameters and physical interpretation documented.
- [x] #2 The full-model state, mass/arclength, parameter scaling, and continuation constants incorporate lessons from TASK-019, TASK-020, TASK-023, and TASK-016, or explicitly justify any deviations.
- [x] #3 z_W0 continuation starts from the TASK-011/TASK-012 seed and covers a documented range relevant to the paper steady/oscillatory transition.
- [x] #4 AUTO branch outputs are parsed for accepted parameter range, state movement, LP/HB/BP/special labels, stability index/eigenvalue diagnostics, and convergence failures.
- [x] #5 Detected or suspected stability transitions are cross-checked with independent Python finite-difference or analytic Jacobian eigenvalues at representative branch points.
- [x] #6 A companion note states whether full-system z_W0 provides AUTO-supported evidence for a Hopf/oscillatory transition, no crossing, or continued numerical inconclusiveness, without overstating results.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Begin only after TASK-023 restricted smoothed z_W0 and TASK-016 full-system H_a3 have produced scaling/profile recommendations; do not run full-system z_W0 directly from the old kinked profile.
2. Port the TASK-023 smoothed updraft profile into the full Berton AUTO/Python diagnostic formulation, documenting the smoothing formula, width, and relationship to the original paper profile.
3. Incorporate full-system mass/arclength and parameter-control scaling lessons from TASK-019, TASK-020, TASK-023, and TASK-016, including physical inverse conversions and parser support.
4. Define the z_W0 continuation range from the paper steady/oscillatory updraft-altitude experiment and from TASK-023 restricted behavior; include anchors near the canonical seed and expected transition regions.
5. Run bidirectional full-system z_W0 continuation from the TASK-011/TASK-012 seed with documented AUTO constants and preserved raw `b/s/d` outputs under a distinct TASK-024 artifact path.
6. Parse branch outputs for accepted z_W0 range, physical state movement, LP/HB/BP/special labels, stability index/eigenvalues, periodic-orbit-relevant Hopf candidates, and convergence failures.
7. Cross-check representative branch points and any suspected stability transitions with independent Python full-system residuals and finite-difference/analytic Jacobian eigenvalues.
8. Compare the full-system z_W0 results against TASK-023 restricted z_W0, TASK-016 H_a3, TASK-012 Python probes, and the original paper steady/oscillatory motivation.
9. Write a companion verdict note stating whether smoothed full-system z_W0 provides AUTO-supported evidence for a Hopf/oscillatory transition, no crossing, or continued numerical inconclusiveness, and whether periodic-orbit continuation should be attempted next.
10. Add tests for smoothing consistency, coordinate/control scaling, artifact coverage, z_W0 range/anchor coverage, independent eigenvalue checks, and conservative verdict language.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
- Added episode 09 full-system smoothed z_W0 AUTO variant at episodes/09-full-model-auto-zw0/auto/berton_full_task024_zw0_smooth/ using TASK-016 full 4D scaling and TASK-023 softplus updraft smoothing (50 m width).
- Ran bidirectional q_z=(z_W0-9000 m)/1000 m AUTO attempts from the TASK-011/TASK-012 seed. Both directions failed before accepting a useful nontrivial branch; curated outputs document the attempted paper-relevant targets and failure notes.
- Added independent Python smoothed full-Jacobian diagnostics at z_W0 anchors spanning 7--10 km, including the 9.6--10 km ramp-transition region.
- Verdict: continued numerical inconclusiveness; no AUTO-supported full-system Hopf/oscillatory transition and no clean negative result over the desired range.
- Verification: uv run pytest tests/test_episode09_full_task024.py tests/test_episode07_restricted_task023.py tests/test_episode08_full_task016.py (12 passed); uv run pytest tests/test_episode09_full_task024.py after removing transient AUTO build files (4 passed).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented TASK-024 as a new episode 09 full-system smoothed z_W0 AUTO experiment.

Changes:
- Added a full 4D AUTO formulation under episodes/09-full-model-auto-zw0/auto/berton_full_task024_zw0_smooth/ using TASK-016 state scaling (Z, U, W, P=log(m/m_seed)/10) and TASK-023 softplus-smoothed updraft with 50 m smoothing width.
- Configured bidirectional q_z=(z_W0-9000 m)/1000 m continuation attempts from the TASK-011/TASK-012 seed with paper-relevant 7--10 km targets.
- Preserved raw AUTO b/s/d artifacts and added synthesis outputs for branch summaries, convergence notes, config metadata, representative points, and independent Python full-Jacobian eigenvalue checks.
- Added a companion verdict note and regression tests for artifacts, smoothing/scaling/control mapping, range/failure curation, Python diagnostics, and conservative conclusion language.

Result:
- AUTO starts at the canonical seed but does not accept a useful nontrivial full-system z_W0 branch in either direction.
- No HB/Hopf label or AUTO-supported oscillatory transition is present.
- Independent Python eigenvalue anchors across 7--10 km are diagnostic only because those anchors are not accepted AUTO branch points.
- Verdict is continued numerical inconclusiveness, not a clean negative result and not evidence for a full-system Hopf transition.

Tests:
- uv run pytest tests/test_episode09_full_task024.py tests/test_episode07_restricted_task023.py tests/test_episode08_full_task016.py
- uv run pytest tests/test_episode09_full_task024.py
<!-- SECTION:FINAL_SUMMARY:END -->
