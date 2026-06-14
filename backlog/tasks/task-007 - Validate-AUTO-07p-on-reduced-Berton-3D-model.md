---
id: TASK-007
title: Validate AUTO-07p on reduced Berton 3D model
status: To Do
assignee: []
created_date: '2026-06-14 12:39'
labels:
  - berton
  - auto
  - continuation
dependencies: []
references:
  - scripts/berton_3d_hopf_task005_classification.py
  - docs/berton_3d_hopf_analysis_summary.md
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create an AUTO-07p continuation problem for the already-audited reduced Berton 3D fixed-point model and verify AUTO reproduces the Python symbolic/root-tracking stability results before porting the full Berton model.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 AUTO problem files for the reduced 3D model are added with clear parameter/state definitions.
- [ ] #2 Equilibrium continuation runs over a drag-rate or mechanism-relevant parameter and detects/records stability consistently with the Python root-tracking scripts.
- [ ] #3 AUTO eigenvalue/Hopf diagnostics are cross-checked against the existing Python corrected cubic at matched parameter values.
- [ ] #4 A short validation note documents commands run, AUTO output files inspected, and any discrepancies.
<!-- AC:END -->
