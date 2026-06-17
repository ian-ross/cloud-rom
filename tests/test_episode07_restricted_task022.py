from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

EP = Path("episodes/07-restricted-equilibrium-auto")
SCRIPT = EP / "scripts" / "berton_restricted_task022_validate_fortran.py"
OUT = EP / "outputs" / "task022"
DOC = EP / "docs" / "task022_restricted_fortran_validation.md"
LINEAR = EP / "auto" / "berton_restricted_task022_linear_surrogate"


def test_task022_script_documents_standalone_fortran_driver_calls() -> None:
    src = SCRIPT.read_text()
    assert "bertonrestricted_task017.f90" in src
    assert "task022_driver.f90" in src
    assert "CALL STPNT(ndim,U,PAR,0D0)" in src
    assert "CALL FUNC(ndim,U,ICP,PAR,2,F,DFDU,DFDP)" in src
    assert "CALL PVLS(ndim,U,PAR)" in src
    assert "gfortran" in src


def test_task022_validation_samples_cover_seed_predictor_and_task012_probes() -> None:
    samples = pd.read_csv(OUT / "validation_samples.csv")
    assert set(samples["sample"]) == {
        "seed",
        "tangent_predictor_W0p601",
        "task012_probe_W0p5",
        "task012_probe_W0p7",
        "task012_probe_W1p0",
    }
    assert set(samples.W_a0.round(3)) == {0.5, 0.6, 0.601, 0.7, 1.0}

    tangent = pd.read_csv(OUT / "seed_implicit_tangent.csv")
    assert set(tangent.state) == {"Z_scaled", "U_scaled", "M_log_ratio"}
    assert tangent.dstate_dW_a0.abs().max() > 1.0

    tangent_check = pd.read_csv(OUT / "local_tangent_check.csv")
    assert set(tangent_check.target_W_a0.round(2)) == {0.55, 0.65}
    assert tangent_check.abs_error.max() < 0.01


def test_task022_residual_jacobian_dfdp_and_pvls_comparisons_are_tight() -> None:
    residual = pd.read_csv(OUT / "residual_comparison.csv")
    assert residual["sample"].nunique() == 5
    assert residual.abs_error.max() < 1e-6
    probe_residuals = residual[residual["sample"].str.startswith("task012_probe")]
    assert probe_residuals["fortran"].abs().max() < 1e-6

    dfdu = pd.read_csv(OUT / "dfdu_comparison.csv")
    assert dfdu["sample"].nunique() == 5
    assert dfdu.abs_error.max() < 1e-5

    dfdp = pd.read_csv(OUT / "dfdp_comparison.csv")
    assert set(dfdp.parameter) == {"W_a0", "z_W0", "H_a3"}
    assert dfdp.abs_error.max() < 1e-3

    pvls = pd.read_csv(OUT / "pvls_comparison.csv")
    assert {"z_phys", "u_phys", "m_phys", "W_a", "U_a", "S_i", "eta", "Re", "k"}.issubset(set(pvls.diagnostic))
    assert pvls.abs_error.max() < 1e-5


def test_task022_linear_surrogate_continues_beyond_python_probe_range() -> None:
    branch = pd.read_csv(OUT / "linear_surrogate_branch_summary.csv")
    assert branch.W_a0.min() == 0.6
    assert branch.W_a0.max() >= 1.2
    assert len(branch) > 20
    assert (LINEAR / "bertonrestricted_task022_linear.f90").exists()
    assert (LINEAR / "c.bertonrestricted-task022-linear-wA0-plus").exists()
    assert (LINEAR / "b.task022-linear-wA0-plus").exists()


def test_task022_verdict_rules_out_basic_callback_mismatches() -> None:
    verdict = json.loads((OUT / "validation_verdict.json").read_text())
    assert verdict["samples_validated"] == 5
    assert verdict["residual_mismatch_plausible"] is False
    assert verdict["dfdu_mismatch_plausible"] is False
    assert verdict["dfdp_indexing_mismatch_plausible"] is False
    assert verdict["pvls_selected_mismatch_plausible"] is False
    assert verdict["linear_surrogate_auto_setup_ok"] is True
    assert "nonlinear Berton residual/arclength corrector interaction" in verdict["remaining_plausible_failure_modes"]
    assert "generic AUTO inability to continue the local affine restricted problem" in verdict["less_plausible_failure_modes"]

    note = DOC.read_text()
    assert "TASK-022 restricted Fortran validation and local surrogate" in note
    assert "FUNC(..., IJAC=2" in note
    assert "affine surrogate" in note
    assert "next experiment should target the nonlinear corrector path" in note
