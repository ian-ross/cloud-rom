---
id: TASK-032
title: Map full-model sensitivity to updraft smoothing width
status: Done
assignee:
  - '@pi'
created_date: '2026-06-17 21:23'
updated_date: '2026-06-18 11:05'
labels:
  - berton
  - continuation
  - python
  - zw0
  - smoothing
  - episode-10
dependencies:
  - TASK-029
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Extend the Episode 10 Python continuation workflow to treat updraft smoothing width as a scientific continuation/sensitivity parameter, not only a numerical staging aid. Use fixed-z_W0 smoothing continuation and two-parameter-style sampling in (z_W0, smoothing width) to determine whether the transition-region obstruction is branch geometry/fold-like behavior, a singular smoothing/nonsmoothness limit, scaling, or unresolved numerical failure.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Continuation experiments at fixed z_W0 anchors in the 9.6-10 km transition region vary smoothing width from easy values toward and below the TASK-023/TASK-024 50 m width when numerically reachable
- [x] #2 A two-parameter-style sampling or continuation map over z_W0 and smoothing width records accepted equilibria, residuals, conditioning diagnostics, eigenvalue spectra, and rejected-step behavior
- [x] #3 Diagnostics explicitly test for fold/turn or near-singular branch geometry using tangent components, fixed-control state Jacobian singular values, branch Jacobian singular values, or documented equivalent indicators
- [x] #4 Results relate the z_W0 fragility to updraft-profile regularity and distinguish branch geometry, singular smoothing/nonsmoothness limit, scaling, and unresolved numerical failure without overstating inconclusive cases
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Review TASK-029 script/outputs and recap note to identify reusable smoothed-updraft functions, z_W0 scaling, accepted branch anchors, rejected-step patterns, and existing diagnostics for branch/state Jacobian conditioning.
2. Design the smoothing-width continuation coordinate, using a positive transform such as log(width_m/50 m) or an affine width scale, and add physical inverse mappings so widths above, at, and below 50 m are recorded clearly.
3. Implement fixed-z_W0 continuation experiments at transition-region anchors, initially z_W0=9600, 9700, 9800, 9900, and near the TASK-029 obstruction around 9930 m, continuing smoothing width from easy values (e.g. 300/150/100 m) toward 50 m and below when reachable.
4. Implement a two-parameter-style sampling map over (z_W0, smoothing width), seeded from known TASK-029 accepted points where possible, with Newton refinement at grid/anchor points and explicit accepted/rejected classifications.
5. Add fold/turn/near-singular diagnostics for each accepted point: branch tangent components, fixed-control state-Jacobian singular values/condition estimates, branch-Jacobian singular values, residual norms, eigenvalue spectra, stable counts, and correction/rejection metadata.
6. Curate outputs under episodes/10-full-model-python-continuation/outputs/task032/ and write a companion doc explaining whether the obstruction is best interpreted as fold-like branch geometry, a singular smoothing/nonsmoothness limit, scaling, or unresolved numerical failure.
7. Add regression tests for smoothing-width mappings, fixed-anchor coverage, two-parameter map schema, diagnostic completeness, and conservative verdict language; run the TASK-032 script/tests plus relevant TASK-029 and episode-10 tests.
8. After validation, update TASK-032 notes, check satisfied acceptance criteria, write a PR-style final summary, and mark the task done.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
- Implemented episodes/10-full-model-python-continuation/scripts/berton_full_task032_smoothing_width_map.py to treat smoothing width as mu=log(width_m/50 m) with inverse width_m=50*exp(mu), while retaining q_z=(z_W0-9000 m)/1000 m for z_W0.
- Ran fixed-z_W0 smoothing-width continuation at 9600, 9700, 9800, 9900, and 9930 m over widths 300, 200, 150, 100, 75, 50, 35, 25, and 10 m; all fixed-z paths accepted with max scaled residual below tolerance.
- Ran a two-parameter-style (z_W0, width) Newton-refined map over z_W0 anchors 9600, 9700, 9800, 9900, 9930, 9950, and 10000 m and the same width schedule; accepted 61 map points with 2 rejected samples recorded.
- Added fold/near-singular diagnostics: fixed-control state-Jacobian singular values/conditioning, width-branch singular values/tangent components, z_W0-branch singular values/tangent components, eigenvalue spectra, stable counts, residuals, and Newton/rejection logs.
- Result: fixed-z_W0 solves reach the previously obstructed 50 m and sub-50 m region, including z_W0=10000 m, so TASK-029 stopping near 9930 m is not evidence of 50 m equilibrium nonexistence. Conditioning grows sharply as width is reduced below 50 m (max state-Jacobian condition >1e9 at 10 m), supporting a near-singular sharp-profile limit.
- Added docs/task032_smoothing_width_sensitivity.md, outputs/task032 curated CSV/JSON artifacts, README entries, and tests/test_episode10_task032_smoothing_width_map.py.
- Validation: uv run python episodes/10-full-model-python-continuation/scripts/berton_full_task032_smoothing_width_map.py; uv run pytest tests/test_episode10_task029_zw0_staged_smoothing.py tests/test_episode10_task032_smoothing_width_map.py tests/test_episode10_task026_python_continuation.py tests/test_episode10_task027_wa0_gate.py tests/test_episode10_task028_ha3_branch.py; uv run pytest.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented TASK-032 smoothing-width sensitivity mapping in Episode 10.

Changes:
- Added a reproducible smoothing-width sensitivity script using mu=log(width_m/50 m) and the TASK-029 smoothed full-model residual.
- Continued fixed-z_W0 equilibria at transition-region anchors 9600, 9700, 9800, 9900, and 9930 m across widths 300 down to 10 m.
- Added a two-parameter-style (z_W0, smoothing width) map covering z_W0 anchors through 10000 m and widths above, at, and below the TASK-023/TASK-024 50 m setting.
- Persisted accepted points, eigenvalue spectra, Newton iterations, rejected samples, width summaries, state/branch Jacobian singular values, branch tangent components, residuals, stable counts, and a verdict JSON under outputs/task032.
- Added a companion doc and regression tests, and updated the Episode 10 README.

Result:
- Fixed-z_W0 solves reach the previously obstructed region at 50 m and below, including z_W0=10000 m, so the TASK-029 z-continuation stop near 9930 m is not evidence that no 50 m equilibrium exists.
- Conditioning worsens dramatically as smoothing width sharpens below 50 m: the max state-Jacobian condition exceeds 1e9 at 10 m, while 50 m remains much better conditioned.
- Verdict: near_singular_sharp_limit_not_50m_nonexistence. The obstruction is best interpreted as a regularity/path-sensitive and increasingly near-singular sharp-profile limit, not primarily q_z scaling or a clean Hopf/bifurcation discovery.

Validation:
- uv run python episodes/10-full-model-python-continuation/scripts/berton_full_task032_smoothing_width_map.py
- uv run pytest tests/test_episode10_task029_zw0_staged_smoothing.py tests/test_episode10_task032_smoothing_width_map.py tests/test_episode10_task026_python_continuation.py tests/test_episode10_task027_wa0_gate.py tests/test_episode10_task028_ha3_branch.py
- uv run pytest
<!-- SECTION:FINAL_SUMMARY:END -->
