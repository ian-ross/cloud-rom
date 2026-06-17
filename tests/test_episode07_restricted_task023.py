from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

EP = Path("episodes/07-restricted-equilibrium-auto")
AUTO = EP / "auto" / "berton_restricted_task023_zw0_smooth"
OUT = EP / "outputs" / "task023"
DOC = EP / "docs" / "task023_zw0_smooth_restricted_verdict.md"
SCRIPT = EP / "scripts" / "berton_restricted_task023_zw0_smooth.py"


def test_task023_auto_source_uses_smoothed_updraft_and_task019_scaling() -> None:
    src = (AUTO / "bertonrestricted_task023_zw0_smooth.f90").read_text()
    assert "TASK-023 smoothed-z_W0 P-scaled restricted/scaled 3D equilibrium continuation" in src
    assert "U(3)=P=M/10 where M=log(m/m_seed)" in src
    assert "UU(4)=LOG(m_seed) + 10D0*U(3)" in src
    assert "softplus_stable" in src
    assert "smooth_clamp01" in src
    assert "PAREFF(1)=9000D0 + 1000D0*PAR(54)" in src
    assert "PAR(56)=50D0" in src

    plus_cfg = (AUTO / "c.bertonrestricted-task023-zw0-smooth-plus").read_text()
    minus_cfg = (AUTO / "c.bertonrestricted-task023-zw0-smooth-minus").read_text()
    for cfg in (plus_cfg, minus_cfg):
        assert "q_z=(z_W0-9000 m)/1000 m" in cfg
        assert "ICP = ['q_zW0_scaled']" in cfg
        assert "P_log_ratio_over_10" in cfg
        assert "softplus" in cfg
        assert "NPAR=98" in cfg
    assert "ISP=2" in minus_cfg


def test_task023_outputs_parse_scaled_zw0_control_and_updraft_diagnostics() -> None:
    branch = pd.read_csv(OUT / "auto_branch_summary.csv")
    assert {"z-plus", "z-minus"}.issubset(set(branch.run))
    assert (branch.z_W0_m - (9000.0 + 1000.0 * branch.q_zW0_scaled)).abs().max() < 1e-6
    assert (branch.M_log_ratio - 10.0 * branch.P_log_ratio_over_10).abs().max() < 1e-12
    assert {"smoothed_W_a_m_s", "piecewise_W_a_m_s", "updraft_difference_m_s", "distance_to_z_W0_m"}.issubset(branch.columns)

    minus = branch[branch.run == "z-minus"]
    assert (minus.z_W0_m <= 7000.0 + 1e-6).any()
    assert len(minus) > 10

    plus = branch[branch.run == "z-plus"]
    assert plus.z_W0_m.max() > 9600.0
    assert plus.z_W0_m.max() < 10000.0
    assert not (branch.type == "HB").any()


def test_task023_python_crosschecks_and_smoothing_samples() -> None:
    seed = pd.read_csv(OUT / "seed_smoothing_crosscheck.csv")
    assert seed.smooth_width_m.iloc[0] == 50.0
    assert abs(seed.updraft_perturbation_m_s.iloc[0]) < 1e-5
    assert seed.scaled_residual_norm_at_piecewise_seed.iloc[0] < 2e-6

    samples = pd.read_csv(OUT / "smoothed_updraft_profile_samples.csv")
    assert samples.smoothed_W_a_m_s.between(-1e-12, 0.60001).all()
    assert samples.updraft_difference_m_s.abs().max() > 1e-4

    diag = pd.read_csv(OUT / "python_residual_eigen_diagnostics.csv")
    assert diag.scaled_restricted_residual_norm.max() < 2e-6
    assert {"full_critical_real_s_inv", "full_critical_imag_s_inv"}.issubset(diag.columns)


def test_task023_verdict_compares_to_prior_tasks_and_is_conservative() -> None:
    verdict = json.loads((OUT / "task023_zw0_verdict.json").read_text())
    assert verdict["uses_task019_scaled_restricted_3d_gate"] is True
    assert verdict["uses_p_mass_coordinate"] is True
    assert verdict["active_control_mapping"] == "q_z=(z_W0-9000 m)/1000 m"
    assert verdict["smoothing_width_m"] == 50.0
    assert verdict["reaches_paper_oscillatory_z_W0_7000m"] is True
    assert verdict["reaches_paper_steady_z_W0_10000m"] is False
    assert verdict["auto_hb_labels"] == 0
    assert "staged full-system attempt" in verdict["verdict"]

    note = DOC.read_text()
    assert "TASK-019 restricted 3D AUTO formulation" in note
    assert "TASK-020 H_a3" in note
    assert "softplus" in note
    assert "no HB" in note

    script = SCRIPT.read_text()
    assert "seed_smoothing_crosscheck.csv" in script
    assert "task023_zw0_verdict.json" in script
