# Berton (2023) model code guide

This guide describes the implementation in `src/cloud_rom/berton2023.py` for humans and coding agents. It is intentionally practical: where to look, what objects mean, and how to extend or inspect the model without breaking equation traceability.

## Design goals

The code is a reference implementation of Berton (2023), not a performance model. Priorities are:

1. preserve paper notation where Python allows (`ρ_a`, `η`, `φ`, `ψ`, `Ω0`);
2. keep Pint units attached to physical quantities;
3. keep equation functions small and traceable to paper equations;
4. expose diagnostics rather than hiding intermediate quantities;
5. use the paper's explicit Euler scheme for reproducibility.

## Core objects

### `ureg`, `Q_`, and `Quantity`

- `ureg` is the module-level Pint `UnitRegistry`.
- `Q_(value, units)` creates quantities from that registry.
- `Quantity` is annotated as `Any` because Pint 0.25.x exposes registry quantities as `PlainQuantity[...]`, which currently produces Pyright false positives against `pint.Quantity` on Python 3.12. Runtime checks still use `isinstance(x, pint.Quantity)` where needed.

### `Constants`

`Constants` stores physical constants from Table 1 and Sect. 2.2.3:

- gravity `g`
- Earth rotation `Ω0`
- gas constants `R_a`, `R_v`
- latent heats `L_s`, `L_v`
- Stefan-Boltzmann constant `σ`
- ice density `ρ_i`
- radiative assumptions (`Q_abs`, `emissivity`)

Default instance: `CONSTANTS`.

### `Atmosphere`

`Atmosphere` stores Appendix A profile parameters and owns all vertical profile methods:

- `horizontal_wind(z)` -- `U_a(z)`, Eq. (68), using corrected Eq. (69) constants.
- `updraft(z)` -- `W_a(z)`, Eq. (70).
- `temperature(z)` -- `T_a(z)`, Eqs. (75)--(76).
- `relative_humidity_profile(z)` -- `H_a(z)`, Eqs. (78)--(79).
- `atmospheric_eta(z)` -- `η_a(z)`, Eqs. (80)--(81).
- `eta(z)` -- crystal-related `η`; returns `η_override` for Cases 1--3 or `atmospheric_eta(z)` for Case 0-style runs.

All profile breakpoints are dataclass attributes, so tests or experiments can override them by constructing a new `Atmosphere`.

### `Crystal`

`Crystal` stores the evolving crystal mass `m` and fixed shape parameters:

- `φ = c/a`, aspect ratio;
- `c_B`, core half-length.

The current dimensions are not stored directly. They are derived from mass using `dimensions_from_mass_constant_phi(...)`, Eq. (35)/(47), which solves the positive cubic root.

### `State`

`State` stores the dynamic parcel state:

- time `t`
- position `x`, `z`
- velocity `u`, `w`
- `crystal`

All fields with dimensions are Pint quantities.

### `SimulationConfig`

`SimulationConfig` controls numerical integration:

- `dt`, `duration`
- latitude `θ`
- `include_coriolis`
- whether to stop when mass becomes non-positive
- Reynolds length convention (`"radius"` by default; `"diameter"` is available because the paper notes both conventions)
- `integration_method`: one of `"euler"` (default, current paper-matching behavior) or any SciPy `solve_ivp` method name (`"RK45"`, `"RK23"`, `"Radau"`, etc.)
- `output_dt`: optional fixed output spacing for diagnostics. If `None` with SciPy methods, output times are chosen adaptively
- `scipy_options`: passthrough dict forwarded to `scipy.integrate.solve_ivp`

### `LocalDiagnostics`

`LocalDiagnostics` is a dataclass holding all quantities evaluated at one state before an Euler update. Construct it with:

```python
diag = LocalDiagnostics.from_state(state, atmosphere, CONSTANTS, config)
```

Important diagnostics include:

- atmospheric: `T_a`, `p_a`, `p_v`, `S_i`, `ρ_a`, `μ_a`, `D_v`, `K_a`, `U_a`, `W_a`;
- geometry: `V`, `a`, `c`, `c_B`, `A`, `D_i`, `r_i`, `C`, `ψ`, `ρ_ie`;
- dynamics: `Re`, `C_D`, `k`, `Sc`, `f_v`;
- microphysics/radiation: `η`, `η_a`, `R`, `driving_factor`, `m_dot`, `T_s_minus_T_a`.

Use `diag.to_dict()` only for tabular output. Within model code prefer attribute access, e.g. `diag.k`, `diag.m_dot`.

## Equation function map

Atmosphere/profile functions:

- `Atmosphere.horizontal_wind` -- Eq. (68)
- `Atmosphere.updraft` -- Eq. (70)
- `Atmosphere.temperature` -- Eqs. (75)--(76)
- `dry_air_pressure` -- Eq. (77)
- `Atmosphere.relative_humidity_profile` -- Eqs. (78)--(79)
- `Atmosphere.atmospheric_eta` -- Eqs. (80)--(81)

Humidity and thermodynamics:

- `saturation_pressure_liquid`, `saturation_pressure_ice` -- Eq. (86)
- `water_vapor_pressure_from_Hl` -- Eqs. (84)--(85)
- `saturation_ratios` -- Eq. (12)
- `relative_humidities` -- Eq. (13)
- `saturation_mixing_ratio` -- Eq. (14)
- `dynamic_viscosity_air` -- Eq. (6)
- `dry_air_density` -- used for `ρ_a` in Eqs. (1), (4), (18)
- `moist_air_density` -- Eq. (7), implemented for reference but not used in the dynamics
- `diffusivity_water_vapor`, `heat_conductivity_air` -- Eq. (15)

Crystal geometry and microphysics:

- `hollow_column_volume_area` -- Eq. (31), with the missing radical restored for the hexagonal cross section
- `volume_from_mass` -- Eq. (36)
- `radius_from_volume_constant_phi` -- Eq. (35)/(47)
- `dimensions_from_mass_constant_phi` -- geometry update for fixed `φ` and `c_B`
- `equivalent_diameter`, `equivalent_radius` -- Eq. (37)/(38)
- `effective_density_max_dimension`, `effective_density_column` -- Eq. (39)/(40)
- `capacitance_hollow_column` -- Eq. (41)
- `reynolds_number` -- Eq. (4)
- `drag_coefficient` -- Eq. (5)
- `damping_coefficient` -- Eq. (3)
- `schmidt_number` -- Eq. (18)
- `ventilation_coefficient` -- Eqs. (16)--(17), using the user-corrected `X = Sc^(1/3) Re^(1/2)`
- `radiative_correction` -- Eq. (19) with Eq. (24)
- `mass_growth_rate` -- Eq. (10)

Dynamics:

- `accelerations` -- Eq. (1a,b), with optional Coriolis terms
- `euler_step` -- explicit-Euler Eqs. (42)--(47) for backward-compatible single-step updates
- `simulate` -- integration driver: explicit Euler (default) or SciPy `solve_ivp` methods via `config.integration_method`
- `simulate_with_method` -- convenience wrapper for one-off method comparisons without manually replacing `SimulationConfig`

## High-level usage

Short Case 0 run:

```python
from cloud_rom import berton2023 as b

state = b.initial_state_for_case(0)
atmosphere = b.atmosphere_for_case(0, oscillatory=True)
config = b.SimulationConfig(duration=b.Q_(10, "minute"), dt=b.Q_(0.04, "s"))

df = b.simulate(state, atmosphere, config=config, sample_every=500)
print(df.iloc[-1]["z"].to("km"))

# Directly compare RK45 output with fixed sample spacing
df_rk45 = b.simulate_with_method(
    "RK45",
    state,
    atmosphere,
    config=b.SimulationConfig(duration=b.Q_(10, "minute"), dt=b.Q_(0.04, "s")),
    output_dt=b.Q_(0.2, "s"),
    progress=False,
)
print(df_rk45.iloc[-1]["z"].to("km"))
```

Convert a Pint-valued column to numeric magnitudes for plotting:

```python
z_km = b.quantity_column_to(df, "z", "km")
```

For more plotting helpers see `src/cloud_rom/berton2023_plots.py`.

## Validation status

Automated tests currently cover:

- atmospheric profile smoke values;
- corrected horizontal wind constants;
- Case 0 geometry against Table 2 values (`m0`, `C0`, `D0`, `ρ_ie0`);
- dimensional checks for `k`, `m_dot`, and accelerations;
- Pint dimensionality error behavior;
- short finite simulation with positive mass.

Run:

```bash
uv run pytest -q
uv run pyright
```

## Known caveats

- The default integration is explicit Euler, so long integrations require small `dt` and can be slow.
- SciPy integrators can be selected via `config.integration_method` for adaptive stepping and usually better stiffness handling.
- Outputs are Pint quantities stored in a pandas DataFrame with object dtype; this is traceable but not fast.
- The paper does not provide machine-readable trajectory data, so full validation is qualitative and table-based rather than exact regression.
- Eq. (7)'s moist-air density is implemented but not used in the coupled dynamics because the governing equations use `ρ_a` and the paper does not appear to use `ρ`/`ρ_m` elsewhere.
- `α` from Eq. (27) is diagnostic only. Numerical cases specify/use `η` directly.
