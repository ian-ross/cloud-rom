from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

EP = Path("episodes/06-full-model-auto-seed-continuation")
OUT = EP / "outputs" / "task015"
AUTO = EP / "auto" / "berton_full_task015"
DOC = EP / "docs" / "task015_logm_reformulation.md"


def test_task015_logm_auto_formulation_documents_coordinate_and_derivatives() -> None:
    f90 = (AUTO / "bertonfull_logm.f90").read_text()
    assert "U(4)=log(m/kg)" in f90
    assert "f(4)=L%m_dot/MAX(EXP(uvec(4)),1D-300)" in f90
    assert "DFDU(1,3)=1D0" in f90
    assert "DFDP(1:4,k)" in f90

    doc = DOC.read_text()
    assert "U(4) = log_m_kg = log(m / 1 kg)" in doc
    assert "m = exp(U(4)) kg" in doc
    assert "Remaining `DFDU` entries are centered finite differences" in doc
    assert "`DFDP` is populated by centered differences" in doc


def test_task015_seed_translation_crosscheck_matches_python_diagnostics() -> None:
    seed = pd.read_csv(OUT / "seed_logm_crosscheck.csv")
    row = seed.iloc[0]
    assert abs(row["m_kg"] - 1.0802293920592054e-9) < 1e-20
    assert abs(row["log_m_kg"] - (-20.646092418309163)) < 1e-12
    assert row["physical_rhs_norm"] < 1e-10
    assert row["transformed_rhs_norm"] < 1e-10
    assert row["fortran_python_transformed_rhs_max_abs_diff"] < 1e-12
    assert bool(row["physical_eigs_match_transformed"])

    eig = pd.read_csv(OUT / "seed_logm_python_eigenvalues.csv")
    assert (eig["real_s_inv"] < 0).all()
    assert (eig["imag_s_inv"].abs() > 1e-4).any()


def test_task015_wA0_retry_is_compared_to_task012_failures() -> None:
    for name in ["logm-wA0-plus", "logm-wA0-minus"]:
        assert (AUTO / f"b.task015-{name}").exists()
        assert (AUTO / f"s.task015-{name}").exists()
        assert (AUTO / f"d.task015-{name}").exists()

    summary = pd.read_csv(OUT / "continuation_summary.csv")
    assert set(summary["run"]) == {"logm-wA0-plus", "logm-wA0-minus"}
    assert set(summary["control"]) == {"W_a0"}
    assert (summary["auto_accepted_non_mx_points"] == 1).all()
    assert (summary["task012_wA0_min_accepted_non_mx_points"] == 1).all()
    assert summary["task012_failure_reference"].str.contains("Retrying step").all()
    assert summary["main_failure_note"].str.contains("NaN|DGEBAL|Retrying", regex=True).all()

    verdict = json.loads((OUT / "task015_verdict.json").read_text())
    assert verdict["coordinate"] == "log_m_kg = log(m/kg)"
    assert verdict["first_step_control"] == "W_a0"
    assert verdict["accepted_nontrivial_branch"] is False
