# Full Berton dynamics continuation report

## Executive verdict

For the canonical Berton Case-0 oscillatory configuration studied here, the best-supported interpretation is **damped transient approach to a stable equilibrium**, not a validated local Hopf bifurcation and not a demonstrated finite-amplitude periodic orbit.

The evidence chain is:

1. The first full-model AUTO equilibrium continuation in `z_W0` did **not** detect LP/HB/BP special points in the 10 km to 9 km regime. The branch remained insensitive to `z_W0` because the solved equilibrium sits above the updraft transition and therefore sees the saturated updraft value.
2. Long no-Coriolis BDF and LSODA integrations of the canonical oscillatory Case-0 configuration to 500 h showed the oscillation envelope collapsing by a factor of about `4.8e-4` between 150-200 h and 450-500 h.
3. The late-time state refines to an equilibrium with a stable complex eigenpair, period about 10.19 h and e-folding time about 39.34 h, which explains the observed decaying oscillation.
4. AUTO continuation initialized from that late-time equilibrium accepted the seed but failed at the first continuation step for both `W_a0` and `H_a3` directions. This is a conditioning/convergence limitation of the current formulation, not evidence for a periodic orbit.
5. An independent Python equilibrium-control probe indicates that `W_a0` moves the local stable equilibrium and `H_a3` can move the critical pair through positive real part, but this remains a direction-finding diagnostic until AUTO is reformulated and validates the branch/special point.

Thus Berton's reported oscillatory case is currently best explained, within this implementation and parameterization, as a **stable spiral transient near a full-model equilibrium**. A parameter-dependent Hopf scenario under a different control or a more carefully scaled continuation formulation remains possible, but it is not established by the completed continuation evidence.

## Reproducibility and runtime assumptions

AUTO interactions are notebook-first and use the system AUTO-07p installation documented in `AGENTS.md`:

- AUTO executable: `/usr/local/bin/auto`
- AUTO root: `/usr/local/lib64/auto-07p`
- AUTO Python parent path, when needed: `/usr/local/lib64/auto-07p/python`

Python workflows use repository scripts and Matplotlib-generated diagnostics. The full-model episodes relevant to this report are:

- `episodes/04-full-model-auto-equilibria/` — full-model AUTO equilibrium setup and `z_W0` screen.
- `episodes/05-full-model-oscillatory-orbit/` — long BDF/LSODA classification of the observed Case-0 oscillation.
- `episodes/06-full-model-auto-seed-continuation/` — continuation attempts from the long-integration seed.

Primary reproduction commands from the repository root are:

```bash
bash episodes/04-full-model-auto-equilibria/auto/berton_full/run_auto.sh
uv run python episodes/04-full-model-auto-equilibria/scripts/berton_full_auto_task010_analyze.py

uv run python episodes/05-full-model-oscillatory-orbit/scripts/berton_full_task011_classify.py

bash episodes/06-full-model-auto-seed-continuation/auto/berton_full_task012/run_auto.sh
uv run python episodes/06-full-model-auto-seed-continuation/scripts/berton_full_task012_seed_continuation.py
```

Notebook entry points:

- `episodes/04-full-model-auto-equilibria/notebooks/berton_full_auto_task010_continuation.ipynb`
- `episodes/05-full-model-oscillatory-orbit/notebooks/task011_case0_long_integration.ipynb`
- `episodes/06-full-model-auto-seed-continuation/notebooks/task012_seed_continuation.ipynb`

## State and parameter mapping

The full no-Coriolis dynamics use the physical state coordinates:

| coordinate | meaning | unit |
| --- | --- | --- |
| `x` | horizontal position, cyclic/arbitrary in no-Coriolis equilibrium classification | m |
| `z` | parcel/cloud altitude | m |
| `u` | horizontal velocity | m s^-1 |
| `w` | vertical velocity | m s^-1 |
| `m` | particle/cloud mass coordinate | kg |

The AUTO equilibrium screens use the dynamic subset needed by the full model formulation and parameters corresponding to the canonical Berton Case 0. The important controls are:

| control | meaning | role in this investigation |
| --- | --- | --- |
| `z_W0` | updraft transition/base height | original Berton-relevant 10 km to 9 km screen; locally insensitive on the first physical branch |
| `W_a0` | saturated updraft amplitude | alternate control expected to move the local vertical-force equilibrium |
| `H_a3` | humidity-profile node near 10 km | alternate control expected to affect growth balance and local eigenvalues |
| `eta_blend` | optional humidity/radiation blend parameter | held at canonical no-override setting here |
| `include_coriolis` | Coriolis toggle | held at `0`/false for canonical no-Coriolis classification |

For TASK-012 AUTO conditioning, the mass state was scaled as `U(4)=m/1e-9 kg`; reported diagnostics convert back to physical kg.

## Original `z_W0` equilibrium Hopf screen and why that path was abandoned

The original full-model AUTO test continued an equilibrium branch over the Berton-relevant `z_W0` interval from 10 km through 9 km, with an additional 8.5 km robustness anchor. The checked-in note is `episodes/04-full-model-auto-equilibria/docs/berton_full_auto_task010_continuation.md` and generated outputs are under `episodes/04-full-model-auto-equilibria/outputs/task010/`.

Key result: no AUTO LP, HB, or BP labels were detected on this branch. At the labeled anchors from 10 km through 8.5 km, the branch remained at approximately:

| quantity | value |
| --- | ---: |
| `z*` | `10178.50407189 m` |
| `u*` | `-0.8925203595 m/s` |
| `w*` | `0 m/s` |
| `m*` | `1.0570071795e-9 kg` |
| critical eigenvalue | `+2.38933e-4 s^-1` real |

The independent Python finite-difference cross-check agreed with the AUTO leading eigenvalue. No complex-conjugate pair approached the imaginary axis. Mechanism diagnostics remained effectively constant, including `sigma_S + R_zeta ~= -1.2268e-4 m^-1` and `R ~= 9.2227e-3`.

This path was abandoned as the primary Hopf explanation because it was a continuation of a state insensitive to the chosen control: the equilibrium altitude stayed above the tested `z_W0` values, so the local updraft seen by the equilibrium remained saturated at `W_a0=0.6 m/s`. It therefore did not probe the local conditions controlling the observed oscillatory trajectory.

## Long BDF/LSODA classification of the observed oscillation

TASK-011 directly integrated the canonical oscillatory Case-0 configuration:

- `atmosphere_for_case(0, oscillatory=True)`
- `z_W0=9 km`
- `W_a0=0.6 m/s`
- `H_a3=0.61`
- `eta_override=None`
- `include_coriolis=False`
- initial state from `initial_state_for_case(0)`

Long integrations used SciPy `BDF` and `LSODA` for 500 h, after the documented extension rule found that the required 200 h horizon still had a nonzero envelope. Solver controls were `rtol=1e-7`, componentwise `atol=[1e-2, 1e-2, 1e-5, 1e-5, 1e-16]`, `max_step=600 s`, and sampled output every 10 min.

The classification outputs are in `episodes/05-full-model-oscillatory-orbit/outputs/task011/` and summarized in `episodes/05-full-model-oscillatory-orbit/docs/task011_case0_long_integration.md`.

Key diagnostics:

| method | horizon | z envelope 150-200 h | z envelope 450-500 h | ratio | late period | verdict |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| BDF | 500 h | `19.2083 m` | `0.0092358 m` | `4.808e-4` | `10.2037 h` | damped/equilibrium-like |
| LSODA | 500 h | `19.2082 m` | `0.0092094 m` | `4.795e-4` | `10.1944 h` | damped/equilibrium-like |

BDF/LSODA agreement was strong: the full-run maximum altitude difference was about `0.00649 m`, and the late-window maximum altitude difference was about `4.35e-5 m`.

The refined late-time equilibrium was:

| quantity | value |
| --- | ---: |
| `z_eq` | `9618.027532260936 m` |
| `u_eq` | `1.9098623386953226 m/s` |
| `w_eq` | `-2.9084536311763646e-21 m/s` |
| `m_eq` | `1.0802293920592054e-9 kg` |
| RHS norm | `2.13e-13` |

Finite-difference eigenvalues included a stable complex pair:

| real part | imaginary part | period | e-folding time |
| ---: | ---: | ---: | ---: |
| `-7.06018e-6 s^-1` | `±1.71212e-4 s^-1` | `10.1939 h` | `39.3443 h` |

This pair quantitatively explains the observed decaying oscillation. Because the trajectory settled, the primary continuation artifact exported by TASK-011 was an equilibrium/state seed rather than a sampled periodic orbit.

Important generated artifacts include:

- `case0_bdf_500h.csv`
- `case0_lsoda_500h.csv`
- `case0_long_timeseries.png`
- `case0_late_envelope.png`
- `case0_solver_agreement.png`
- `classification_verdict.json`
- `continuation_equilibrium_seed.csv`
- `continuation_equilibrium_eigenvalues.csv`

## Continuation from the long-integration seed

TASK-012 used the TASK-011 damped/equilibrium-like verdict to initialize equilibrium continuation from the late-time state. Periodic-orbit continuation was not attempted because there was no limit-cycle-like sampled orbit to seed.

The checked-in note is `episodes/06-full-model-auto-seed-continuation/docs/task012_seed_continuation.md`; outputs are in `episodes/06-full-model-auto-seed-continuation/outputs/task012/`.

The current AUTO formulation accepted the seed and reproduced the stable complex pair near:

| Re(lambda) | Im(lambda) | interpretation |
| ---: | ---: | --- |
| `-7.06018e-6 s^-1` | `±1.71213e-4 s^-1` | stable spiral, period about 10.19 h |

The alternate controls were chosen specifically not to repeat the insensitive `z_W0` branch:

- `W_a0`, because it changes the local vertical force balance and equilibrium altitude.
- `H_a3`, because it changes humidity/growth balance and local linear stability.

AUTO runs in both directions failed at the first continuation step after repeated step-size reduction:

| run family | control | accepted non-MX points | accepted control range | failure mode |
| --- | --- | ---: | --- | --- |
| `wA0-plus/minus` | `W_a0` | 1 | `0.6` only | first step retried to minimum-step `MX` |
| `Ha3-plus/minus` | `H_a3` | 1 | `0.61` only | first step retried to minimum-step `MX` |

This is a failure of the present AUTO parameterization/conditioning, not a dynamical indication of a periodic orbit.

To assess whether the controls were nevertheless meaningful, TASK-012 added an independent Python root-continuation probe. This is not an AUTO validation, but it is useful direction finding:

| control | sampled range | result |
| --- | --- | --- |
| `W_a0` | `0.1-1.2 m/s` | equilibrium altitude shifts from about `9596.49 m` to `9651.96 m`; sampled critical real parts remain negative |
| `H_a3` | `0.4-0.85` | critical real part ranges from about `-1.37e-4` to `+1.62e-4 s^-1`, suggesting a possible local stability crossing to revisit with better AUTO scaling |

## Comparison with reduced 3D prediction

The reduced 3D analysis found a corrected Hopf-capable sign structure for the baseline local reduced fixed point, controlled by:

```text
sigma_S + R_zeta = -5.640219674712e-05 m^-1 < 0
```

With the corrected Jacobian, the determinant term is:

```text
a0 = a*c - b*d
```

and the Routh-Hurwitz Hopf condition is:

```text
a2*a1 = a0
```

The reduced baseline is therefore a stable slow spiral with a Hopf-capable sign structure, not a corrected-Jacobian saddle. It predicts that destabilization would require moving the physical operating point toward the Hopf surface, for example through controls that strengthen the relevant feedbacks or alter damping.

The full-model evidence is consistent with the stable-spiral part of that reduced picture but does **not** validate a Hopf in the tested full-model continuation runs:

- The long full-model trajectory settles onto a stable spiral equilibrium.
- The stable full-model complex pair has period about 10.19 h, while the reduced baseline slow pair was about 7.4 h; this is qualitatively similar but quantitatively different.
- The original full-model `z_W0` continuation did not move the local equilibrium conditions and found no Hopf candidate.
- The Python `H_a3` probe suggests a possible stability crossing, but the current AUTO run did not validate it.

Therefore the reduced model should be treated as a mechanism guide, not as proof that Berton's reported full-model oscillation is a local Hopf under the tested controls.

## Mechanism assessment

| candidate explanation | status | evidence |
| --- | --- | --- |
| Local Hopf on original `z_W0` branch | Not supported | AUTO found no HB/LP/BP, no complex pair crossing, branch insensitive to `z_W0` |
| Finite-amplitude periodic orbit/global mechanism | Not supported by current data | BDF/LSODA oscillations decay by about `2,000x`; no periodic seed exported; no PO continuation attempted |
| Damped transient approach to equilibrium | Best supported | 500 h integration envelope collapse, solver agreement, refined equilibrium RHS norm, stable complex eigenpair matching period |
| Different branch/control | Plausible but unvalidated | `H_a3` Python probe suggests a crossing; AUTO conditioning currently prevents accepted nontrivial branch |
| Inconclusive globally | Yes, for the global parameter space | only specific no-Coriolis Case-0 controls have been tested deeply |
| Parameter-dependent scenario | Possible | requires reformulated AUTO validation under `H_a3`, humidity, drag, eta, Coriolis, or other controls |

## Residual numerical risks

- The classification is for the canonical no-Coriolis Case-0 configuration used in these tasks. Coriolis-enabled dynamics may alter horizontal coupling and should not be inferred from the no-Coriolis runs.
- Long integrations are numerical evidence, not a proof of asymptotic convergence, although BDF/LSODA agreement and the local eigenvalues make the damped interpretation strong.
- Finite-difference Jacobians are sensitive to scaling near very small mass residuals. The AUTO seed eigenvalues support the TASK-011 eigenvalue picture, but future branch validation should use better-scaled variables and/or analytic derivatives.
- The first AUTO continuation steps from the TASK-011 seed failed for `W_a0` and `H_a3`; this leaves the alternate-control bifurcation question unresolved.
- The Python root-continuation probe is independent direction-finding, not a substitute for AUTO special-point detection.
- Model-port discrepancies, atmosphere-profile smoothing, or omitted feedbacks could shift the local stability balance.

## Suggested next steps

Given that continuation from the observed oscillatory solution did not produce a periodic-orbit branch and the observed oscillation decays, the most productive next steps are:

1. **Do not continue investing in the original `z_W0` Hopf path** unless the control is reformulated so the updraft transition actually crosses the local equilibrium altitude.
2. **Reformulate the AUTO variables** using log-mass or radius rather than raw/scaled mass, and add analytic `DFDU`/`DFDP` where practical to reduce first-step minimum-step failures.
3. **Retry `H_a3` as the primary Hopf-control candidate** after reformulation, because the Python probe shows the strongest change in critical real part.
4. **Use `W_a0` as a conditioning/control sanity check**, because it smoothly moves the equilibrium altitude while remaining stable in the Python probe.
5. **Only attempt periodic-orbit continuation after a true periodic seed exists**, e.g. from a parameter set where long BDF/LSODA integration remains limit-cycle-like over an extension horizon rather than decaying.
6. **Document any future positive Hopf claim with both AUTO special-point labels and independent eigenvalue cross-checks**, including solver tolerances and branch scaling.

## Final conclusion

The completed full-model investigation does not reproduce Berton's reported oscillatory case as a sustained periodic orbit under the canonical no-Coriolis Case-0 settings. The apparent oscillation is instead explained by decay toward a stable equilibrium with a lightly damped complex mode. The failed AUTO continuation from the long-integration seed is a numerical limitation of the current formulation, not positive evidence for a hidden limit cycle. Further work should target a better-conditioned AUTO reformulation and alternate controls, especially `H_a3`, if the goal is to determine whether a nearby parameter-dependent Hopf exists in the full model.
