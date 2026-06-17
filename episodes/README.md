# Episode index

Research artifacts are organized by episode: a coherent phase of the investigation that may span multiple backlog tasks and include docs, scripts, notebooks, AUTO files, and curated outputs.

Reusable source code remains in `src/cloud_rom/`; tests remain in top-level `tests/`.

## 01 — Berton 2023 integration

Path: `episodes/01-berton2023-integration/`

Purpose: extract and implement the Berton (2023) cirrus parcel model, document the implementation, and reproduce the paper's basic steady/oscillatory integrations.

Backlog relationship: pre-AUTO foundation work; supports all later tasks.

## 02 — Reduced-model CAS analysis

Path: `episodes/02-reduced-model-cas/`

Purpose: derive and analyze the reduced 3D Berton fixed-point Jacobian, Routh-Hurwitz/Hopf conditions, sign structure, singular reduction, and mechanism classification.

Backlog tasks: TASK-001 through TASK-006.

## 03 — Reduced-model AUTO analysis

Path: `episodes/03-reduced-model-auto/`

Purpose: validate AUTO-07p continuation and Hopf detection on the reduced 3D model before attempting the full model.

Backlog task: TASK-007.

## 04 — Full-model AUTO equilibria

Path: `episodes/04-full-model-auto-equilibria/`

Purpose: design and validate the full Berton AUTO equilibrium problem, then continue equilibria over the `z_W0` control range to test whether the paper's 10 km to 9 km transition is explained by a Hopf bifurcation.

Backlog tasks: TASK-008 through TASK-010.

Conclusion so far: no LP/HB/BP or Hopf candidate is detected on the selected full-model `z_W0` equilibrium branch; the paper's reported oscillation likely requires a separate periodic-orbit/global-dynamics episode rather than continuation from this equilibrium Hopf premise.

## 05 — Full-model oscillatory-orbit classification

Path: `episodes/05-full-model-oscillatory-orbit/`

Purpose: classify the canonical full Berton Case-0 oscillatory trajectory using long BDF/LSODA integrations after the failed `z_W0` Hopf screen, and export a continuation-ready seed for follow-up AUTO experiments.

Backlog task: TASK-011.

Conclusion: the no-Coriolis canonical Case-0 oscillation is damped/equilibrium-like over 500 h; a stable complex eigenpair at the settled state explains the decaying oscillation, so the exported seed is an equilibrium/state estimate rather than a periodic-orbit seed.

## 06 — Full-model AUTO seed continuation

Path: `episodes/06-full-model-auto-seed-continuation/`

Purpose: initialize full-model equilibrium continuation from the TASK-011 late-time equilibrium seed and probe controls expected to affect local equilibrium conditions (`W_a0` and `H_a3`) rather than repeating the insensitive `z_W0` branch alone.

Backlog tasks: TASK-012, TASK-013, and TASK-015.

Conclusion: AUTO accepts the TASK-011 seed and reproduces the stable complex eigenpair, but TASK-012 first continuation steps in `W_a0` and `H_a3` fail at the minimum step size. TASK-015 replaces scaled mass with `log(m/kg)`, documents the physical-state conversion and derivative policy, and cross-checks the transformed seed residual/eigenvalues; the `W_a0` retry still accepts only the seed and now exposes Newton/NaN/DGEBAL divergence, so robust alternate-control continuation remains unresolved.

## 07 — Restricted equilibrium AUTO continuation

Path: `episodes/07-restricted-equilibrium-auto/`

Purpose: investigate whether a restricted/local 3D equilibrium formulation with `w=0` and unknowns such as scaled altitude, horizontal velocity, and log-mass/radius is better conditioned than the episode-06 full 4D ODE-equilibrium AUTO problem.

Backlog tasks: TASK-017 through TASK-023.

Conclusion: centered/scaled restricted states, row-scaled residuals, and the `P=log(m/m_seed)/10` mass arclength coordinate make the restricted `W_a0` gate useful; TASK-019 follows a meaningful `W_a0` branch and matches the Python probe. Restricted `H_a3` continuation finds a nearby fold/turning limitation but no AUTO-supported Hopf, while smoothed restricted `z_W0` continuation reaches the paper-relevant downward direction and identifies the 9.6--10 km updraft-transition region as the main numerical risk.

## 08 — Full-model AUTO H_a3 retry

Path: `episodes/08-full-model-auto-ha3/`

Purpose: retry full 4D Berton equilibrium continuation in the humidity control `H_a3` using the scaled-state lessons from the restricted continuation work.

Backlog task: TASK-016.

Conclusion: the full-system scaled `H_a3` retry starts at the TASK-011/TASK-012 stable seed but accepts no useful nontrivial branch in either direction. No HB/Hopf label is present; the suspected `H_a3≈0.62` crossing remains a Python/restricted hint only, not full-system AUTO evidence.

## 09 — Full-model AUTO z_W0 continuation

Path: `episodes/09-full-model-auto-zw0/`

Purpose: port the TASK-023 softplus-smoothed updraft transition and scaled full-system variables into a full 4D continuation in `q_z=(z_W0-9000 m)/1000 m`.

Backlog task: TASK-024.

Conclusion: the smoothed full-system `z_W0` attempt accepts only the seed and fails numerically before producing a useful branch across the 7--10 km paper-relevant interval. This remains inconclusive numerically, not AUTO-supported Hopf evidence, and periodic-orbit continuation should wait for a better-conditioned full equilibrium branch or an independently validated periodic seed.

## 10 — Full-model Python continuation

Path: `episodes/10-full-model-python-continuation/`

Purpose: provide the reproducible home for a Python-continuation-first full-model investigation, using the conditioning lessons from episodes 06–09 to explore branches in Python before creating any final AUTO validation case.

Backlog task: TASK-025.

Strategy: Python continuation first; AUTO only for final validation after Python identifies a mature branch segment or bifurcation candidate worth validating.
