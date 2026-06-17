from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EP = ROOT / "episodes" / "09-full-model-auto-zw0"
OUT = EP / "outputs" / "task024"
AUTO = EP / "auto" / "berton_full_task024_zw0_smooth"
DOC = EP / "docs" / "task024_full_zw0_smooth_verdict.md"


def test_task024_artifacts_exist() -> None:
    required = [
        AUTO / "bertonfull_task024_zw0_smooth.f90",
        AUTO / "run_auto.sh",
        AUTO / "b.task024-full-zw0-smooth-plus",
        AUTO / "b.task024-full-zw0-smooth-minus",
        AUTO / "d.task024-full-zw0-smooth-plus",
        AUTO / "d.task024-full-zw0-smooth-minus",
        OUT / "auto_branch_summary.csv",
        OUT / "auto_convergence_notes.csv",
        OUT / "auto_eigenvalue_diagnostics.csv",
        OUT / "config_summary.csv",
        OUT / "python_full_eigenvalue_crosscheck.csv",
        OUT / "python_full_eigenvalues.csv",
        OUT / "task024_full_zw0_verdict.json",
        DOC,
    ]
    for path in required:
        assert path.exists(), path


def test_task024_smoothing_scaling_and_control_are_documented() -> None:
    source = (AUTO / "bertonfull_task024_zw0_smooth.f90").read_text()
    assert "smooth_clamp01" in source
    assert "eps=50/Delta_z_W" in DOC.read_text()
    assert "U(1)=Z=(z-z_seed)/1000" in source
    assert "U(4)=P=(log(m/m_seed))/10" in source
    assert "PAR(96)=q_z=(z_W0-9000 m)/1000 m" in source

    cfg = pd.read_csv(OUT / "config_summary.csv")
    assert set(cfg["run"]) == {"z-plus", "z-minus"}
    assert cfg["control_scaling"].str.contains("q_z=(z_W0-9000 m)/1000 m", regex=False).all()
    assert cfg["smoothed_updraft"].str.contains("width 50 m", regex=False).all()
    assert cfg["physical_inverse"].str.contains("m_seed*exp(10P)", regex=False).all()


def test_task024_bidirectional_attempt_and_range_failure_are_curated() -> None:
    branch = pd.read_csv(OUT / "auto_branch_summary.csv")
    summary = pd.read_csv(OUT / "zw0_full_verdict_summary.csv")
    notes = pd.read_csv(OUT / "auto_convergence_notes.csv")
    assert set(branch["direction"]) == {"upward", "downward"}
    assert set(summary["direction"]) == {"upward", "downward"}
    assert branch["z_W0_m"].between(8999.999, 9000.001).all()
    assert not summary["has_auto_hopf_label"].any()
    assert not summary["reached_paper_7km"].any()
    assert not summary["reached_transition_9p6_10km"].any()
    assert notes["message"].str.contains("No convergence|DGEBAL|floating-point|illegal", regex=True).any()


def test_task024_python_crosscheck_and_conservative_verdict() -> None:
    diag = pd.read_csv(OUT / "python_full_eigenvalue_crosscheck.csv")
    assert {7000, 9000, 9500, 9700, 10000}.issubset(set(diag["z_W0_m"].round().astype(int)))
    assert diag["source"].str.contains("diagnostic", case=False).any() or DOC.read_text().lower().count("diagnostic") >= 1
    assert diag.loc[diag["z_W0_m"].round().astype(int) == 7000, "full_rhs_norm"].iloc[0] < 1e-9
    assert diag.loc[diag["z_W0_m"].round().astype(int) == 9700, "critical_real_s_inv"].iloc[0] > 0

    verdict = json.loads((OUT / "task024_full_zw0_verdict.json").read_text())
    assert verdict["has_auto_supported_hopf"] is False
    assert verdict["smoothing_width_m"] == 50.0
    assert "inconclusiveness" in verdict["verdict"]

    doc = DOC.read_text()
    assert "not AUTO-supported evidence" in doc
    assert "not a mathematically clean negative result" in doc
    assert "should not be attempted" in doc
