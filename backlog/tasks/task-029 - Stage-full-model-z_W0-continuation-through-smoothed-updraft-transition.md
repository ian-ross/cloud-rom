---
id: TASK-029
title: Stage full-model z_W0 continuation through smoothed updraft transition
status: In Progress
assignee:
  - '@pi'
created_date: '2026-06-17 16:39'
updated_date: '2026-06-17 20:45'
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
