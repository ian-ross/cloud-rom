---
id: TASK-013
title: Write full Berton AUTO continuation Hopf report
status: To Do
assignee: []
created_date: '2026-06-14 12:39'
updated_date: '2026-06-14 13:00'
labels:
  - berton
  - auto
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
Produce the final report for the full Berton AUTO-07p continuation study, tying continuation evidence back to the reduced 3D analysis and answering whether Berton's transition is locally Hopf-like.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Report summarizes AUTO setup, state/parameter mapping, installation/runtime assumptions, and reproducibility commands.
- [ ] #2 Report includes equilibrium continuation results, detected special points, eigenvalue cross-checks, and mechanism diagnostics.
- [ ] #3 Report includes periodic-orbit continuation results if Hopf candidates were found, or clearly explains why none were continued.
- [ ] #4 Report compares full-model evidence with the reduced 3D prediction based on sigma_S + R_zeta and the corrected determinant/Hopf locus.
- [ ] #5 Report gives a clear final verdict: Hopf, saddle/global/nonsmooth, inconclusive, or parameter-dependent, with evidence and residual risks.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Gather outputs from TASK-007 through TASK-012: AUTO setup notes, design mapping, port validation, equilibrium continuation, periodic-orbit continuation, and robustness probes.
2. Draft the report structure: methods/reproducibility, model/state/parameter mapping, baseline equilibrium continuation, Hopf/periodic-orbit results, robustness probes, comparison to reduced 3D mechanism, and final verdict.
3. Include tables/figures for equilibrium branches, special points, critical eigenvalues, periodic-orbit periods/amplitudes if available, and mechanism diagnostics.
4. Explicitly compare full-model evidence to the reduced criterion based on sigma_S+R_zeta, corrected determinant, and Hopf locus.
5. State limitations and residual risks, including AUTO convergence/scaling issues, profile nonsmoothness, model-port discrepancies, or parameter-dependence.
6. Add tests or lightweight report checks for required sections, formulas, labels, and final verdict language.
7. Run validation/report checks and update the backlog task with final summary and evidence.
<!-- SECTION:PLAN:END -->
