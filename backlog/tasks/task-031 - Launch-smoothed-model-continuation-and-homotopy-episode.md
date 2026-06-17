---
id: TASK-031
title: Launch smoothed-model continuation and homotopy episode
status: To Do
assignee: []
created_date: '2026-06-17 20:38'
labels:
  - berton
  - continuation
  - smoothing
  - homotopy
  - episode
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a new research episode for a principled smoothed variant of the Berton full model. The episode should add controlled smoothing to kinked atmospheric profiles and regime switches used by the current Python continuation setup, identify suitable steady and oscillatory starting states by numerical integration, analyze continuation branches in the smoothed model, and then homotope smoothing widths back toward the paper-faithful nonsmooth model to distinguish robust dynamics from kink-induced artifacts.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A new episode directory is created with a README explaining the purpose, scope, and relationship to episode 10 and the paper-faithful nonsmooth model
- [ ] #2 The paper-faithful model remains available as a baseline, while a parameterized smoothed-model variant is implemented or wrapped with documented smoothing widths and formulas
- [ ] #3 Relevant kinked atmospheric profiles and regime switches are audited, with an explicit decision about which are smoothed first and why
- [ ] #4 Numerical integration is used to identify reproducible steady and oscillatory candidate starting states for smoothed-model continuation
- [ ] #5 Python continuation is run on at least the primary smoothed-model equilibrium branch, with residuals, eigenvalues, stability counts, and candidate bifurcations recorded
- [ ] #6 If additional branches or oscillatory seeds are found, the episode documents whether they are pursued immediately or deferred
- [ ] #7 A smoothing-width homotopy is performed toward the paper-faithful model, reporting whether key stability features persist, shift, vanish, or collapse onto profile kinks
- [ ] #8 The episode report clearly distinguishes robust smoothed-model dynamics from artifacts of the nonsmooth paper profiles
<!-- AC:END -->
