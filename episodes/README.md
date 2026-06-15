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
