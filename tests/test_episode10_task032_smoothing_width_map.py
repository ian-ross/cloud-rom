from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

EP = Path("episodes/10-full-model-python-continuation")
SCRIPT_DIR = EP / "scripts"
OUT = EP / "outputs" / "task032"
DOC = EP / "docs" / "task032_smoothing_width_sensitivity.md"
if str(SCRIPT_DIR.resolve()) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR.resolve()))

from berton_full_task032_smoothing_width_map import (  # noqa: E402
    FIXED_Z_ANCHORS_M,
    MAP_Z_ANCHORS_M,
    WIDTH_ANCHORS_M,
    mu_to_width,
    width_to_mu,
)


def test_task032_width_coordinate_round_trips() -> None:
    for width in WIDTH_ANCHORS_M:
        assert abs(mu_to_width(width_to_mu(width)) - width) < 1e-10
    summary = json.loads((OUT / "task032_smoothing_width_verdict.json").read_text())
    assert summary["width_coordinate"] == "mu=log(width_m/50 m)"
    assert summary["width_inverse_mapping"] == "width_m=50*exp(mu)"
    assert summary["z_W0_coordinate"] == "q_z=(z_W0-9000 m)/1000 m"


def test_task032_fixed_z_paths_cover_transition_widths_below_50m() -> None:
    points = pd.read_csv(OUT / "fixed_z_width_continuation_points.csv")
    assert set(points["z_W0_m"]) == set(FIXED_Z_ANCHORS_M)
    assert set(points["smooth_width_m"]) == set(WIDTH_ANCHORS_M)
    assert points["scaled_residual_norm"].max() < 3e-6
    assert (points["smooth_width_m"] < 50.0).any()
    for z in FIXED_Z_ANCHORS_M:
        subset = points[points.z_W0_m == z]
        assert {50.0, 35.0, 25.0, 10.0}.issubset(set(subset.smooth_width_m))


def test_task032_two_parameter_map_records_diagnostics_and_rejections() -> None:
    points = pd.read_csv(OUT / "zw0_width_map_points.csv")
    required = {
        "z_W0_m",
        "smooth_width_m",
        "mu_log_width_over_50m",
        "scaled_residual_norm",
        "state_jacobian_condition",
        "state_jacobian_min_singular_value",
        "width_branch_condition",
        "width_branch_min_singular_value",
        "width_tangent_mu",
        "z_branch_condition",
        "z_tangent_lambda",
        "critical_real_s_inv",
        "stable_eigenvalue_count",
        "updraft_difference_m_s",
    }
    assert required.issubset(points.columns)
    assert set(MAP_Z_ANCHORS_M).issubset(set(points["z_W0_m"]))
    assert {50.0, 35.0, 25.0}.issubset(set(points["smooth_width_m"]))
    assert points["scaled_residual_norm"].max() < 3e-6

    rejected = pd.read_csv(OUT / "zw0_width_map_rejected_points.csv")
    assert {"z_W0_m", "smooth_width_m", "reason", "scaled_residual_norm"}.issubset(rejected.columns)

    eig = pd.read_csv(OUT / "zw0_width_map_eigenvalues.csv")
    assert {"real_s_inv", "imag_s_inv", "z_W0_m", "smooth_width_m"}.issubset(eig.columns)
    assert len(eig) >= 4 * len(points)


def test_task032_verdict_identifies_sharp_limit_not_50m_nonexistence() -> None:
    summary = json.loads((OUT / "task032_smoothing_width_verdict.json").read_text())
    assert summary["classification"] == "near_singular_sharp_limit_not_50m_nonexistence"
    assert 10000.0 in summary["accepted_50m_z_values_m"]
    assert 10000.0 in summary["accepted_below_50m_z_values_m"]
    assert summary["max_state_jacobian_condition"] > 1e8
    assert summary["max_scaled_residual_norm"] < 3e-6

    width_summary = pd.read_csv(OUT / "width_summary.csv")
    cond_50 = float(width_summary.loc[width_summary.smooth_width_m == 50.0, "max_state_jacobian_condition"].iloc[0])
    cond_10 = float(width_summary.loc[width_summary.smooth_width_m == 10.0, "max_state_jacobian_condition"].iloc[0])
    assert cond_10 > 100 * cond_50


def test_task032_doc_is_conservative_and_reproducible() -> None:
    doc = DOC.read_text()
    assert "TASK-032" in doc
    assert "mu=log(width_m/50 m)" in doc
    assert "q_z=(z_W0-9000 m)/1000 m" in doc
    assert "near_singular_sharp_limit_not_50m_nonexistence" in doc
    assert "does not by itself prove a global two-parameter bifurcation diagram" in doc
