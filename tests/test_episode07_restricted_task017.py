from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

EP = Path("episodes/07-restricted-equilibrium-auto")
AUTO = EP / "auto" / "berton_restricted_task017"
SCRIPT = EP / "scripts" / "berton_restricted_task017_wa0_sanity.py"
OUT = EP / "outputs" / "task017"
DOC = EP / "docs" / "task017_wa0_conditioning_sanity_check.md"


def test_task017_restricted_auto_variant_documents_scaled_inverse_map() -> None:
    src = (AUTO / "bertonrestricted_task017.f90").read_text()
    assert "TASK-017 restricted/scaled 3D equilibrium gate" in src
    assert "U(1)=Z=(z-z_seed)/100 m" in src
    assert "U(3)=M=log(m/m_seed)" in src
    assert "UU(3)=0D0" in src
    assert "F(1)=FF(2)/s_du" in src
    assert "F(2)=FF(3)/s_dw" in src
    assert "F(3)=FF(4)/s_dlogm" in src
    assert (AUTO / "c.bertonrestricted-task017-wA0-plus").exists()
    assert (AUTO / "c.bertonrestricted-task017-wA0-minus").exists()


def test_task017_seed_crosscheck_uses_task011_seed_and_scaled_residuals() -> None:
    seed = pd.read_csv(OUT / "seed_restricted_crosscheck.csv").iloc[0]
    assert abs(seed.z_m - 9618.027532260936) < 1e-9
    assert abs(seed.u_m_s - 1.9098623386953226) < 1e-12
    assert abs(seed.M_log_ratio) < 1e-15
    assert seed.raw_restricted_residual_norm < 1e-10
    assert seed.scaled_restricted_residual_norm < 1e-7
    assert seed.residual_scale_du_dt > 1.0
    assert seed.residual_scale_dw_dt > 1.0
    assert 0 < seed.residual_scale_dlogm_dt < 1e-4


def test_task017_python_probe_and_auto_failure_are_compared() -> None:
    probe = pd.read_csv(OUT / "python_wa0_probe_summary.csv").iloc[0]
    assert probe.control_min == 0.1
    assert probe.control_max == 1.2
    assert probe.successful_points >= 20
    assert probe.altitude_span_m > 50.0
    assert bool(probe.all_stable)

    summary = pd.read_csv(OUT / "continuation_conditioning_summary.csv").iloc[0]
    assert summary.python_probe_min == 0.1
    assert summary.python_probe_max == 1.2
    assert summary.auto_control_min == 0.6
    assert summary.auto_control_max == 0.6
    assert int(summary.auto_nontrivial_points) == 0
    assert int(summary.task015_full4d_nontrivial_points) == 0
    assert "broader formulation/conditioning" in summary.conditioning_interpretation
    assert "NaN" in summary.restricted_failure_mode or "DGEBAL" in summary.restricted_failure_mode


def test_task017_verdict_does_not_overstate_h_a3_specificity() -> None:
    verdict = json.loads((OUT / "task017_conditioning_verdict.json").read_text())
    assert verdict["seed_source"] == "TASK-011/TASK-012 equilibrium"
    assert verdict["wA0_python_expected_range_m_s"] == [0.1, 1.2]
    assert verdict["wA0_auto_covered_range_m_s"] == [0.6, 0.6]
    assert verdict["auto_accepted_nontrivial_branch"] is False
    assert "H_a3 failures remain broader formulation/conditioning concerns" in verdict["conditioning_verdict"]

    note = DOC.read_text()
    assert "TASK-017 W_a0 conditioning sanity check" in note
    assert "TASK-012 Python probe follows stable W_a0 equilibria" in note
    assert "only the seed value" in note
    assert "should **not** be interpreted as control-specific Hopf evidence" in note
    assert "DGEBAL/NaN" in note
    assert "Successor addendum: TASK-019 resolves the W_a0 gate" in note
    assert "P=M/10" in note
    assert "the un-fixed `M` coordinate immediately fails after the seed" in note
