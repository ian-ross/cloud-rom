---
id: TASK-013
title: Write full Berton dynamics continuation report
status: In Progress
assignee:
  - '@pi'
created_date: '2026-06-14 12:39'
updated_date: '2026-06-15 17:08'
labels:
  - berton
  - auto
  - integration
  - report
dependencies:
  - TASK-011
  - TASK-012
references:
  - docs/berton_3d_hopf_analysis_summary.md
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Produce the final report for the full Berton dynamics investigation after the negative z_W0 equilibrium Hopf screen. Synthesize the equilibrium continuation evidence, long-time BDF/LSODA trajectory classification, and continuation experiments seeded from the observed solution to assess whether Berton's reported oscillatory case is best explained by local Hopf, a finite-amplitude periodic orbit/global mechanism, damped transient approach to an equilibrium, a different branch/control, or an inconclusive parameter-dependent scenario.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Report summarizes the full-model AUTO setup, state/parameter mapping, time-integration configuration, installation/runtime assumptions, and reproducibility commands.
- [ ] #2 Report includes the z_W0 equilibrium continuation negative result, special-point/eigenvalue cross-checks, and why the original Hopf-candidate path was abandoned.
- [ ] #3 Report includes TASK-011 long-integration results: BDF/LSODA settings, envelope/period/solver-agreement diagnostics, plots, classification verdict, seed artifacts, and residual numerical risks.
- [ ] #4 Report includes TASK-012 continuation results from the long-integration seed, including periodic-orbit or alternate-equilibrium branch diagnostics and failure modes as applicable.
- [ ] #5 Report compares full-model evidence with the reduced 3D prediction based on sigma_S + R_zeta and the corrected determinant/Hopf locus without overstating Hopf evidence.
- [ ] #6 Report gives a clear final verdict among local Hopf, finite-amplitude/global/nonsmooth mechanism, damped transient/equilibrium approach, different branch/control, inconclusive, or parameter-dependent, with evidence and residual risks.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Gather outputs from TASK-007 through TASK-012, including full-model port validation, z_W0 equilibrium continuation, long-integration classification, and continuation from the integration seed.
2. Draft the report structure around the updated evidence chain: methods/reproducibility, negative equilibrium Hopf screen, long-time trajectory classification, continuation from the observed-solution seed, comparison to reduced 3D diagnostics, and final verdict.
3. Include tables/figures for equilibrium branches, critical eigenvalues, long-integration envelopes/periods/solver agreement, continuation branches, and mechanism diagnostics.
4. Explicitly explain why the original Hopf-candidate plan changed after TASK-010 and how TASK-011/TASK-012 address the observed oscillatory trajectory directly.
5. State limitations and residual risks, including solver tolerances, long-horizon integration reliability, AUTO initialization/scaling issues, profile nonsmoothness, model-port discrepancies, and parameter dependence.
6. Add lightweight report checks for required sections, commands, generated artifacts, and final verdict language if useful.
7. Run validation/report checks and update the backlog task with final summary and evidence.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Started TASK-013: reviewed TASK-010, TASK-011, and TASK-012 summaries. Current evidence chain is: z_W0 equilibrium continuation is insensitive/no Hopf; long BDF/LSODA integration classifies the reported oscillation as damped/equilibrium-like; AUTO from the long-integration seed accepts only the seed and fails first continuation steps for W_a0/H_a3, while the Python probe suggests H_a3/log-mass reformulation as the strongest follow-up.
<!-- SECTION:NOTES:END -->
