---
id: TASK-030
title: Validate Python-discovered full-model candidates with AUTO
status: To Do
assignee: []
created_date: '2026-06-17 16:39'
labels:
  - berton
  - continuation
  - auto
  - python
  - episode-10
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Use AUTO only after the Python continuation workflow has produced accepted full-model equilibrium branch points, tangents, and candidate bifurcation locations. This task is for final validation, not exploratory branch discovery.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 AUTO setup is seeded from Python-accepted branch points with documented coordinates, residuals, parameter values, and tangent estimates
- [ ] #2 AUTO validation targets only specific Python-discovered candidates or branch segments, not blind broad continuation from the original seed
- [ ] #3 Any positive Hopf claim requires AUTO HB labeling or equivalent accepted special-point evidence plus independent Python eigenvalue cross-checks
- [ ] #4 A synthesis note compares AUTO validation results against Python continuation evidence and episodes 06–09
<!-- AC:END -->
