from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

EP = Path("episodes/07-restricted-equilibrium-auto")
AUTO = EP / "auto" / "berton_restricted_task019_pmass"
OUT = EP / "outputs" / "task019"
DOC = EP / "docs" / "task019_pmass_wa0_gate.md"
SCRIPT = EP / "scripts" / "berton_restricted_task019_pmass_wa0.py"


def test_task019_pmass_auto_variant_documents_inverse_map() -> None:
    src = (AUTO / "bertonrestricted_task019_pmass.f90").read_text()
    assert "TASK-019 P-scaled restricted/scaled 3D equilibrium gate" in src
    assert "U(3)=P=M/10 where M=log(m/m_seed)" in src
    assert "UU(4)=LOG(m_seed) + 10D0*U(3)" in src
    assert "dM/dP=10 factor" in src

    plus = (AUTO / "c.bertonrestricted-task019-pmass-wA0-plus").read_text()
    minus = (AUTO / "c.bertonrestricted-task019-pmass-wA0-minus").read_text()
    for cfg in (plus, minus):
        assert "P_log_ratio_over_10" in cfg
        assert "ICP = ['W_a0']" in cfg
        assert "JAC=0" in cfg
        assert "ISP=0" in cfg
    assert (AUTO / "b.task019-pmass-wA0-plus").exists()
    assert (AUTO / "d.task019-pmass-wA0-plus").exists()


def test_task019_seed_and_config_crosschecks() -> None:
    seed = pd.read_csv(OUT / "seed_crosscheck.csv").iloc[0]
    assert abs(seed.Z_scaled) < 1e-15
    assert abs(seed.U_scaled) < 1e-15
    assert abs(seed.P_log_ratio_over_10) < 1e-15
    assert abs(seed.M_log_ratio) < 1e-15
    assert seed.scaled_restricted_residual_norm < 1e-7
    assert int(seed.python_probe_seed_stable_eigenvalue_count) == 4

    cfg = pd.read_csv(OUT / "config_summary.csv")
    assert cfg.uses_p_mass_coordinate.all()
    assert not cfg.has_diagnostic_icp.any()
    assert set(cfg.icp) == {"['W_a0']"}


def test_task019_wa0_gate_passes_and_reconstructs_physical_mass() -> None:
    branch = pd.read_csv(OUT / "auto_branch_summary.csv")
    plus = branch[branch.run == "pmass-wA0-plus"]
    assert plus.W_a0.min() == 0.6
    assert plus.W_a0.max() >= 1.2
    assert (abs(plus.W_a0 - 0.6) > 1e-8).sum() > 10
    assert (plus.W_a0.round(6) == 1.2).any()
    assert plus.z_m.max() - plus.z_m.min() > 50.0
    assert (plus.M_log_ratio - 10.0 * plus.P_log_ratio_over_10).abs().max() < 1e-12
    assert plus.m_kg.max() > plus.m_kg.min()

    summary = pd.read_csv(OUT / "wa0_gate_summary.csv").iloc[0]
    assert bool(summary.uses_p_mass_coordinate)
    assert bool(summary.plus_reached_1p2)
    assert bool(summary.gate_passes_for_task020)
    assert int(summary.task017_nontrivial_points) == 0
    assert int(summary.task021_nontrivial_points) == 0
    assert "P=M/10" in summary.verdict


def test_task019_matches_task012_python_probe_at_user_anchors() -> None:
    comparison = pd.read_csv(OUT / "python_probe_comparison.csv")
    assert {0.7, 0.8, 0.9, 1.0, 1.1, 1.2}.issubset(set(comparison.W_a0.round(1)))
    assert comparison.z_abs_error_m.max() < 1e-3
    assert comparison.u_abs_error_m_s.max() < 1e-5
    assert comparison.relative_m_error.max() < 1e-4
    assert (comparison.python_stable_eigenvalue_count == 4).all()
    assert (comparison.python_critical_real_s_inv < 0).all()


def test_task019_doc_and_verdict_clear_task020_gate() -> None:
    verdict = json.loads((OUT / "task019_wa0_gate_verdict.json").read_text())
    assert verdict["task022_arclength_fix"] == "P=M/10"
    assert verdict["gate_passes_for_task020"] is True
    assert verdict["plus_reached_1p2"] is True
    assert "M_log_ratio=10*P_log_ratio_over_10" in verdict["p_to_m_conversion"]

    note = DOC.read_text()
    assert "TASK-019 P-scaled restricted W_a0 gate" in note
    assert "P=M/10" in note
    assert "hit all user anchors through `W_a0=1.2`" in note
    assert "gate **passes**" in note
    assert "Do not reuse the older unscaled `M` coordinate" in note

    src = SCRIPT.read_text()
    assert "m_log_ratio = 10.0 * p_scaled" in src
    assert "m_seed*exp(10P)" in src
