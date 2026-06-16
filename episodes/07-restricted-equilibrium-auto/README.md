# Episode 07 — Restricted equilibrium AUTO continuation

This episode investigates whether a restricted/local 3D equilibrium formulation is better conditioned than the full 4D ODE-equilibrium AUTO problem used in episode 06.

Motivation: TASK-015 showed that replacing scaled mass with `log(m/kg)` validates the seed transformation but still does not allow `W_a0` continuation beyond the seed. The next step is therefore not a direct `H_a3` retry on the full 4D formulation, but a restricted equilibrium system with `w=0` and unknowns such as scaled altitude, horizontal velocity, and log-mass/radius.

Tasks:

- TASK-018 — diagnose scaling and conditioning for the restricted 3D residual near the TASK-011 seed. Initial result: the unscaled `(z,u,log_m)` residual has condition estimate about `1.8e8`, while centered/scaled states plus row-scaled residuals reduce this to about `7.4`; nearby 10 km humidity/eta kinks remain branch risks.
- TASK-017 — use `W_a0` as a conditioning sanity check for the scaled restricted residual. Result: the TASK-012 Python probe remains smooth/stable across `0.1`–`1.2 m/s`, but this AUTO setup still accepts only the seed and hits DGEBAL/NaN first-step failures; current `H_a3` failures should not be treated as control-specific Hopf evidence.
- TASK-019 — implement the next scaled restricted 3D AUTO continuation refinement and use `W_a0` as the conditioning gate before any Hopf-focused work.
- TASK-020 — retry `H_a3` Hopf-control continuation only after the restricted `W_a0` gate is meaningful.

Suggested organization:

- `scripts/` — Python conditioning diagnostics and AUTO parsers.
- `notebooks/` — notebook-first reproducibility records for AUTO commands and plots.
- `auto/` — AUTO-07p restricted 3D formulations and raw branch/solution/diagnostic files.
- `outputs/` — curated task outputs supporting documented findings.
- `docs/` — companion notes, scaling decisions, and verdicts.
