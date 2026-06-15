# Episode 05 — Full-model oscillatory-orbit classification

This episode follows the failed full-model `z_W0` equilibrium Hopf screen by directly integrating the canonical Berton Case-0 oscillatory configuration with long adaptive SciPy integrations.

Primary TASK-011 workflow:

- Notebook: `notebooks/task011_case0_long_integration.ipynb`
- Reproducible runner/helper: `scripts/berton_full_task011_classify.py`
- Companion note: `docs/task011_case0_long_integration.md`
- Curated outputs: `outputs/task011/`

Run from the repository root:

```bash
uv run python episodes/05-full-model-oscillatory-orbit/scripts/berton_full_task011_classify.py
```

The workflow uses BDF and LSODA for 500 h after applying the documented extension rule from the required 200 h run. It classifies the canonical no-Coriolis Case-0 oscillation as damped/equilibrium-like and exports an equilibrium continuation seed plus finite-difference eigenvalue diagnostics.
