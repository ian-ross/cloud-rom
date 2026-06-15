# Episode 03: Reduced-model AUTO analysis

## Research question

Can AUTO-07p reproduce the reduced Berton 3D equilibrium continuation and Hopf/stability diagnostics predicted by the corrected reduced-model analysis?

## Status / conclusion

The reduced AUTO problem validates the AUTO environment and branch parsing/eigenvalue workflow before moving to the full Berton problem. Results are documented in `docs/berton_3d_auto_task007_validation.md`.

## Key artifacts

- `auto/berton_reduced_3d/` — AUTO-07p problem, constants, run script, and curated `b./s./d.` outputs.
- `scripts/berton_3d_auto_task007_validate.py` — parser and Python cross-checks against Episode 02 formulas.
- `notebooks/berton_3d_auto_task007_validation.ipynb` — notebook-driven validation workflow.
- `docs/berton_3d_auto_task007_validation.md` — validation note.

## Reproducibility

```bash
bash episodes/03-reduced-model-auto/auto/berton_reduced_3d/run_auto.sh
uv run python episodes/03-reduced-model-auto/scripts/berton_3d_auto_task007_validate.py
uv run pytest tests/test_episode03_reduced_auto_validate.py
```

## Relationship to backlog tasks

Backlog task: TASK-007.

## Next questions

Episode 03 establishes the AUTO workflow used for the full Berton equilibrium problem in Episode 04.
