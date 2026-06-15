# Episode 01: Berton 2023 integration

## Research question

Can we extract, implement, and reproduce the Berton (2023) cirrus parcel model in a reusable Python reference implementation?

## Status / conclusion

The core model lives in `src/cloud_rom/berton2023.py` with plotting helpers in `src/cloud_rom/berton2023_plots.py`. This episode contains the extraction notes, implementation guide, notebooks, example run, and curated magnitude exports used to validate and explain that implementation.

## Key artifacts

- `docs/MODEL_EXTRACTION.md` — extraction and implementation record.
- `docs/berton2023-model-code.md` — guide to the Python implementation.
- `docs/notebooks.md` — notebook inventory.
- `notebooks/atmospheric-profiles.ipynb` — atmospheric profile reproduction.
- `notebooks/replicate-steady-state.ipynb` — steady/non-oscillatory Case 0 workflow.
- `notebooks/replicate-oscillatory-state.ipynb` — reported oscillatory Case 0 workflow.
- `notebooks/integration-methods.ipynb` — integration-method notes.
- `examples/berton2023_case0.py` — minimal executable case.
- `outputs/df_steady_magnitudes.csv`, `outputs/df_oscillatory_magnitudes.csv` — curated notebook exports.

## Reproducibility

```bash
uv run pytest tests/test_berton2023.py
uv run python episodes/01-berton2023-integration/examples/berton2023_case0.py
```

## Relationship to backlog tasks

This episode predates the later AUTO-focused backlog tasks and provides the implementation used by TASK-001 onward.

## Next questions

The reported oscillatory integration should be revisited in a later episode now that the full equilibrium Hopf search did not explain it.
