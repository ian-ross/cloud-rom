# Notebooks

This directory contains notebooks used to inspect and reproduce parts of Berton (2023), *Two-Dimensional Dynamics of Ice Crystal Parcels in a Cirrus Uncinus*.

## `episodes/01-berton2023-integration/notebooks/atmospheric-profiles.ipynb`

Purpose: reproduce the prescribed atmospheric profiles in paper Figures 1--5.

It uses `cloud_rom.berton2023.Atmosphere` and low-level thermodynamic helpers to plot:

1. **Figure 1** -- horizontal wind profile `U_a(z)` from Appendix A.1 / Eq. (68).
2. **Figure 2** -- updraft profiles `W_a(z)` for steady and oscillatory cases from Appendix A.1 / Eq. (70).
3. **Figure 3** -- ambient temperature `T_a(z)` and dry-air pressure `p_a(z)` from Appendix A.2 / Eqs. (75)--(77).
4. **Figure 4** -- relative humidity and saturation ratios derived from Appendix A.3, Appendix B, and Eqs. (12)--(13).
5. **Figure 5** -- atmospheric infrared ratio `η_a(z)` from Appendix A.4 / Eqs. (80)--(81).

The notebook should be the first stop for checking that the atmospheric forcing encoded in `Atmosphere` matches the paper.

## `episodes/01-berton2023-integration/notebooks/replicate-steady-state.ipynb`

Purpose: run and plot the paper's Case 0 **steady / non-oscillatory** Section 3 solution.

It uses:

- `cloud_rom.berton2023.initial_state_for_case(0)`
- `cloud_rom.berton2023.atmosphere_for_case(0, oscillatory=False)`
- `cloud_rom.berton2023.simulate(...)`
- plotting helpers in `cloud_rom.berton2023_plots`

The notebook generates trajectory, hodograph, time-series, microphysical, drag, and diagnostic panels for comparison with the paper's steady Case 0 figures.

## `episodes/01-berton2023-integration/notebooks/replicate-oscillatory-state.ipynb`

Purpose: run and plot the paper's Case 0 **oscillatory** Section 3 solution.

It uses:

- `cloud_rom.berton2023.initial_state_for_case(0)`
- `cloud_rom.berton2023.atmosphere_for_case(0, oscillatory=True)`
- `cloud_rom.berton2023.simulate(...)`
- plotting helpers in `cloud_rom.berton2023_plots`

The notebook focuses on the low-base updraft case and its damped oscillatory trajectory. It is useful for checking the qualitative trajectory and diagnostic time series against the paper's oscillatory Case 0 figures.

## `episodes/01-berton2023-integration/notebooks/integration-methods.ipynb`

Purpose: compare the saved explicit-Euler reproduction outputs against SciPy ODE integrators.

It uses `cloud_rom.berton2023.simulate_with_method(...)` to run `Radau`, `BDF`, and `LSODA` in two modes:

- fixed `output_dt`, matching the saved Euler CSV cadence for side-by-side comparison;
- native/adaptive output times with `output_dt=None`, demonstrating solver-selected output spacing.

## Generated CSV files

The files below are generated numerical magnitude tables used by the reproduction notebooks:

- `episodes/01-berton2023-integration/outputs/df_steady_magnitudes.csv`
- `episodes/01-berton2023-integration/outputs/df_oscillatory_magnitudes.csv`

They contain unit-converted numeric columns derived from the Pint-valued simulation output. They are convenience artifacts, not primary model source.

## Running notebooks

The project is packaged via `pyproject.toml`, so notebooks should be able to import `cloud_rom` when launched from the project environment, for example:

```bash
uv run jupyter lab
```

or by selecting the project's `uv`/virtualenv Python interpreter in an editor.

If executing notebook cells non-interactively, avoid committing large generated outputs unless they are intentionally part of the documentation.
