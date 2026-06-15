# TASK-009 full Berton AUTO-07p validation

This note records the reproducible build/run and validation commands for the full four-state Berton AUTO problem in `episodes/04-full-model-auto-equilibria/auto/berton_full/bertonfull.f90`.

## AUTO problem

The Fortran AUTO problem uses the TASK-008 state mapping:

- `U(1)=z` altitude [m]
- `U(2)=u` horizontal velocity [m/s]
- `U(3)=w` vertical velocity [m/s]
- `U(4)=m` crystal mass [kg]

The cyclic horizontal position `x` is omitted.  `FUNC` evaluates the physical-unit RHS

```text
F(1) = w
F(2) = -k(u-U_a(z)) - 2 f_c w
F(3) = -k(w-W_a(z)) - g(1-rho_a/rho_i) + 2 f_c u
F(4) = m_dot
```

where thermodynamics, drag, crystal geometry, radiation, ventilation, and mass growth are ported directly from `src/cloud_rom/berton2023.py`.  The initial run sets `include_coriolis=0` and uses the diameter Reynolds convention.

## Build and AUTO run

From the repository root:

```bash
bash episodes/04-full-model-auto-equilibria/auto/berton_full/run_auto.sh
```

This compiles `episodes/04-full-model-auto-equilibria/auto/berton_full/bertonfull.f90` with the installed AUTO-07p environment and saves:

- `episodes/04-full-model-auto-equilibria/auto/berton_full/b.bertfull-zW0`
- `episodes/04-full-model-auto-equilibria/auto/berton_full/s.bertfull-zW0`
- `episodes/04-full-model-auto-equilibria/auto/berton_full/d.bertfull-zW0`

The continuation constants are in `episodes/04-full-model-auto-equilibria/auto/berton_full/c.bertonfull`; the primary continuation parameter is `PAR(1)=z_W0`, with user output at 10000, 9500, 9000, and 8500 m.

## Initial equilibrium

`STPNT` uses a Python steady solve at the high-base Case-0 setting (`z_W0=10000 m`, `W_a0=0.6 m/s`, `H_a3=0.61`, `eta_blend=0`, `include_coriolis=0`):

```text
z = 10178.50407189 m
u = -0.89252035945 m/s
w = 0 m/s
m = 1.057007179452e-9 kg
```

Independent Python validation of the AUTO-saved initial point reports residual

```text
[0.0, -8.98843029e-09, -3.02515346e-10, -2.15440121e-23]
||F||_2 = 8.993519586403786e-09
```

The small nonzero acceleration components are due to decimal precision in the saved AUTO solution file.

## PVLS diagnostics

`PVLS` writes auxiliary diagnostics beginning at `PAR(60)`, including:

- `sigma_S`, `R_zeta`, `sigma_plus_Rzeta`
- `R`, `rad_R`, `driving_factor`, `m_dot`
- `k`, `Re`, `C_D`, `f_v`, `Sc`
- `T_a`, `p_a`, `p_v`, `S_i`, `H_l`, `eta`, `eta_a`
- `W_a`, `U_a`, `rho_a`
- crystal geometry `V`, `a`, `c`, `A`, `D_i`, `r_i`, `C`, `psi`, `rho_ie`
- `vertical_force_residual`, `growth_balance_residual`
- finite-difference mass-slope proxies for vertical force and growth
- `reduced_det_proxy`, the local 2x2 determinant proxy from finite-difference `(z,m)` force/growth slopes

## Python/Fortran RHS and eigenvalue validation

Run:

```bash
uv run python episodes/04-full-model-auto-equilibria/scripts/berton_full_auto_task009_validate.py
```

or include a fresh AUTO run:

```bash
uv run python episodes/04-full-model-auto-equilibria/scripts/berton_full_auto_task009_validate.py --run-auto
```

Current validation output:

```text
Fortran/Python RHS comparison (max abs diff): [0.00000000e+00 0.00000000e+00 0.00000000e+00 1.02500694e-24]
AUTO initial solution U: [ 1.01785041e+04 -8.92520359e-01  0.00000000e+00  1.05700718e-09]
Python residual at AUTO initial solution: [ 0.00000000e+00 -8.98843029e-09 -3.02515346e-10 -2.15440121e-23]
Residual norm: 8.993519586403786e-09
AUTO d-file eigenvalues: [ 2.38933e-04+0.j -2.56484e-04+0.j -1.63426e+01+0.j -1.85823e+01+0.j]
Python finite-difference Jacobian eigenvalues: [-1.63426322e+01 -2.56484059e-04  2.38933324e-04 -1.85823275e+01]
Fortran AUTO-port finite-difference Jacobian eigenvalues: [-1.63426322e+01 -2.56484059e-04  2.38933324e-04 -1.85823275e+01]
Validation passed: Fortran RHS matches Python samples and AUTO fixed point residual/eigenvalues are independently checked.
```

The RHS comparison compiles a standalone Fortran driver against the same `bertonfull.f90` module used by AUTO and compares selected state/parameter samples with `src/cloud_rom/berton2023.py`.  Tolerances are `1e-12` for `z_dot`, `5e-8 m/s^2` for accelerations, and `5e-18 kg/s` for mass growth.  The eigenvalue check parses AUTO's `d.bertfull-zW0` eigenvalues, finite-differences both the Python RHS and the Fortran AUTO-port RHS at the AUTO-saved initial fixed point, and compares all three Jacobian spectra.
