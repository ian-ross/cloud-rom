# TASK-017 W_a0 conditioning sanity check

This note uses `W_a0` as a non-Hopf conditioning control for the Berton equilibrium seed. The seed is the TASK-011/TASK-012 stable equilibrium translated into the TASK-018 restricted/scaled coordinates `Z=(z-z_seed)/100 m`, `U=(u-u_seed)/(1 m/s)`, `M=log(m/m_seed)`, with `w=0`.

## Commands and artifacts

```bash
bash episodes/07-restricted-equilibrium-auto/auto/berton_restricted_task017/run_auto.sh
uv run python episodes/07-restricted-equilibrium-auto/scripts/berton_restricted_task017_wa0_sanity.py
```

Curated outputs are in `episodes/07-restricted-equilibrium-auto/outputs/task017/`. Raw AUTO files are saved as `b./s./d.task017-restricted-wA0-{plus,minus}` under `episodes/07-restricted-equilibrium-auto/auto/berton_restricted_task017/`.

## Python expectation

The TASK-012 Python probe follows stable W_a0 equilibria over `0.10`-`1.20` m/s, with altitude moving by `55.473` m and all saved critical real parts negative.

## AUTO result

The restricted/scaled AUTO retry accepted `2` total printed branch points and `0` non-seed/nontrivial points. The covered AUTO W_a0 range is `0.600`-`0.600` m/s, i.e. only the seed value. The diagnostic logs retain DGEBAL/NaN/floating-point failure messages before any user anchor is reached.

## Conditioning verdict

**Verdict:** W_a0 restricted/scaled AUTO still accepts only the seed; H_a3 failures remain broader formulation/conditioning concerns rather than control-specific evidence.

Because the easy W_a0 gate still fails before a nontrivial branch point, current H_a3 failures should **not** be interpreted as control-specific Hopf evidence. They remain evidence of broader AUTO formulation/conditioning or problem-setup fragility despite the Python equilibrium branch being smooth and stable.

Residual risk: the restricted/scaled residual is much better conditioned locally per TASK-018, but the AUTO equilibrium setup still encounters first-step linear-algebra divergence; further work should isolate AUTO arclength/Jacobian scaling details before H_a3 Hopf work.
