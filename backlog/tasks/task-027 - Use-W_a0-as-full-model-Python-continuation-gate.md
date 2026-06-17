---
id: TASK-027
title: Use W_a0 as full-model Python continuation gate
status: In Progress
assignee:
  - '@pi'
created_date: '2026-06-17 16:39'
updated_date: '2026-06-17 16:57'
labels:
  - berton
  - continuation
  - python
  - episode-10
dependencies:
  - TASK-026
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Apply the episode-10 Python continuation core to the full Berton equilibrium branch in W_a0 before any Hopf-focused controls. This is the conditioning/control sanity gate replacing repeated AUTO-first attempts.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Full-model Python continuation follows W_a0 through the comparison range used by previous Python probes, including anchors up to at least W_a0=1.2 m/s when numerically reachable
- [ ] #2 Accepted branch points have documented full-RHS residual norms, scaled residual norms, eigenvalues, and conditioning diagnostics
- [ ] #3 Branch geometry is compared against previous W_a0 Python probe and restricted TASK-019 behavior, with discrepancies documented
- [ ] #4 A clear pass/fail verdict states whether the full-model continuation core is ready for H_a3 and z_W0 studies
<!-- AC:END -->
