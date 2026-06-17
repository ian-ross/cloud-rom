---
id: TASK-029
title: Stage full-model z_W0 continuation through smoothed updraft transition
status: In Progress
assignee:
  - '@pi'
created_date: '2026-06-17 16:39'
updated_date: '2026-06-17 20:47'
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
- [ ] #1 Continuation uses the smoothed updraft formulation from TASK-023/TASK-024 and records smoothing width, z_W0 scaling, and physical inverse mappings
- [ ] #2 A staged schedule explores easier smoothing widths before attempting the sharper TASK-023/TASK-024 width
- [ ] #3 Accepted branches are checked across the paper-relevant 7–10 km z_W0 interval when numerically reachable, with special attention to the 9.6–10 km transition region
- [ ] #4 Results state whether transition-region fragility is branch geometry, smoothing/nonsmoothness, scaling, or unresolved numerical failure
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
