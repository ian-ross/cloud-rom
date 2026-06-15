# TASK-011 full Berton Case-0 oscillatory-orbit classification

## Command

Run from repository root:

```bash
uv run python episodes/05-full-model-oscillatory-orbit/scripts/berton_full_task011_classify.py
```

## Canonical configuration

- `atmosphere_for_case(0, oscillatory=True)`: `z_W0=9 km`, `W_a0=0.6 m/s`, `H_a3=0.61`, `eta_override=None`.
- `initial_state_for_case(0)`.
- `SimulationConfig(include_coriolis=False, stop_on_nonpositive_mass=False)`.
- Long classification integrations use SciPy `BDF` and `LSODA`; no explicit-Euler long integration is used.
- Solver controls: `duration=500 h`, `output_dt=10 min`, `rtol=1e-7`, `atol=[1e-2, 1e-2, 1e-5, 1e-5, 1e-16]`, `max_step=600 s`.

## Extension rule

The required 200 h BDF/LSODA runs still had a nonzero late envelope, so the workflow extends both solvers to 500 h and classifies using the 450-500 h envelope.

## Verdict

**damped/equilibrium-like**, not a finite-amplitude limit cycle.

Key diagnostics:

| method | duration_h | base_duration_h | extension_rule | z_final_m | u_final_m_s | w_final_m_s | m_final_kg | z_amp_150_200h_m | z_amp_450_500h_m | amp_ratio_late_to_base | late_peak_period_h | classification |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BDF | 500 | 200 | Amplitude at 150-200 h remained nonzero; extend both BDF and LSODA to 500 h and classify using the 450-500 h envelope. | 9618.03 | 1.90986 | 2.27999e-07 | 1.08023e-09 | 19.2083 | 0.0092358 | 0.000480824 | 10.2037 | damped/equilibrium-like |
| LSODA | 500 | 200 | Amplitude at 150-200 h remained nonzero; extend both BDF and LSODA to 500 h and classify using the 450-500 h envelope. | 9618.03 | 1.90986 | 2.26344e-07 | 1.08023e-09 | 19.2082 | 0.00920939 | 0.000479451 | 10.1944 | damped/equilibrium-like |

Solver agreement:

| horizon_h | max_abs_z_diff_m | max_abs_w_diff_m_s | late_max_abs_z_diff_m | late_max_abs_w_diff_m_s |
| --- | --- | --- | --- | --- |
| 200 | 0.00648993 | 7.34056e-06 | 0.0016371 | 2.99633e-07 |
| 500 | 0.00648993 | 7.34056e-06 | 4.3517e-05 | 7.94254e-09 |

The 450-500 h envelope is less than 0.05 of the 150-200 h envelope for both solvers, and BDF/LSODA agree to sub-meter altitude differences over the full run.

## Equilibrium/eigenvalue seed

Refined reduced equilibrium (x is cyclic/arbitrary in the no-Coriolis run):

| root_success | root_message | z_eq_m | u_eq_m_s | w_eq_m_s | m_eq_kg | rhs_norm | rhs_z_m_s | rhs_u_m_s2 | rhs_w_m_s2 | rhs_m_kg_s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| True | The solution converged. | 9618.03 | 1.90986 | -2.90845e-21 | 1.08023e-09 | 2.13194e-13 | -2.90845e-21 | 3.62867e-15 | -2.13163e-13 | -3.79552e-25 |

Finite-difference eigenvalues:

| eigenvalue_index | real_s_inv | imag_s_inv | period_h_if_complex | e_folding_h |
| --- | --- | --- | --- | --- |
| 1 | -16.3421 | 0 |  | 1.69977e-05 |
| 2 | -18.7184 | 0 |  | 1.48399e-05 |
| 3 | -7.06018e-06 | 0.000171212 | 10.1939 | 39.3443 |
| 4 | -7.06018e-06 | -0.000171212 | 10.1939 | 39.3443 |

The complex pair (Re=-7.060180e-06 s^-1, |Im|=1.712123e-04 s^-1, period=10.194 h, e-folding=39.344 h) explains the observed decaying oscillation: it is a stable spiral mode, not a Hopf-neutral or growing oscillatory mode.

## Generated files

- `case0_bdf_500h.csv`
- `case0_equilibrium_eigenvalues.png`
- `case0_late_envelope.png`
- `case0_long_timeseries.png`
- `case0_lsoda_500h.csv`
- `case0_solver_agreement.png`
- `classification_verdict.json`
- `continuation_equilibrium_eigenvalues.csv`
- `continuation_equilibrium_seed.csv`
- `eigenvalues.csv`
- `equilibrium.csv`
- `extrema.csv`
- `late_time_tail_480_500h.csv`
- `solver_agreement.csv`
- `summary.csv`

## Residual risks

- The classification is for the no-Coriolis canonical Case-0 settings requested here; adding Coriolis changes horizontal dynamics.
- The finite-difference Jacobian is local and uses the Python RHS, not AUTO's Fortran-generated Jacobian.
- The primary continuation seed is an equilibrium/state seed because the trajectory settles; no periodic-orbit seed is exported as primary evidence.
