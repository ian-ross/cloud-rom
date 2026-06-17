from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EP = ROOT / "episodes" / "08-full-model-auto-ha3"
OUT = EP / "outputs" / "task016"
AUTO = EP / "auto" / "berton_full_task016_ha3_scaled"
DOC = EP / "docs" / "task016_full_ha3_scaled_verdict.md"


def test_task016_artifacts_exist_and_use_distinct_episode() -> None:
    required = [
        AUTO / "bertonfull_task016_ha3_scaled.f90",
        AUTO / "run_auto.sh",
        AUTO / "b.task016-full-ha3-q-plus",
        AUTO / "b.task016-full-ha3-q-minus",
        AUTO / "d.task016-full-ha3-q-plus",
        AUTO / "d.task016-full-ha3-q-minus",
        OUT / "auto_branch_summary.csv",
        OUT / "auto_convergence_notes.csv",
        OUT / "auto_eigenvalue_diagnostics.csv",
        OUT / "config_summary.csv",
        OUT / "python_full_eigenvalue_crosscheck.csv",
        OUT / "python_suspected_crossing_crosscheck.csv",
        OUT / "task016_full_ha3_verdict.json",
        DOC,
    ]
    for path in required:
        assert path.exists(), path


def test_task016_scaling_and_seed_mapping_are_documented() -> None:
    source = (AUTO / "bertonfull_task016_ha3_scaled.f90").read_text()
    assert "U(1)=Z=(z-z_seed)/1000" in source
    assert "U(4)=P=(log(m/m_seed))/10" in source
    assert "PAR(96)=q_H=(H_a3-0.61)/0.001" in source
    assert "m=m_seed*exp(10P)" in source

    cfg = pd.read_csv(OUT / "config_summary.csv")
    assert set(cfg["run"]) == {"q-plus", "q-minus"}
    assert cfg["contains_canonical_H_a3_0_61"].all()
    assert cfg["control_scaling"].str.contains(r"q_H=\(H_a3-0.61\)/0.001", regex=True).all()
    assert cfg["physical_inverse"].str.contains(r"m_seed\*exp\(10P\)", regex=True).all()


def test_task016_bidirectional_attempt_and_failure_range_are_curated() -> None:
    branch = pd.read_csv(OUT / "auto_branch_summary.csv")
    summary = pd.read_csv(OUT / "ha3_full_verdict_summary.csv")
    notes = pd.read_csv(OUT / "auto_convergence_notes.csv")
    assert set(branch["direction"]) == {"upward", "downward"}
    assert set(summary["attempted_direction"]) == {"upward", "downward"}
    assert branch["H_a3"].between(0.609999, 0.610001).all()
    assert not summary["has_auto_hopf_label"].any()
    assert notes["message"].str.contains("NaN|DGEBAL|Retrying step|floating-point", regex=True).any()


def test_task016_python_crosscheck_and_conservative_verdict() -> None:
    diag = pd.read_csv(OUT / "python_full_eigenvalue_crosscheck.csv")
    assert not diag.empty
    assert (diag["full_rhs_norm"] < 1e-10).all()
    assert (diag["stable_eigenvalue_count"] == 4).all()
    assert (diag["critical_real_s_inv"] < 0).all()

    crossing = pd.read_csv(OUT / "python_suspected_crossing_crosscheck.csv")
    assert {0.6, 0.61, 0.625, 0.65}.issubset(set(crossing["H_a3"].round(3)))
    assert crossing.loc[crossing["H_a3"] == 0.6, "critical_real_s_inv"].iloc[0] < 0
    assert crossing.loc[crossing["H_a3"] == 0.65, "critical_real_s_inv"].iloc[0] > 0
    assert crossing["interpretation"].str.contains("not an accepted AUTO branch point").all()

    verdict = json.loads((OUT / "task016_full_ha3_verdict.json").read_text())
    assert verdict["seed_source"] == "TASK-011/TASK-012 equilibrium seed"
    assert verdict["canonical_H_a3_included"] is True
    assert verdict["accepted_non_seed_points"] == 0
    assert verdict["auto_hopf_validated"] is False
    assert "negative/inconclusive" in verdict["verdict"]
    assert verdict["zW0_ready"] is False

    doc = DOC.read_text()
    assert "does **not** provide an AUTO-validated full-system Hopf candidate" in doc
    assert "Python/restricted numerical hint only" in doc
    assert "python_suspected_crossing_crosscheck.csv" in doc
    assert "branch fails before reaching the Python-predicted `H_a3≈0.62`" in doc
