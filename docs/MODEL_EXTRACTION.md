# Model extraction specification: Berton (2023) 2D ice-crystal cirrus model

## 1. Paper/source citation

- **Paper:** Roland P. H. Berton, *Two-Dimensional Dynamics of Ice Crystal Parcels in a Cirrus Uncinus*, Tellus A: Dynamic Meteorology and Oceanography, 2023, DOI: `10.16993/tellusa.3227`.
- **Source file:** `../../papers/berton-2023-2d-ice-crystal-cirrus-model.pdf`.
- **Extraction notes:** `pandoc` is installed, but cannot read PDF input (`Unknown input format pdf`). Text was therefore extracted with `pdftotext` into:
  - `docs/berton-2023-pdftotext.txt` (`-layout`, best for equations/tables)
  - `docs/berton-2023-raw.txt` (`-raw`, fallback for prose)

The PDF text extraction preserves most equations but loses some table-like constants, especially Eq. (69), the horizontal-wind profile constants.

## 2. Implementation goal

Implement a readable Python/Pint reference implementation of the coupled 2D Lagrangian parcel model in `src/cloud_rom/berton2023.py`:

- kinematics of a representative hollow-column ice crystal parcel in a vertical `(x,z)` plane;
- microphysical mass evolution by vapor deposition/sublimation with capacitance, ventilation, and radiative-transfer correction;
- paper atmospheric profiles for wind, updraft, temperature, pressure, humidity, and infrared ratio;
- explicit-Euler time integration matching Sect. 3.1, Eqs. (42)--(47).

Intended API:

- low-level functions for each paper equation/profile;
- dataclasses for physical constants, crystal shape state, atmospheric profile parameters, and integration state;
- one high-level `simulate(...)` function returning a `pandas.DataFrame` with unit-bearing metadata or Pint quantities converted to documented columns.

## 3. Domain of validity and assumptions

Paper-stated assumptions:

- 2D parcel motion in vertical plane `(O,x,z)`, `z` upward.
- Flat Earth approximation; Coriolis is included in Eq. (1) but later treated as negligible for the local non-oscillatory case.
- Representative average ice crystal, not a full particle-size distribution.
- Crystal growth after nucleation by deposition; crystal loss by sublimation.
- Ambient saturation is not depleted by crystal growth because the trajectory does not revisit the same air region.
- Kelvin curvature effect neglected.
- Ice density fixed at `ρ_i = 920 kg m^-3`.
- Hollow hexagonal column habit; in the main numerical model `φ = c/a` and `c_B` are kept constant.
- Crystal emissivity `ε_r = 1`; infrared absorption efficiency `Q_abs ≈ 1`.
- Explicit Euler scheme with small timestep (`0.02--0.04 s` in paper cases).

Implementation assumptions to make explicit:

- Use SI internally with `pint`; altitude inputs may be passed in km or m and are converted to meters.
- Coriolis terms are implemented and controlled by `SimulationConfig(include_coriolis=..., θ=...)`; the default configuration includes them, while reproduction notebooks can disable them for closer comparison with the paper's local-scale numerical discussion.
- Eq. (7) is printed as moist-air density but appears to use `pvsl`; implementation should expose both `ρ_m` as printed and dry-air density `ρ_a = p_a/(R_a T_a)` where equations specifically call for `ρ_a`.
- Drag/Reynolds convention ambiguity near Eq. (41): use equivalent radius `r_i = D_i/2` in Eq. (3) and Eq. (19); use `r_i` in Eq. (4) as printed, with an option to use `D_i` as the paper notes.
- For Eq. (35), solve the cubic for the positive real crystal radius `a`.

## 4. Symbol table

| Paper symbol | Python identifier | Units | Meaning | Source |
|---|---:|---|---|---|
| `x, z` | `x, z` | m | crystal coordinates | Sect. 2.1, Eq. (1) |
| `u, w` | `u, w` | m s^-1 | crystal velocity components | Sect. 2.1 |
| `U_a, W_a` | `U_a, W_a` | m s^-1 | ambient horizontal wind, updraft | App. A.1 |
| `k` | `k` | s^-1 | damping coefficient | Eq. (3) |
| `Re` | `Re` | dimensionless | Reynolds number | Eq. (4) |
| `C_D` | `C_D` | dimensionless | drag coefficient | Eq. (5) |
| `μ_a` | `μ_a` | Pa s | dynamic viscosity of air | Eq. (6) |
| `ρ_a` | `ρ_a` | kg m^-3 | dry-air density | Eq. (1), Eq. (4) |
| `ρ_m` / `ρ` | `ρ_m` | kg m^-3 | moist-air density | Eq. (7) |
| `ρ_i` | `ρ_i` | kg m^-3 | solid ice density | Table 1, Sect. 2.2.3 |
| `m` | `m` | kg | crystal mass | Eq. (10) |
| `C` | `C` | m | capacitance | Eq. (41) |
| `f_v` | `f_v` | dimensionless | ventilation coefficient | Eq. (16) |
| `S_l, S_i` | `S_l, S_i` | dimensionless | saturation ratios over water/ice | Eq. (12) |
| `H_l, H_i` | `H_l, H_i` | dimensionless | relative humidities wrt water/ice | Eq. (13) |
| `p, p_a, p_v` | `p, p_a, p_v` | Pa | total, dry-air, vapor pressures | App. B |
| `p_vsl, p_vsi` | `p_vsl, p_vsi` | Pa | saturation vapor pressures over water/ice | App. C |
| `q_s` | `q_s` | kg kg^-1 | saturation mixing ratio | Eq. (14) |
| `D_v` | `D_v` | m^2 s^-1 | diffusivity of water vapor in air | Eq. (15) |
| `K_a` | `K_a` | W m^-1 K^-1 | heat conductivity of air | Eq. (15) |
| `Sc` | `Sc` | dimensionless | Schmidt number | Eq. (18) |
| `R` | `R` | dimensionless | radiative correction to supersaturation | Eq. (19) |
| `ℛ` | `ℛ` | W | radiative source term | Eq. (20), Eq. (24) |
| `η, η_a` | `η, η_a` | dimensionless | crystal/atmospheric infrared ratio | Eq. (23), Eq. (27) |
| `α` | `α` | dimensionless | shape coefficient mapping `η_a` to `η` | Eq. (27) |
| `a` | `a` | m | hexagonal column radius | Eq. (31) |
| `c` | `c` | m | hexagonal column half-length | Eq. (31) |
| `c_B` | `c_B` | m | core half-length | Eq. (31), Eq. (33) |
| `φ` | `φ` | dimensionless | aspect ratio `c/a` | Eq. (34) |
| `ψ` | `ψ` | dimensionless | hollowness factor `1 - c_B/c` | Eq. (33) |
| `V, A` | `V, A` | m^3, m^2 | crystal volume, area | Eq. (31) |
| `D_i, r_i` | `D_i, r_i` | m | equivalent diameter/radius | Eq. (37), Eq. (38) |
| `ρ_ie` | `ρ_ie` | kg m^-3 | effective mass density | Eq. (39), Eq. (40) |

## 5. Constants and parameters

Fixed physical constants from paper:

| Identifier | Value | Units | Source |
|---|---:|---|---|
| `g` | 9.81 | m s^-2 | Table 1 |
| `Ω0` | 7.27e-5 | rad s^-1 | Table 1 |
| `R_a` | 287.05 | J kg^-1 K^-1 | Table 1 |
| `R_v` | 461.00 | J kg^-1 K^-1 | Table 1 |
| `ε` | 0.622 | dimensionless | Table 1 |
| `L_s` | 2.837e6 | J kg^-1 | Table 1 |
| `L_v` | 2.525e6 | J kg^-1 | Table 1 |
| `σ` | 5.67e-8 | W m^-2 K^-4 | Table 1 |
| `T_r` | 273.15 | K | Eq. (6), Table 1 |
| `p_r` | 1e5 | Pa | Table 1 |
| `ρ_i` | 920 | kg m^-3 | Sect. 2.2.3 |
| `Q_abs` | 1 | dimensionless | Sect. 2.2.2 |
| crystal emissivity | 1 | dimensionless | Sect. 2.2.2 |

Atmospheric profiles:

- Temperature Eq. (75)/(76): breakpoints `(0,2,8,14,20) km`, temperatures `(T_r+20, T_r, T_r-50, T_r-60, T_r-60) K`.
- Pressure Eq. (77): `p_a(z)=p0 exp(-z/h)`, `p0=101493 Pa`, `h=7.5 km`.
- Humidity Eq. (78)/(79): breakpoints `(0,2,4,10,15,20) km`, `H_a=(0.20,0.30,0.40,0.61,0.20,0)` for Cases 0--1; Cases 2--3 use `H_a3=0.68` at 10 km.
- Infrared ratio Eq. (80)/(81): `η_a=0.9` below 9 km, linearly transitions to `1.1` at 10 km, then `1.1` above. Cases 1--3 override with constant `η=1`, `1.1`, or `0.9`.
- Updraft Eq. (70)/(71): zero below `z_W1=z_W0-0.3 km`, linear transition, constant above. Cases 0--1 use `W_a0=0.6 m/s`; Cases 2--3 use `W_a0=0.8 m/s`; `z_W0` is 10 km for steady modes and 9 km or 7 km for oscillatory modes.
- Horizontal wind Eq. (68)/(69): use corrected constants `z_U1=5 km`, `U_a1=5 m/s`, `z_U0=8 km`, `U_a0=10 m/s`, `z_U2=16 km`, `U_a2=-30 m/s`. This gives shears of `1.0`, `1.666...`, and `-5 m s^-1 km^-1` in layers I--III; note the paper prose says `1.3` for layer II, which is inconsistent with these corrected constants unless another value differs.

Test-case defaults from Table 2:

| Case | `η` | `W_a0` | `z_W0` oscillatory | `H_a3` | `a0` | `c0` | `φ0` | `ψ0` | `c_B0` | `m0` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | altitude-dependent 0.9--1.1 | 0.6 m/s | 9 km | 0.61 | 51.1 µm | 102.2 µm | 2.0 | 0.80 | 20.44 µm | 0.935 µg |
| 1 | 1.0 | 0.6 m/s | 9 km | 0.61 | 50.17 µm | 100.34 µm | 2.0 | 0.80 | 20.068 µm | 0.885 µg |
| 2 | 1.1 | 0.8 m/s | 7 km | 0.68 | 52.0 µm | 104.0 µm | 2.0 | 0.80 | 20.80 µm | 0.986 µg |
| 3 | 0.9 | 0.8 m/s | 7 km | 0.68 | 50.2 µm | 100.4 µm | 2.0 | 0.80 | 20.08 µm | 0.887 µg |

Initial trajectory conditions: `x0=2 km`, `z0=10 km`, `u0=0`, `w0=0.6 m/s` for Cases 0--1 and `w0=0.8 m/s` for Cases 2--3. Lifetimes: 5 h/40 h for Cases 0--1, 4 h/40 h for Cases 2--3. Timesteps: 0.02 s or 0.04 s in the paper.

## 6. Equation inventory

| Ref. | Expression/meaning | Proposed Python function |
|---|---|---|
| Eq. (1a,b) | `ẍ=-k(ẋ-U_a)-2Ω0 ż cosθ`; `z̈=-k(ż-W_a)-g(1-ρ_a/ρ_i)+2Ω0 ẋ cosθ` | `accelerations(...)` |
| Eq. (3) | `k = 6π C_D Re μ_a r_i /(24 m)` | `damping_coefficient(...)` |
| Eq. (4) | `Re = ρ_a r_i sqrt((u-U_a)^2+(w-W_a)^2)/μ_a` | `reynolds_number(...)` |
| Eq. (5) | `C_D = 64/(π Re) * (1 + 0.078 Re^0.945)` | `drag_coefficient(...)` |
| Eq. (6) | polynomial for `μ_a(T)` | `dynamic_viscosity_air(...)` |
| Eq. (7) | moist-air density | `moist_air_density(...)` |
| Eq. (8),(9) | limit/fall velocity | `terminal_fall_speed(...)` |
| Eq. (10) | mass growth with capacitance, ventilation, saturation and radiative correction | `mass_growth_rate(...)` |
| Eq. (12) | `S_l=p_v/p_vsl`, `S_i=p_v/p_vsi` | `saturation_ratios(...)` |
| Eq. (13) | relative humidities | `relative_humidities(...)` |
| Eq. (14) | `q_s=ε p_vsl/(p-p_vsl)` | `saturation_mixing_ratio(...)` |
| Eq. (15) | `D_v(T,p)`, `K_a(T)` | `diffusivity_water_vapor(...)`, `heat_conductivity_air(...)` |
| Eq. (16)--(18) | `f_v=1+0.039X+0.1447X²`, `X=Sc^(1/3) Re^(1/2)` (corrected from PDF text extraction, which dropped both root signs) | `schmidt_number(...)`, `ventilation_coefficient(...)` |
| Eq. (19)--(24) | radiative correction and source | `blackbody_flux(...)`, `radiative_source(...)`, `radiative_correction(...)` |
| Eq. (27) | `η-1=α(η_a-1)` | `crystal_eta(...)` |
| Eq. (28) | growth condition `S_i >= 1+R` | `driving_factor(...)` |
| Eq. (31) | hollow column `V`, `A` | `hollow_column_volume_area(...)` |
| Eq. (33),(34) | `ψ=1-c_B/c`, `φ=c/a` | `hollowness(...)`, `aspect_ratio(...)` |
| Eq. (35),(47) | cubic for `a` under constant `φ,c_B`; implemented with the restored hexagonal `sqrt(3)` factor | `radius_from_volume_constant_phi(...)` |
| Eq. (36) | `V=m/ρ_i` | `volume_from_mass(...)` |
| Eq. (37),(38) | equivalent diameter/radius | `equivalent_diameter(...)`, `equivalent_radius(...)` |
| Eq. (39),(40) | effective density definitions | `effective_density_max_dimension(...)`, `effective_density_column(...)` |
| Eq. (41) | `C=0.751a+0.491c` | `capacitance_hollow_column(...)` |
| Eq. (42)--(44) | explicit-Euler updates for `u,w,x,z,m` | `euler_step(...)` |
| Eq. (45)--(47) | update volume and dimensions from new mass | part of `euler_step(...)` |
| Eq. (68)--(71) | wind/updraft profiles | `Atmosphere.horizontal_wind(...)`, `Atmosphere.updraft(...)` |
| Eq. (75)--(81) | temperature, pressure, humidity, infrared profiles | `Atmosphere.temperature(...)`, `dry_air_pressure(...)`, `Atmosphere.relative_humidity_profile(...)`, `Atmosphere.atmospheric_eta(...)` |
| Eq. (84),(85) | invert relative humidity to vapor pressure | `water_vapor_pressure_from_Hl(...)` |
| Eq. (86),(87) | Sonntag saturation pressures | `saturation_pressure_liquid(...)`, `saturation_pressure_ice(...)` |

## 7. Evaluation order / algorithm

For each time step `n`:

1. Evaluate atmospheric profiles at current `z_n`: `T_a`, `p_a`, `H_l`, `η_a`, `U_a`, `W_a`.
2. Compute saturation pressures `p_vsl(T_a)`, `p_vsi(T_a)`.
3. Compute water vapor pressure `p_v` from `H_l` using Eq. (84)/(85), then total pressure `p=p_a+p_v`.
4. Compute `S_i`, `S_l`, densities, `μ_a`, `D_v`, `K_a`.
5. From current mass, update `V`, solve dimensions `a,c,c_B`, compute `A`, `C`, `D_i`, `r_i`, `ρ_ie`.
6. Compute `Re`, `C_D`, `k`, `Sc`, `f_v`.
7. Compute radiative `η` and `R`.
8. Compute `dm/dt` from Eq. (10).
9. Update velocities with Eq. (42) and positions with Eq. (43).
10. Update mass with Eq. (44); stop if mass becomes non-positive unless `allow_negative_mass=True` for debugging.
11. Recompute `V,a,c,A,C,...` from the new mass for diagnostics.
12. Append all diagnostic quantities to output.

## 8. Numerical methods

- Use the paper's explicit Euler method as the default integrator.
- Provide a `dt` argument as a Pint time quantity; default to paper values depending on scenario but do not hard-code one universal value.
- Cubic Eq. (35)/(47): solve the hexagonal-column volume equation `sqrt(3) * (2 φ a + c_B) * a^2 - V = 0` and select the unique positive real root. The PDF text extraction dropped the radical in Eq. (31a); the restored `sqrt(3)` factor is required to reproduce Table 2 geometry. The implementation uses `scipy.optimize.brentq` with a positive bracket.
- Piecewise-linear profiles should be literal, not interpolated splines.
- Stop conditions: elapsed time, altitude bounds optional, nonpositive mass.

## 9. Ambiguities / required user decisions

Resolved by user correction:

1. **Horizontal wind constants Eq. (69):** `z_U1=5 km`, `U_a1=5 m/s`; use inferred/visible upper constants `z_U0=8 km`, `U_a0=10 m/s`, `z_U2=16 km`, `U_a2=-30 m/s`.
2. **Ventilation Eq. (17):** implement `X=Sc^(1/3) Re^(1/2)`.

Remaining implementation notes:

3. **Density symbols:** Eq. (7) defines `ρ_m`/moist-air density but it does not appear to be used elsewhere in the governing model. Keep `moist_air_density(...)` as a reference equation function, but use dry-air density `ρ_a=p_a/(R_a T_a)` in Eq. (1), Eq. (4), and Eq. (18), matching the printed symbols in those equations.
4. **Radiative coefficient `α`:** Eq. (27) is only a diagnostic relation connecting crystal-related `η` to atmospheric `η_a`; the numerical cases appear to specify/use `η` directly (constant in Cases 1--3, altitude-dependent in Case 0). Do not require `α` as a model input. Optionally provide `alpha_from_eta(η,η_a)` and `eta_from_alpha(α,η_a)` helper functions for diagnostics.

Non-blocking decisions now resolved:

- Include Coriolis terms in the implementation, controlled by an `Ω0` parameter and latitude `θ`; keep them enabled by equation default but easy to set to zero/disable.
- Outputs should be Pint quantities.
- Add `pytest` as a development dependency.

## 10. Proposed file layout

Create/modify:

Implemented:

- `src/cloud_rom/berton2023.py` — constants, atmosphere profiles, equation functions, `LocalDiagnostics`, explicit-Euler stepping, case helpers, and simulator.
- `src/cloud_rom/berton2023_plots.py` — plotting and numeric conversion helpers used by notebooks.
- `src/cloud_rom/__init__.py` — package marker.
- `tests/test_berton2023.py` — dimensional, smoke, and Table 2 geometry tests.
- `examples/berton2023_case0.py` — minimal short Case 0 run.
- `notebooks/atmospheric-profiles.ipynb` — reproduces paper Figures 1--5.
- `notebooks/replicate-steady-state.ipynb` — steady/non-oscillatory Case 0 reproduction workflow.
- `notebooks/replicate-oscillatory-state.ipynb` — oscillatory Case 0 reproduction workflow.
- `docs/MODEL_EXTRACTION.md` — this extraction/implementation record.
- `docs/berton2023-model-code.md` — code guide for humans and agents.
- `docs/notebooks.md` — notebook guide.

Packaging/tooling:

- `pyproject.toml` now declares a Hatchling build backend for `src/cloud_rom`, so `uv run pytest` works without `PYTHONPATH=src`.
- `pytest` is included in the development dependency group.
- Runtime dependencies include `tqdm` for optional progress bars in long integrations.

## 11. Test plan

Dimensional/unit tests:

- `dynamic_viscosity_air(T)` returns pressure*time dimension.
- `mass_growth_rate(...)` returns kg/s.
- `damping_coefficient(...)` returns 1/s.
- `accelerations(...)` returns m/s².
- incompatible units fail through Pint dimensionality errors.

Equation smoke tests:

- `T_a(0 km)=293.15 K`, `T_a(8 km)=223.15 K`, `T_a(20 km)=213.15 K`.
- `p_a(0)=101493 Pa`, `p_a(7.5 km)=p0/e`.
- `η_a(9 km)=0.9`, `η_a(9.5 km)=1.0`, `η_a(10 km)=1.1`.
- `hollow_column_volume_area` for Table 2 Case 0 should reproduce `m0≈0.935 µg` from `a0=51.1 µm`, `c0=102.2 µm`, `c_B0=20.44 µm`, `ρ_i=920 kg/m³`.
- `capacitance` for Case 0 should reproduce `C0≈88.6 µm`.
- `equivalent_diameter` for Case 0 should reproduce `D0≈125 µm`.
- `effective_density_column` for Case 0 should reproduce `ρ_ie0≈675 kg/m³`.

Reference/regression tests from paper:

- Short Case 0/1 smoke run should remain finite and positive mass for initial timesteps.
- Full 40 h runs are expensive at `dt=0.04 s`; use optional slow tests to compare approximate period/wavelength/limit altitude from Table 2 if desired.
- Paper lacks machine-readable trajectories, so full model validation can only be approximate against Table 2 and qualitative figures.

Physical sanity tests:

- Mass increases when `S_i - 1 - R > 0`, decreases when `< 0`.
- Cubic dimension solve returns positive `a,c` and preserves `V`.
- `C_D`, `f_v`, `k`, `D_i`, `A`, `V` are positive for physical states.

## 12. Example plan

Implemented examples/notebooks:

- `examples/berton2023_case0.py`: short Case 0 run that prints final state diagnostics.
- `notebooks/atmospheric-profiles.ipynb`: reproduces Figures 1--5 atmospheric profiles.
- `notebooks/replicate-steady-state.ipynb`: runs and plots the steady/non-oscillatory Case 0 state.
- `notebooks/replicate-oscillatory-state.ipynb`: runs and plots the oscillatory Case 0 state.

The reproduction notebooks are qualitative/table-based because the paper does not provide machine-readable trajectory data.

## 13. Phase 2 implementation status

Phase 2 has been implemented.

Code and API status:

- `Atmosphere` owns the prescribed vertical profiles and exposes profile methods rather than module-level profile functions.
- `LocalDiagnostics` is a dataclass built with `LocalDiagnostics.from_state(...)`; it stores all local atmospheric, crystal, drag, radiative, and mass-growth quantities used by one Euler step.
- `simulate(...)` returns a `pandas.DataFrame` whose physical columns are Pint quantities. Use `quantity_column_to(...)` or `cloud_rom.berton2023_plots.qcol(...)` to convert columns for plotting.
- `euler_step(...)` implements the paper's explicit Euler update and returns `(next_state, diagnostics)`.
- `atmosphere_for_case(...)` and `initial_state_for_case(...)` encode Table 2 case defaults.

Validation commands run during implementation:

```bash
uv run pytest -q
uv run pyright
uv run python examples/berton2023_case0.py
```

Current validation status:

- Tests pass and Pyright reports zero errors.
- Case 0 geometry reproduces Table 2 initial values for mass, capacitance, equivalent diameter, and effective density within test tolerances.
- Atmospheric profile notebook code executes and reproduces the prescribed profiles from Appendix A.
- Full trajectory validation remains qualitative because the paper does not provide machine-readable trajectory output.

Known implementation-specific notes:

- Pint 0.25.3 is Python 3.12 compatible, but its static typing currently reports registry-created quantities as `PlainQuantity[...]`; the code therefore uses `Quantity: TypeAlias = Any` while keeping runtime Pint quantities throughout.
- `moist_air_density(...)` implements Eq. (7) for traceability but is not used in the coupled dynamics.
- `alpha_from_eta(...)` and `eta_from_alpha(...)` are diagnostic helpers only; numerical cases specify/use `η` directly.
- The restored `sqrt(3)` factor in hollow-column volume is required to reproduce Table 2 values and corrects a PDF text-extraction loss.
