# TASK-012 continuation from TASK-011 long-integration seed

## Command

Notebook entry point:

```bash
# Open/run cells in:
episodes/06-full-model-auto-seed-continuation/notebooks/task012_seed_continuation.ipynb
```

Equivalent non-interactive reproduction from the repository root:

```bash
bash episodes/06-full-model-auto-seed-continuation/auto/berton_full_task012/run_auto.sh
uv run python episodes/06-full-model-auto-seed-continuation/scripts/berton_full_task012_seed_continuation.py
```

## TASK-011 seed review

TASK-011 classified canonical no-Coriolis Case 0 as **damped/equilibrium-like**, not limit-cycle-like. Therefore TASK-012 did not attempt periodic-orbit continuation from a sampled orbit. The continuation basis is the exported equilibrium seed:

| seed type | z [m] | u [m/s] | w [m/s] | m [kg] | RHS norm |
| --- | ---: | ---: | ---: | ---: | ---: |
| late-time equilibrium estimate | 9618.027532260936 | 1.9098623386953226 | -2.9084536311763646e-21 | 1.0802293920592054e-09 | 2.1319370397478602e-13 |

The AUTO `STPNT` uses canonical oscillatory Case-0 parameters: `z_W0=9000 m`, `W_a0=0.6 m/s`, `H_a3=0.61`, `eta_blend=0`, `include_coriolis=0`. To improve AUTO conditioning, the AUTO state stores `U(4)=m/1e-9 kg`; diagnostics and the Python probe report physical kg.

## Continuation controls

The previous z_W0 continuation was locally insensitive, so TASK-012 uses controls expected to affect the local equilibrium:

- `W_a0`: updraft amplitude; changes the local vertical force balance and equilibrium altitude.
- `H_a3`: humidity profile node at 10 km; changes growth balance and local linear stability near the seed.

AUTO runs were attempted in both directions for each control:

- `task012-wA0-plus`, `task012-wA0-minus`
- `task012-Ha3-plus`, `task012-Ha3-minus`

## AUTO result

AUTO accepted the TASK-011 seed and reported the same stable complex pair found in TASK-011:

| Re(lambda) [s^-1] | Im(lambda) [s^-1] | interpretation |
| ---: | ---: | --- |
| -7.06018e-06 | ±1.71213e-04 | stable spiral, period ≈ 10.19 h, e-folding ≈ 39.34 h |

However, the first continuation step for each `W_a0`/`H_a3` direction repeatedly retried down to `DSMIN` and ended at `MX`/minimum-step failure. Thus the AUTO parameter range actually accepted is the seed value only:

| run | control | accepted non-MX points | control range | main failure |
| --- | --- | ---: | --- | --- |
| `wA0-plus` | `W_a0` | 1 | 0.6 to 0.6 | retrying step; no convergence with minimum step size |
| `wA0-minus` | `W_a0` | 1 | 0.6 to 0.6 | retrying step; no convergence with minimum step size |
| `Ha3-plus` | `H_a3` | 1 | 0.61 to 0.61 | retrying step; no convergence with minimum step size |
| `Ha3-minus` | `H_a3` | 1 | 0.61 to 0.61 | retrying step; no convergence with minimum step size |

Saved AUTO diagnostics:

- `outputs/task012/auto_branch_summary.csv`
- `outputs/task012/auto_eigenvalue_diagnostics.csv`
- `outputs/task012/auto_convergence_notes.csv`
- raw AUTO files under `auto/berton_full_task012/b.*`, `s.*`, and `d.*`

## Independent equilibrium-control probe

Because AUTO did not take a successful first continuation step, the diagnostic script also performs a Python root-continuation probe using the same full-model RHS and finite-difference Jacobian. This is not a replacement for a successful AUTO branch, but it checks whether the selected controls actually affect local equilibrium diagnostics.

| control | range | points | max RHS norm | critical Re(lambda) range [s^-1] | result |
| --- | --- | ---: | ---: | ---: | --- |
| `W_a0` | 0.1–1.2 m/s | 23 | 5.02e-11 | -2.2e-05 to -1.0e-06 | equilibrium altitude shifts from 9596.49 m to 9651.96 m; all sampled points stable |
| `H_a3` | 0.4–0.85 | 19 | 6.86e-13 | -1.37e-04 to +1.62e-04 | seed-local equilibrium residual remains small; critical pair crosses positive real part above ~0.61 |

Plot/table:

- `outputs/task012/python_equilibrium_control_probe.csv`
- `outputs/task012/python_equilibrium_control_probe.png`

## Interpretation

- The TASK-011 oscillation remains best explained as a stable spiral transient at the exported equilibrium seed, not a finite-amplitude periodic orbit.
- The AUTO failure is a numerical/conditioning obstacle at the first parameter step, not evidence of a periodic orbit.
- `W_a0` is a useful local-equilibrium control: the Python probe moves the equilibrium over a finite altitude range while retaining stable eigenvalues.
- `H_a3` strongly affects local stability diagnostics and may be the better follow-up control for a Hopf-focused search, but the current AUTO formulation needs a better-scaled state/parameterization or analytic parameter derivatives before treating that crossing as an AUTO-validated special point.

## Residual risks and follow-up

- AUTO did not produce an accepted nontrivial branch from the seed; only the seed eigenvalues and failure diagnostics are AUTO-validated here.
- The Python probe uses independent root solves and finite-difference eigenvalues. It is useful for direction finding but does not replace AUTO special-point detection.
- The scaled AUTO mass state improves state conditioning but the first continuation step still fails, likely due parameter/state scaling and finite-difference sensitivity around very small mass-growth residuals.
- A follow-up should reformulate AUTO variables more aggressively (e.g. log-mass or radius rather than mass, plus explicit analytic `DFDP`) and retry `H_a3` as the primary Hopf-control candidate.
