---
id: TASK-029
title: Stage full-model z_W0 continuation through smoothed updraft transition
status: Done
assignee:
  - '@pi'
created_date: '2026-06-17 16:39'
updated_date: '2026-06-17 20:53'
labels:
  - berton
  - continuation
  - python
  - zw0
  - episode-10
dependencies:
  - TASK-027
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Use the Python continuation workflow to study full Berton z_W0 equilibrium branches through the updraft transition region with staged smoothing, instead of relying on immediate full AUTO continuation.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Continuation uses the smoothed updraft formulation from TASK-023/TASK-024 and records smoothing width, z_W0 scaling, and physical inverse mappings
- [x] #2 A staged schedule explores easier smoothing widths before attempting the sharper TASK-023/TASK-024 width
- [x] #3 Accepted branches are checked across the paper-relevant 7–10 km z_W0 interval when numerically reachable, with special attention to the 9.6–10 km transition region
- [x] #4 Results state whether transition-region fragility is branch geometry, smoothing/nonsmoothness, scaling, or unresolved numerical failure
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Review episode-10 Python continuation core and TASK-027/TASK-028 scripts/outputs to reuse the validated full-model seed, scaling, residual/eigenvalue diagnostics, anchor refinement, and output schema.
2. Review TASK-023/TASK-024 smoothed z_W0 artifacts to port the softplus updraft smoothing, 50 m target width, q_z=(z_W0-9000 m)/1000 m scaling, and physical inverse mappings into the Python continuation workflow.
3. Implement a reproducible episode-10 TASK-029 script that runs staged z_W0 pseudo-arclength continuation from easier smoothing widths toward the TASK-023/TASK-024 50 m width, persisting accepted branch points, rejected/corrector histories, smoothing metadata, q_z/z_W0 mappings, residuals, conditioning, and eigenvalue spectra.
4. Evaluate reachability and diagnostics over the paper-relevant 7-10 km interval, with explicit anchors and dense inspection near the 9.6-10 km transition region when the branch is numerically reachable.
5. Write curated TASK-029 outputs and a companion note explaining whether transition-region fragility is best attributed to branch geometry, smoothing/nonsmoothness, scaling, or unresolved numerical failure, without overstating numerically inconclusive results.
6. Add regression tests for staged smoothing metadata, physical mappings, interval/transition-region coverage or documented failure, diagnostic completeness, and conservative verdict language.
7. Run the TASK-029 script/tests plus relevant episode-10 and smoothing-regression tests, then update backlog notes, check satisfied ACs, add final summary, and mark the task done if validation passes.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
- Implemented episodes/10-full-model-python-continuation/scripts/berton_full_task029_zw0_staged_smoothing.py using the TASK-026 scaled/log-mass full-model continuation core with TASK-023/TASK-024 softplus-smoothed updraft.
- Ran staged smoothing widths 300, 150, 100, and 50 m with q_z=(z_W0-9000 m)/1000 m, persisted branch/eigenvalue/corrector/rejection diagnostics under outputs/task029, and documented the physical inverse mapping.
- Results: the 50 m width reaches z_W0≈6999.5--9929.96 m with accepted anchors through 9900 m and 28 accepted points in the 9.6--10 km transition region, but does not reach 10 km; easier 100--300 m widths reach ≈10 km. Verdict classifies transition fragility as smoothing/nonsmoothness sensitive rather than pure q_z scaling.
- Added docs/task029_zw0_staged_smoothing.md, updated the Episode 10 README, and added tests/test_episode10_task029_zw0_staged_smoothing.py.
- Validation: uv run python episodes/10-full-model-python-continuation/scripts/berton_full_task029_zw0_staged_smoothing.py; uv run pytest tests/test_episode10_task026_python_continuation.py tests/test_episode10_task027_wa0_gate.py tests/test_episode10_task028_ha3_branch.py tests/test_episode10_task029_zw0_staged_smoothing.py tests/test_episode07_restricted_task023.py tests/test_episode09_full_task024.py; uv run pytest.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented TASK-029 staged full-model Python z_W0 continuation.

Changes:
- Added a reproducible episode-10 z_W0 pseudo-arclength workflow using TASK-026 full-model scaled/log-mass variables and the TASK-023/TASK-024 softplus-smoothed updraft.
- Explored staged smoothing widths 300, 150, 100, and 50 m before judging the sharper 50 m TASK-023/TASK-024 setting.
- Persisted curated branch points, eigenvalue spectra, residual norms, conditioning diagnostics, corrector histories, rejected steps, smoothing metadata, q_z scaling, and z_W0 physical inverse mappings under outputs/task029.
- Added a companion TASK-029 note and README entry, plus regression tests for smoothing metadata, coverage, transition-region diagnostics, conservative verdict language, and curated outputs.

Result:
- The 50 m branch reaches z_W0≈6999.5--9929.96 m and includes accepted anchors through 9900 m with dense 9.6--10 km transition-region diagnostics, but it does not cleanly reach 10 km.
- Easier smoothing widths reach approximately 10 km, while the 50 m width accumulates corrector failures near z_W0≈9930 m.
- Verdict: transition-region fragility is smoothing/nonsmoothness-sensitive, not primarily q_z scaling; it remains short of a fully clean 7--10 km sharp-width result.

Validation:
- uv run python episodes/10-full-model-python-continuation/scripts/berton_full_task029_zw0_staged_smoothing.py
- uv run pytest tests/test_episode10_task026_python_continuation.py tests/test_episode10_task027_wa0_gate.py tests/test_episode10_task028_ha3_branch.py tests/test_episode10_task029_zw0_staged_smoothing.py tests/test_episode07_restricted_task023.py tests/test_episode09_full_task024.py
- uv run pytest
<!-- SECTION:FINAL_SUMMARY:END -->
