---
id: TASK-020
title: Retry H_a3 Hopf-control continuation on scaled restricted 3D system
status: To Do
assignee: []
created_date: '2026-06-15 20:17'
updated_date: '2026-06-16 20:22'
labels:
  - berton
  - auto
  - hopf
  - continuation
dependencies:
  - TASK-019
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
In episodes/07-restricted-equilibrium-auto/, after the restricted 3D W_a0 sanity check demonstrates acceptable conditioning, retry H_a3 as the Hopf-relevant control on the scaled restricted equilibrium formulation. Treat this as the successor to the direct full-4D H_a3 retry, which should not be trusted until the restricted formulation passes the W_a0 gate.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 H_a3 continuation uses the scaled restricted 3D AUTO formulation validated by the W_a0 sanity check, or explicitly documents why the gate was not met.
- [ ] #2 AUTO branch results are parsed for accepted points, LP/HB/BP labels, eigenvalue diagnostics, and user-defined control anchors over a documented H_a3 range.
- [ ] #3 Python diagnostics independently evaluate residuals and critical eigenvalues along representative accepted points or explain why this is impossible.
- [ ] #4 Results are compared against the TASK-012 Python H_a3 probe and the failed full-4D AUTO attempts.
- [ ] #5 A companion note states whether there is AUTO-supported evidence for a Hopf candidate, no crossing, or continued numerical inconclusiveness.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Read TASK-018, TASK-019, TASK-021, and TASK-022 outputs first; proceed only if TASK-019 validates the `P=M/10` restricted W_a0 gate over the expected W_a0 range.
2. Clone or parameterize the validated TASK-019 restricted AUTO setup for `H_a3`, preserving `Z=(z-z_seed)/100 m`, `U=(u-u_seed)/(1 m/s)`, `P=M/10`, row-scaled residuals, physical inverse conversions, and parser/test conventions.
3. Choose bidirectional H_a3 ranges and UZR anchors from the TASK-012 Python probe, including the canonical value 0.61 and the predicted critical-real-part crossing region.
4. Run AUTO H_a3 continuation with documented constants and preserve raw `b/s/d` outputs under the episode-07 AUTO/output structure; do not use the older un-fixed `M` arclength coordinate for verdicts.
5. Parse accepted branch points, labels, stability index/eigenvalues, physical state movement, `P` and reconstructed `M`, and convergence failures; generate branch and critical-eigenvalue tables/plots where possible.
6. Independently evaluate Python restricted residuals and full physical finite-difference eigenvalues at representative accepted or labeled points.
7. Compare results against the TASK-012 H_a3 Python probe, the failed full-4D TASK-012/TASK-015 attempts, and the restricted W_a0 gate behavior from TASK-019.
8. Write a companion verdict note: AUTO-supported Hopf candidate, no crossing, numerical hint only, or still inconclusive; include residual risks and recommended next step.
9. Add tests that verify H_a3 artifacts, `P<->M` conversion, comparison tables, independent eigenvalue checks or justified absence, and conservative verdict language.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
TASK-022 follow-up found a concrete arclength scaling fix for the restricted W_a0 gate: continue the mass coordinate as `P=M/10` with `M=log(m/m_seed)`, mapping back via `log(m)=log(m_seed)+10P`. TASK-020 should not clone the older TASK-017/TASK-021 `M` coordinate; it should wait for TASK-019 to validate and curate the `P=M/10` W_a0 branch, then reuse that exact coordinate for H_a3.
<!-- SECTION:NOTES:END -->
