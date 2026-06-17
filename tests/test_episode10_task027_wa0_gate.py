from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

EP = Path("episodes/10-full-model-python-continuation")
SCRIPT_DIR = EP / "scripts"
OUT = EP / "outputs" / "task027"
DOC = EP / "docs" / "task027_wa0_full_model_gate.md"
if str(SCRIPT_DIR.resolve()) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR.resolve()))

from berton_full_task027_wa0_gate import GateConfig, run_gate  # noqa: E402


def test_task027_run_gate_reaches_required_wa0_anchors() -> None:
    run = run_gate(GateConfig(ds_initial=0.20, ds_max=0.35))
    anchors = run["anchor_reachability"]
    assert anchors["reachable"].all()
    assert set(np.round(anchors["W_a0"], 1)) == set(np.round(np.arange(0.1, 1.21, 0.1), 1))
    assert anchors.loc[np.isclose(anchors.W_a0, 1.2), "nearest_abs_delta_W_a0_m_s"].iloc[0] < 1e-10
    assert run["comparison_branch"].W_a0_m_s.min() <= 0.1 + 1e-9
    assert run["comparison_branch"].W_a0_m_s.max() >= 1.2 - 1e-9


def test_task027_curated_outputs_record_residuals_eigenvalues_conditioning_and_verdict() -> None:
    summary = json.loads((OUT / "task027_wa0_gate_verdict.json").read_text())
    assert summary["verdict"] == "pass"
    assert summary["reaches_W_a0_1_2_m_s"] is True
    assert summary["max_scaled_residual_norm"] < 2e-6
    assert summary["max_physical_residual_norm"] < 1e-8
    assert summary["max_branch_jacobian_condition"] > 1.0

    branch = pd.read_csv(OUT / "full_wa0_branch_points.csv")
    required = {
        "physical_residual_norm",
        "scaled_residual_norm",
        "critical_real_s_inv",
        "critical_imag_s_inv",
        "branch_jacobian_condition",
        "branch_min_singular_value",
    }
    assert required.issubset(branch.columns)
    assert (branch["m_kg"] > 0.0).all()
    assert branch["scaled_residual_norm"].max() < 2e-6
    assert {"upward", "downward", "anchor"}.issubset(set(branch["run"]))

    eig = pd.read_csv(OUT / "full_wa0_eigenvalues.csv")
    assert len(eig) >= 4 * branch[["run", "step_index"]].drop_duplicates().shape[0]
    assert {"real_s_inv", "imag_s_inv", "W_a0_m_s"}.issubset(eig.columns)

    iterations = pd.read_csv(OUT / "full_wa0_corrector_iterations.csv")
    assert {"residual_norm", "correction_norm", "jacobian_condition", "linear_solver"}.issubset(iterations.columns)


def test_task027_comparisons_document_previous_probe_and_restricted_geometry() -> None:
    py = pd.read_csv(OUT / "python_probe_comparison.csv")
    assert py["reachable"].all()
    assert py["z_abs_error_vs_task012_m"].dropna().max() < 1e-6
    assert py["relative_m_error_vs_task012"].dropna().max() < 1e-9

    restricted = pd.read_csv(OUT / "restricted_task019_comparison.csv")
    assert restricted["z_abs_error_vs_task019_restricted_m"].dropna().max() < 1e-4
    assert restricted["relative_m_error_vs_task019_restricted"].dropna().max() < 1e-5

    doc = DOC.read_text()
    assert "TASK-027 applies the TASK-026" in doc
    assert "Against the previous TASK-012 Python" in doc
    assert "Against the restricted TASK-019" in doc
    assert "The W_a0 gate **passes**" in doc
