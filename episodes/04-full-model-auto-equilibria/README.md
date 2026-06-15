# Episode 04: Full-model AUTO equilibria

## Research question

Can the Berton Case-0 transition from `z_W0 = 10 km` to `z_W0 = 9 km` be explained by a Hopf bifurcation of an equilibrium in the full four-state Berton AUTO problem?

## Status / conclusion

No Hopf candidate was found on the selected `z_W0` equilibrium branch. The tracked equilibrium remains above the updraft transition and therefore sees saturated `W_a = 0.6 m/s` across the 10 km to 9 km interval. AUTO detects no LP/HB/BP labels, and independent Python finite-difference Jacobians confirm a real positive leading eigenvalue rather than a complex pair crossing the imaginary axis.

## Key artifacts

- `docs/berton_full_auto_task008_design.md` — full-model state/parameter design.
- `auto/berton_full/` — full-model AUTO-07p problem, constants, run script, and curated outputs.
- `scripts/berton_full_auto_task009_validate.py` — RHS/eigenvalue validation for the full Fortran port.
- `docs/berton_full_auto_task009_validation.md` — validation note.
- `scripts/berton_full_auto_task010_analyze.py` — branch parser, special-point catalogue, Python eigenvalue cross-check, and plot/table generator.
- `notebooks/berton_full_auto_task010_continuation.ipynb` — notebook-driven continuation workflow.
- `outputs/task010/` — curated continuation summary tables and plot.
- `docs/berton_full_auto_task010_continuation.md` — continuation note and conclusion.

## Reproducibility

```bash
bash episodes/04-full-model-auto-equilibria/auto/berton_full/run_auto.sh
uv run python episodes/04-full-model-auto-equilibria/scripts/berton_full_auto_task009_validate.py
uv run python episodes/04-full-model-auto-equilibria/scripts/berton_full_auto_task010_analyze.py
uv run pytest tests/test_episode04_full_auto_validate.py tests/test_episode04_full_auto_continuation.py
```

## Relationship to backlog tasks

Backlog tasks: TASK-008, TASK-009, TASK-010.

## Next questions

TASK-011 and TASK-012 were premised on a Hopf candidate from this equilibrium branch. The next scientifically relevant episode should instead reproduce and continue the reported full-model oscillatory orbit directly from time integration, looking for finite-amplitude periodic-orbit or global-dynamics explanations independent of an equilibrium Hopf initialization.
