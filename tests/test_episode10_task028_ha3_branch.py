from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

EP = Path("episodes/10-full-model-python-continuation")
SCRIPT_DIR = EP / "scripts"
OUT = EP / "outputs" / "task028"
DOC = EP / "docs" / "task028_ha3_full_model_branch.md"
if str(SCRIPT_DIR.resolve()) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR.resolve()))

from berton_full_task028_ha3_branch import Ha3Config, run_ha3_branch  # noqa: E402


def test_task028_run_ha3_branch_covers_suspected_region() -> None:
    run = run_ha3_branch(Ha3Config(ds_initial=0.20, ds_max=0.35))
    branch = run["comparison_branch"]
    assert branch.H_a3.min() <= 0.6001
    assert branch.H_a3.max() >= 0.65 - 1e-6
    assert branch.scaled_residual_norm.max() < 2e-6
    assert {2, 4}.issubset(set(branch.stable_eigenvalue_count))


def test_task028_curated_outputs_record_branch_eigen_diagnostics_and_verdict() -> None:
    summary = json.loads((OUT / "task028_ha3_branch_verdict.json").read_text())
    assert summary["covers_suspected_0_61_to_0_65_region"] is True
    assert summary["verdict"] == "no_hopf_but_stability_transition"
    assert summary["candidate_hopf_crossing"]["found"] is False
    assert summary["stability_transition"]["found"] is True
    assert summary["max_scaled_residual_norm"] < 2e-6
    assert summary["max_physical_residual_norm"] < 1e-8
    assert summary["independent_eigen_check_max_abs_delta_pair_real_s_inv"] < 1e-12

    branch = pd.read_csv(OUT / "full_ha3_branch_points.csv")
    required = {
        "physical_residual_norm",
        "scaled_residual_norm",
        "critical_real_s_inv",
        "critical_imag_s_inv",
        "stable_eigenvalue_count",
        "complex_pair_count",
        "tracked_pair_real_s_inv",
        "tracked_pair_imag_abs_s_inv",
        "branch_jacobian_condition",
    }
    assert required.issubset(branch.columns)
    assert branch["scaled_residual_norm"].max() < 2e-6
    assert {"upward", "downward", "anchor"}.issubset(set(branch["run"]))

    eig = pd.read_csv(OUT / "full_ha3_eigenvalues.csv")
    assert {"real_s_inv", "imag_s_inv", "H_a3"}.issubset(eig.columns)
    assert len(eig) >= 4 * branch[["run", "step_index"]].drop_duplicates().shape[0]

    independent = pd.read_csv(OUT / "independent_eigen_check.csv")
    assert independent["delta_vs_branch_tracked_pair_real_s_inv"].abs().max() < 1e-12


def test_task028_doc_distinguishes_non_hopf_transition_from_numerical_limit() -> None:
    doc = DOC.read_text()
    assert "TASK-028 follows the full four-dimensional" in doc
    assert "No Hopf-style complex-pair sign crossing" in doc
    assert "non-Hopf stability-count transition" in doc
    assert "Rejected corrector steps" in doc
    assert "Finite-difference Jacobian robustness check" in doc
    assert "trusted scales supporting a Hopf-style complex-pair sign crossing: `False`" in doc


def test_task028_fd_jacobian_robustness_outputs_support_conservative_verdict() -> None:
    summary = json.loads((OUT / "fd_jacobian_robustness_summary.json").read_text())
    assert summary["trusted_scales_support_hopf_like_complex_sign_change"] is False
    assert summary["all_trusted_scales_show_stable_count_transition"] is True
    assert summary["any_tested_scale_supports_hopf_like_complex_sign_change"] is True

    rows = pd.read_csv(OUT / "fd_jacobian_robustness.csv")
    assert {"fd_step_scale", "H_a3", "stable_eigenvalue_count", "complex_pair_count", "tracked_pair_real_s_inv"}.issubset(rows.columns)
    trusted = rows[rows.fd_step_scale <= 10.0]
    assert set(trusted.stable_eigenvalue_count) == {2, 4}
    assert not summary["trusted_scales_support_hopf_like_complex_sign_change"]
