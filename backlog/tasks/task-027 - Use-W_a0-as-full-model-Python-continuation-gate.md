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

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect the TASK-026 continuation core, curated outputs, and previous W_a0 probe artifacts from TASK-019 to identify reusable branch-following APIs, diagnostic schema, and comparison ranges.
2. Extend Episode 10 with a TASK-027 reproducibility script/notebook-driven workflow that seeds from the validated full-model equilibrium and follows W_a0 in both directions through the prior comparison range, targeting anchors up to at least W_a0=1.2 m/s when numerically reachable.
3. Persist accepted/rejected branch diagnostics under episodes/10-full-model-python-continuation/outputs/task027/: physical/scaled residual norms, eigenvalues, singular values/condition estimates, corrector histories, anchor reachability, and pass/fail verdict metadata.
4. Compare TASK-027 full-model branch geometry against the previous Python W_a0 probe and restricted TASK-019 behavior, documenting agreements, discrepancies, and likely causes in an Episode 10 doc.
5. Add regression/validation tests for TASK-027 outputs and comparison/verdict invariants, then run the TASK-026/TASK-027 targeted tests and any relevant restricted/full-model tests.
6. Update backlog implementation notes, check ACs that are satisfied, add a PR-style final summary, and mark TASK-027 done only after validation passes.
<!-- SECTION:PLAN:END -->
