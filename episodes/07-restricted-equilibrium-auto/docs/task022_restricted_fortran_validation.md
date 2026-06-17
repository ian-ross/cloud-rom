# TASK-022 restricted Fortran validation and local surrogate

This note validates the failing TASK-017 restricted/scaled AUTO Fortran source outside AUTO and adds the local affine surrogate proposed after TASK-021.

## Commands

```bash
uv run python episodes/07-restricted-equilibrium-auto/scripts/berton_restricted_task022_validate_fortran.py
uv run pytest tests/test_episode07_restricted_task022.py
```

The script compiles `episodes/07-restricted-equilibrium-auto/auto/berton_restricted_task017/bertonrestricted_task017.f90` with a generated standalone driver under `auto/berton_restricted_task022_validate/`. It calls `STPNT`, `FUNC(..., IJAC=2, ...)`, and `PVLS` at the seed, a local tangent predictor point, and TASK-012 W_a0 probe equilibria at 0.5, 0.7, and 1.0 m/s.

## Validation result

- Samples validated: `5`.
- Max Fortran/Python residual absolute error: `7.362e-08`.
- Max DFDU absolute error: `3.596e-06`.
- Max DFDP absolute error for W_a0/z_W0/H_a3: `9.524e-05`.
- Max selected PVLS diagnostic absolute error: `6.161e-07`.

These checks make residual mismatch, the validated DFDU entries, active DFDP parameter indexing, and selected physical PVLS diagnostics unlikely explanations for the first-step AUTO failure.

## Local tangent and affine surrogate

The affine surrogate based on the seed matrices accepted `180` branch rows and covered `W_a0=0.600`-`1.663`. That means AUTO can continue the local linearized restricted problem with the same state coordinates and W_a0 control.

## Conclusion

The restricted sandbox is still useful, but the next experiment should target the nonlinear corrector path, not PVLS or basic residual/Jacobian indexing. The most plausible remaining causes are nonlinear Berton residual/arclength interaction, step/tangent scaling for the nonlinear restricted problem, or finite-difference behavior after Newton iterates jump far from the local branch. A practical next step is to make AUTO follow the nonlinear problem with an explicitly scaled W_a0 control or externally seeded small predictor steps, then compare each Newton iterate against the validated local tangent.

## Follow-up arclength scaling fix

A follow-up scratch AUTO test found a concrete scaling fix for the nonlinear restricted `W_a0` branch.  The problematic coordinate is the log-mass displacement

```fortran
U(3)=M=log(m/m_seed)
UU(4)=LOG(m_seed) + U(3)
```

The TASK-022 local tangent shows this coordinate dominates the arclength geometry:

```text
dZ/dW_a0 =  0.4378165
dU/dW_a0 = -0.2189083
dM/dW_a0 =  3.0862972
```

Rescaling only the AUTO mass coordinate to

```fortran
U(3)=P=M/10
UU(4)=LOG(m_seed) + 10D0*U(3)
```

keeps the same physical residual while reducing the mass direction's contribution to AUTO's arclength norm.  In the scratch test, the restricted nonlinear `W_a0` continuation no longer failed at the first correction and accepted nontrivial branch points through the `W_a0=1.2` target:

```text
PT 10  W_a0≈0.651
PT 20  W_a0≈0.815
PT 30  W_a0≈0.982
PT 40  W_a0≈1.141
UZ 44  W_a0=1.200
```

TASK-019 should therefore implement the curated fix as a new artifact rather than continuing from the older TASK-017/TASK-021 `M` coordinate.  Required implementation details:

- Use `P=M/10` as the AUTO state and reconstruct physical mass with `m=m_seed*exp(10P)`.
- Update `unames`, parser outputs, docs, and tests to report both `P` and reconstructed `M`/`m`.
- Apply the chain-rule factor of 10 to any supplied `DFDU(:,3)` or choose `JAC=0` first and document AUTO finite differences in the `P` coordinate.
- Treat this fixed `W_a0` branch as the gate that TASK-020 must pass before any `H_a3` Hopf-control verdict.
