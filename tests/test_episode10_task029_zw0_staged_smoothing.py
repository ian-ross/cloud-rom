from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

EP = Path("episodes/10-full-model-python-continuation")
SCRIPT_DIR = EP / "scripts"
OUT = EP / "outputs" / "task029"
DOC = EP / "docs" / "task029_zw0_staged_smoothing.md"
if str(SCRIPT_DIR.resolve()) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR.resolve()))

from berton_full_task029_zw0_staged_smoothing import (  # noqa: E402
    DELTA_Z_W_M,
    WIDTH_SCHEDULE_M,
    piecewise_updraft_value,
    smoothed_updraft_value,
)


def test_task029_smoothed_updraft_formula_and_mapping_metadata() -> None:
    summary = json.loads((OUT / "task029_zw0_staged_verdict.json").read_text())
    assert summary["coordinate_system"] == "TASK-026 scaled z,u,w,log(m/kg) with q_z=(z_W0-9000 m)/1000 m"
    assert summary["physical_inverse_mapping"] == "z_W0_m = 9000 + 1000*q_z_W0_scaled"
    assert summary["smoothing_width_schedule_m"] == WIDTH_SCHEDULE_M
    assert summary["delta_z_W_m"] == DELTA_Z_W_M
    assert "softplus" in summary["smoothing_formula"]

    assert smoothed_updraft_value(9300.0, 9000.0, width_m=50.0) > 0.59
    assert piecewise_updraft_value(9300.0, 9000.0) == 0.6
    assert smoothed_updraft_value(8500.0, 9000.0, width_m=50.0) < 0.02


def test_task029_curated_outputs_cover_staged_widths_and_transition_region() -> None:
    summary = json.loads((OUT / "task029_zw0_staged_verdict.json").read_text())
    schedule = pd.read_csv(OUT / "smoothing_stage_summary.csv")
    assert sorted(schedule["smooth_width_m"].tolist(), reverse=True) == WIDTH_SCHEDULE_M
    assert (schedule["z_W0_min_m"] <= 7000.0 + 1.0).all()
    assert (schedule["transition_region_points"] > 0).all()

    branch = pd.read_csv(OUT / "full_zw0_staged_unique_points.csv")
    required = {
        "smooth_width_m",
        "z_W0_m",
        "q_z_W0_scaled",
        "z_m",
        "u_m_s",
        "w_m_s",
        "m_kg",
        "physical_residual_norm",
        "scaled_residual_norm",
        "critical_real_s_inv",
        "critical_imag_s_inv",
        "stable_eigenvalue_count",
        "branch_jacobian_condition",
        "smoothed_W_a_m_s",
        "piecewise_W_a_m_s",
        "updraft_difference_m_s",
        "eps_dimensionless",
    }
    assert required.issubset(branch.columns)
    assert set(branch["smooth_width_m"]) == set(WIDTH_SCHEDULE_M)
    assert branch["scaled_residual_norm"].max() < 3e-6

    final = branch[branch["smooth_width_m"] == 50.0]
    assert summary["final_width_z_W0_min_m"] <= 7000.0 + 1.0
    assert summary["final_width_z_W0_max_m"] >= 9900.0
    assert summary["final_width_transition_region_points"] >= 3
    assert {9600.0, 9700.0, 9800.0, 9900.0}.issubset(set(round(v, 6) for v in final.loc[final.run == "anchor", "z_W0_m"]))
    assert abs((final["z_W0_m"] - (9000.0 + 1000.0 * final["q_z_W0_scaled"]))).max() < 1e-8


def test_task029_verdict_distinguishes_smoothing_from_scaling_and_unreached_limit() -> None:
    summary = json.loads((OUT / "task029_zw0_staged_verdict.json").read_text())
    assert summary["final_width_covers_7_10_km"] is False
    assert summary["final_width_z_W0_max_m"] < 10000.0
    assert summary["fragility_classification"] == "smoothing_or_nonsmoothness_sensitive"
    assert "Easier smoothing widths reach farther" in summary["fragility_reason"]
    assert summary["max_scaled_residual_norm"] < 3e-6

    rejected = pd.read_csv(OUT / "full_zw0_staged_rejected_steps.csv")
    assert not rejected.empty
    assert (rejected["smooth_width_m"] == 50.0).any()
    assert rejected.loc[rejected["smooth_width_m"] == 50.0, "start_z_W0_m"].max() > 9900.0


def test_task029_doc_records_reproducible_conservative_result() -> None:
    doc = DOC.read_text()
    assert "TASK-029" in doc
    assert "q_z=(z_W0-9000 m)/1000 m" in doc
    assert "softplus" in doc
    assert "50 m" in doc
    assert "smoothing_or_nonsmoothness_sensitive" in doc
    assert "9.6--10 km" in doc
