# TASK-008 design: full Berton AUTO continuation state and controls

## Scope and source implementation

This design specifies the first full-model AUTO-07p problem to build from `src/cloud_rom/berton2023.py` after the reduced 3D validation in `episodes/03-reduced-model-auto/auto/berton_reduced_3d`.  It is a design handoff for TASK-009: state ordering, parameter ordering, equilibrium equations, primary continuation controls, and diagnostics should be implementable without rediscovering the mapping.

The source ODE in `berton2023.py` is the autonomous part of `_ode_rhs`:

```text
x_dot = u
z_dot = w
u_dot = -k(u - U_a(z)) - 2 f_c w
w_dot = -k(w - W_a(z)) - g(1 - rho_a(z)/rho_i) + 2 f_c u
m_dot = M(z, u, w, m; profiles, constants)
```

where `f_c = Ω0 cos(theta)`, and `M` is the mass-growth rate from `LocalDiagnostics.from_state(...)`:

```text
M = 4 pi C(m) f_v(Re) [S_i(z) - 1 - R(z,m)] / denominator(z).
```

The horizontal position `x` is cyclic: no model ingredient depends on `x`.  It should not be included in the first equilibrium-continuation problem because `x_dot = u` would require zero absolute horizontal velocity and introduces a neutral translation direction unrelated to the vertical Hopf mechanism.  AUTO should instead solve the vertical/profile equilibrium in a frame that ignores horizontal translation.

## AUTO state vector U

Use a four-dimensional full Berton equilibrium state:

| AUTO state | Python field / quantity | Units | Role |
|---|---|---:|---|
| `U(1)` | `z` | m | altitude, the profile coordinate used by `U_a`, `W_a`, `T_a`, `H_a`, and `eta` |
| `U(2)` | `u` | m s^-1 | horizontal parcel velocity entering drag and Coriolis |
| `U(3)` | `w` | m s^-1 | vertical parcel velocity; equilibrium requires `w = 0` in the fixed-altitude frame |
| `U(4)` | `m` | kg | ice crystal mass; geometry is recomputed from mass with fixed `phi` and `c_B` |

Do **not** include these quantities as state variables in the initial full AUTO problem:

- `x`: cyclic/ignorable position; omit or treat as a reconstructed output using `x_dot = u` after continuation.
- `t`: AUTO handles autonomous time internally.
- crystal dimensions `V`, `a`, `c`, `A`, `D_i`, `r_i`, `C`: algebraic functions of `m`, fixed `phi`, fixed `c_B`, and constants.
- diagnostic thermodynamics and transport (`T_a`, `p_a`, `S_i`, `rho_a`, `k`, `Re`, etc.): algebraic outputs from `z`, `u`, `w`, `m`, and `PAR`.

Recommended numerical scaling for TASK-009:

```text
z_scale = 1e4 m
u_scale = w_scale = 1 m/s
m_scale = 1e-9 kg
```

AUTO itself can store physical-unit magnitudes.  If Newton conditioning is poor, introduce scaled internal variables
`Z=z/z_scale`, `U=u/u_scale`, `W=w/w_scale`, `M=m/m_scale`, but keep `PVLS` outputs in physical units.

## Equilibrium equations

The equilibrium residual for AUTO should be the full four-state RHS with `x` omitted:

```text
F(1) = w
F(2) = -k(u - U_a(z)) - 2 f_c w
F(3) = -k(w - W_a(z)) - g(1 - rho_a(z)/rho_i) + 2 f_c u
F(4) = m_dot(z, u, w, m)
```

At an equilibrium:

```text
w* = 0
u* = U_a(z*)                    if Coriolis is disabled
u* = U_a(z*) - (2 f_c/k*) w*    in general, so still U_a(z*) when w*=0
k*(W_a(z*) - w*) + 2 f_c u* = g(1 - rho_a(z*)/rho_i)
m_dot(z*, u*, w*, m*) = 0
```

The first implementation should support both `include_coriolis = 0` and `1`, but the initial continuation should set `include_coriolis = 0` unless TASK-009 specifically needs Berton's horizontal/Coriolis drift.  With Coriolis enabled, the term `2 f_c u*` is numerically comparable to `O(1e-3 m/s^2)` for `u ~ 10 m/s`, so it can change the static vertical force balance even though the reduced 3D analysis neglected it.

The equilibrium mass condition is equivalent to the Berton growth-balance condition:

```text
S_i(z*) - 1 - R(z*, m*) = 0
```

because all denominator/capacitance/ventilation factors multiplying this driving factor are positive in the physical regime.  For robustness, AUTO should still evaluate the actual `m_dot` residual rather than replacing it by only the dimensionless driving factor; output both.

## AUTO parameter vector PAR

Use physical-unit magnitudes.  Keep the ordering stable so saved AUTO branches are reproducible.

### Primary/free controls

| PAR | Name | Units | Default / baseline | Notes |
|---:|---|---:|---:|---|
| `PAR(1)` | `z_W0` | m | `10000` for steady start, then continue toward `9000` | **Initial primary continuation parameter** |
| `PAR(2)` | `W_a0` | m s^-1 | `0.6` for Cases 0--1 | updraft amplitude |
| `PAR(3)` | `rad_mult` | - | `1.0` | multiplier on radiative correction `R`; `0` disables net radiative correction in growth balance |
| `PAR(4)` | `H_a3` | - | `0.61` Case 0/1, `0.68` Case 2/3 | upper-tropospheric humidity control at 10 km |
| `PAR(5)` | `eta_mode_or_override` | - | sentinel, see below | use `eta_a(z)` for Case 0 or constant override for Cases 1--3 |
| `PAR(6)` | `drag_mult` | - | `1.0` | multiplier on `k`, useful as a mechanism probe and reduced-model cross-check |

For `PAR(5)`, avoid a branch-discontinuous integer mode inside continuation.  Recommended TASK-009 convention:

```text
PAR(5) = eta_override_value
PAR(6 or a later flag) = eta_blend
eta(z) = (1 - eta_blend) * eta_a(z) + eta_blend * eta_override_value
```

with `eta_blend=0` for Case 0 and `eta_blend=1` for constant-eta cases.  If keeping `PAR(6)` as `drag_mult`, place `eta_blend` in the fixed/profile block below.

### Fixed profile/shape/constants block

The following should be represented explicitly in `PAR` even when fixed in the first run, because later two-parameter continuation and sensitivity runs will need them.

| PAR | Name | Units | Default |
|---:|---|---:|---:|
| `PAR(7)` | `Delta_z_W` | m | `300` |
| `PAR(8)` | `z_U1` | m | `5000` |
| `PAR(9)` | `U_a1` | m s^-1 | `5` |
| `PAR(10)` | `z_U0` | m | `8000` |
| `PAR(11)` | `U_a0` | m s^-1 | `10` |
| `PAR(12)` | `z_U2` | m | `16000` |
| `PAR(13)` | `U_a2` | m s^-1 | `-30` |
| `PAR(14)` | `z_T0` | m | `0` |
| `PAR(15)` | `T_a0` | K | `293.15` |
| `PAR(16)` | `z_T1` | m | `2000` |
| `PAR(17)` | `T_a1` | K | `273.15` |
| `PAR(18)` | `z_T2` | m | `8000` |
| `PAR(19)` | `T_a2` | K | `223.15` |
| `PAR(20)` | `z_T3` | m | `14000` |
| `PAR(21)` | `T_a3` | K | `213.15` |
| `PAR(22)` | `z_T4` | m | `20000` |
| `PAR(23)` | `T_a4` | K | `213.15` |
| `PAR(24)` | `z_H0` | m | `0` |
| `PAR(25)` | `H_a0` | - | `0.20` |
| `PAR(26)` | `z_H1` | m | `2000` |
| `PAR(27)` | `H_a1` | - | `0.30` |
| `PAR(28)` | `z_H2` | m | `4000` |
| `PAR(29)` | `H_a2` | - | `0.40` |
| `PAR(30)` | `z_H3` | m | `10000` |
| `PAR(31)` | `H_a4` | - | `0.20` |
| `PAR(32)` | `z_H4` | m | `15000` |
| `PAR(33)` | `H_a5` | - | `0.0` |
| `PAR(34)` | `z_H5` | m | `20000` |
| `PAR(35)` | `z_eta0` | m | `9000` |
| `PAR(36)` | `eta_a0` | - | `0.9` |
| `PAR(37)` | `z_eta1` | m | `10000` |
| `PAR(38)` | `eta_a1` | - | `1.1` |
| `PAR(39)` | `eta_blend` | - | `0.0` for Case 0 |
| `PAR(40)` | `phi` | - | `2.0` |
| `PAR(41)` | `c_B` | m | `20.44e-6` for Case 0 |
| `PAR(42)` | `theta` | rad | `pi/4` |
| `PAR(43)` | `include_coriolis` | - | `0` initially, `1` for paper-faithful rerun |
| `PAR(44)` | `reynolds_length_mode` | - | `2` for diameter convention, `1` for radius convention |
| `PAR(45)` | `rho_i` | kg m^-3 | `920` |
| `PAR(46)` | `g` | m s^-2 | `9.81` |
| `PAR(47)` | `Omega0` | s^-1 | `7.27e-5` |
| `PAR(48)` | `R_a` | J kg^-1 K^-1 | `287.05` |
| `PAR(49)` | `R_v` | J kg^-1 K^-1 | `461.00` |
| `PAR(50)` | `epsilon` | - | `0.622` |
| `PAR(51)` | `L_s` | J kg^-1 | `2.837e6` |
| `PAR(52)` | `sigma_SB` | W m^-2 K^-4 | `5.67e-8` |
| `PAR(53)` | `emissivity` | - | `1.0` |

TASK-009 can initially hard-code the fixed block in Fortran if necessary, but it should reserve the PAR slots and document any constants not yet externally adjustable.

## Candidate continuation parameters

1. **`z_W0` / updraft-base or updraft-top altitude (`PAR(1)`)**: primary physical control for the first full Berton Hopf search.  In the code, `W_a(z)` is zero below `z_W1 = z_W0 - Delta_z_W`, ramps over `Delta_z_W`, and equals `W_a0` above `z_W0`.  Berton reports a steady/non-oscillatory Case 0 at `z_W0 = 10 km` and an oscillatory Case 0 at `z_W0 = 9 km`; therefore continuing `z_W0` downward directly follows the observed transition.
2. **`W_a0` (`PAR(2)`)**: controls vertical forcing strength.  It distinguishes Cases 0--1 (`0.6 m/s`) from Cases 2--3 (`0.8 m/s`) and changes the force-balance altitude for a given crystal size.
3. **`rad_mult` (`PAR(3)`)**: multiplies the radiative correction `R` in the growth driving factor.  This tests whether net radiative transfer shifts the Hopf locus, while preserving the rest of the thermodynamic profile.
4. **Humidity/profile controls (`H_a3`, `eta_a0`, `eta_a1`, `eta_blend`, `eta_override`)**: these change `S_i(z)`, `R(z,m)`, and especially the combined gradient `sigma_S + R_zeta` identified in the reduced analysis.
5. **`drag_mult` or Reynolds convention**: mechanism probe for damping and reduced-model consistency; not the first physical control because Berton's transition is not described as a drag-parameter experiment.
6. **Crystal habit/geometry (`phi`, `c_B`, possibly `rho_i`)**: changes capacitance, area, fall-speed damping, and mass-radius relations.  Useful for robustness after the main transition is located.

## Initial primary control choice

Choose `PAR(1) = z_W0` as the first primary continuation parameter.

Start from a steady high-base Case-0 equilibrium near `z_W0 = 10000 m`, then continue toward `9000 m`.  This is the most direct AUTO analogue of Berton's reported transition: all other Case-0 controls remain fixed while the updraft onset/top is lowered from 10 km to 9 km.  It is also preferable to a synthetic gradient multiplier because the reduced-model validation already used a synthetic `alpha_grad` only as an AUTO/Hopf diagnostic check; the full-model question is whether the paper's physical updraft-base change moves an actual equilibrium through a Hopf surface.

Suggested first continuation interval:

```text
ICP = [1]
PAR(1): 10000 m -> 9000 m, with room to continue to 8500 m if no bifurcation is detected
```

After a branch and any Hopf labels are found, use two-parameter continuation in `(z_W0, W_a0)` and `(z_W0, rad_mult)`.

## Auxiliary diagnostics for PVLS/output

Record these in `PVLS` as output-only `PAR` entries after the fixed input block, beginning at `PAR(60)` or later to avoid collisions.

| Diagnostic | Units | Definition / reason |
|---|---:|---|
| `sigma_S` | m^-1 | `d(S_i - 1)/dz` at the equilibrium, finite-differenced or analytic within the active profile segment |
| `R_zeta` | m^-1 | `dR/dz` at fixed `m,u,w`; include both thermodynamic and `eta_a`/radiation-profile contributions |
| `sigma_plus_Rzeta` | m^-1 | `sigma_S + R_zeta`; key reduced-model sign/control quantity |
| `R` / radiative correction | - | dimensionless radiative correction in `S_i - 1 - R` |
| `rad_mult * R` | - | actual correction entering the residual |
| `fall_speed_slope_proxy` | s^-1 or m s^-1 per kg | local derivative of the vertical force/slip equilibrium with respect to `m`; reduced analogue is `B = dV_f/dr = 2 beta r*` |
| `reduced_det_proxy` | s^-2 or scaled | reduced determinant proxy `w_eff*c_eff - B_eff*d_eff` where applicable; output `NaN`/sentinel if finite differences fail |
| `driving_factor` | - | `S_i - 1 - rad_mult*R` |
| `m_dot` | kg s^-1 | should be near zero on equilibrium branch |
| `k` | s^-1 | drag relaxation rate after `drag_mult` |
| `Re`, `C_D`, `f_v`, `Sc` | - | drag/ventilation regime and checks for singular low-Re behavior |
| `T_a`, `p_a`, `p_v`, `S_i`, `H_l`, `eta`, `eta_a` | mixed | physical branch interpretation |
| `W_a`, `U_a`, `rho_a` | mixed | force-balance interpretation |
| `V`, `a`, `c`, `A`, `D_i`, `r_i`, `C`, `psi`, `rho_ie` | mixed | crystal geometry along branch |
| `vertical_force_residual` | m s^-2 | `-k(w-W_a)-g(1-rho_a/rho_i)+2f_c u`, should be near zero |
| `growth_balance_residual` | - | dimensionless `S_i - 1 - rad_mult*R`, should be near zero at equilibrium |

For finite-difference diagnostics, use a step small relative to the physical scale but large enough to avoid cancellation, e.g. `dz = 1 m` and relative mass perturbation `dm/m = 1e-4`, then test sensitivity.  Because several profiles are piecewise linear, also output active segment identifiers or distances to profile breakpoints (`z_W0`, `z_W0-Delta_z_W`, 9 km, 10 km, humidity/temperature knots).  Do not trust finite-difference gradients when the equilibrium is within the perturbation step of a kink.

## Implementation notes for TASK-009

- Reuse the equation order and units from `src/cloud_rom/berton2023.py`; do not change physical formulas while porting.
- Start with the diameter Reynolds convention (`reynolds_length_mode=2`) because the current reference implementation defaults to `SimulationConfig.reynolds_length = "diameter"`.
- Guard against nonphysical states: `m <= 0`, `T <= 0`, negative pressures, and invalid Reynolds numbers should return large residuals or stop continuation rather than silently producing NaNs.
- The mass-to-radius relation requires solving a cubic in Python.  In Fortran, implement a deterministic positive-root routine for `sqrt(3)*(2*phi*a + c_B)*a^2 = m/rho_i`; verify against `tests/test_berton2023.py` Case-0 geometry values before running AUTO.
- AUTO bifurcation labels should be cross-checked with a Python finite-difference Jacobian of the four-state residual at selected branch points, analogous to the reduced TASK-007 cubic cross-check.
