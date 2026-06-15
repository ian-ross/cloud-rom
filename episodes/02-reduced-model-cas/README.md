# Episode 02: Reduced-model CAS analysis

## Research question

What does symbolic and numerical analysis of the reduced Berton 3D fixed point say about Hopf capability, stability, and the mechanism diagnostics controlling oscillations?

## Status / conclusion

The reduced analysis derived the Jacobian/characteristic polynomial, tracked corrected roots, studied the radiative-gradient sign structure, derived a singular perturbation reduction, and classified the baseline fixed point. The synthesis is in `docs/berton_3d_hopf_analysis_summary.md`.

## Key artifacts

- `scripts/berton_3d_hopf_task001_symbolic.py` — symbolic Jacobian and characteristic polynomial.
- `scripts/berton_3d_hopf_task002_rzeta_sign.py` — radiative-gradient sign analysis.
- `scripts/berton_3d_hopf_task003_root_tracking.py` — corrected root tracking across drag rate.
- `scripts/berton_3d_hopf_task004_singular_reduction.py` — singular perturbation reduction.
- `scripts/berton_3d_hopf_task005_classification.py` — baseline Hopf/saddle classification.
- `docs/berton_3d_hopf_analysis_summary.md` — final reduced-analysis summary.
- `docs/berton_3d_hopf_briefing.md` and `docs/berton_3d_hopf_review_checklist.md` — review and briefing material.

## Reproducibility

```bash
uv run pytest \
  tests/test_episode02_reduced_cas_symbolic.py \
  tests/test_episode02_reduced_cas_rzeta_sign.py \
  tests/test_episode02_reduced_cas_root_tracking.py \
  tests/test_episode02_reduced_cas_singular_reduction.py \
  tests/test_episode02_reduced_cas_classification.py \
  tests/test_episode02_reduced_cas_summary.py
```

## Relationship to backlog tasks

Backlog tasks: TASK-001, TASK-002, TASK-003, TASK-004, TASK-005, TASK-006.

## Next questions

The reduced CAS model motivated AUTO validation in Episode 03 and the full-model equilibrium search in Episode 04.
