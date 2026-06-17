---
id: TASK-028
title: Continue full-model H_a3 branch with Python continuation
status: To Do
assignee: []
created_date: '2026-06-17 16:39'
updated_date: '2026-06-17 16:39'
labels:
  - berton
  - continuation
  - python
  - hopf
  - episode-10
dependencies:
  - TASK-027
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
After the W_a0 gate passes, use Python pseudo-arclength continuation to follow the actual full Berton equilibrium branch in H_a3 through the previously suspected stability-crossing region, rather than evaluating fixed-seed probes.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 H_a3 continuation starts from the TASK-011/TASK-012 equilibrium seed and attempts to cover the suspected H_a3≈0.61–0.65 crossing region
- [ ] #2 Accepted branch points include full residuals, scaled residuals, eigenvalue spectra, stable-eigenvalue counts, and complex-pair tracking
- [ ] #3 Any candidate Hopf crossing is supported by accepted equilibrium branch points on both sides and an independently checked eigenvalue sign change
- [ ] #4 If no crossing is found or continuation fails, the report distinguishes numerical limitation from negative dynamical evidence
<!-- AC:END -->
