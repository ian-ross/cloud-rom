from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

EP = Path("episodes/07-restricted-equilibrium-auto")
AUTO_Q = EP / "auto" / "berton_restricted_task020_ha3_scaled"
AUTO_H = EP / "auto" / "berton_restricted_task020_ha3_hscaled"
OUT = EP / "outputs" / "task020"
DOC = EP / "docs" / "task020_ha3_scaled_restricted_verdict.md"
SCRIPT = EP / "scripts" / "berton_restricted_task020_ha3_scaled.py"


def test_task020_auto_sources_use_task019_gate_and_scaled_ha3_control() -> None:
    src = (AUTO_Q / "bertonrestricted_task020_ha3_scaled.f90").read_text()
    assert "TASK-020 P-scaled restricted/scaled 3D H_a3 continuation" in src
    assert "U(3)=P=M/10 where M=log(m/m_seed)" in src
    assert "PAR(54)=q_H=(H_a3-0.61)/0.001" in src
    assert "PAREFF(4)=H_ref + H_scale*PAR(54)" in src
    assert "UU(4)=LOG(m_seed) + 10D0*U(3)" in src

    plus_cfg = (AUTO_Q / "c.bertonrestricted-task020-ha3-q-plus").read_text()
    minus_cfg = (AUTO_Q / "c.bertonrestricted-task020-ha3-q-minus").read_text()
    for cfg in (plus_cfg, minus_cfg):
        assert "q_H=(H_a3-0.61)/0.001" in cfg
        assert "ICP = ['q_H_scaled']" in cfg
        assert "P_log_ratio_over_10" in cfg
        assert "NPAR=98" in cfg
    assert "ISP=2" in minus_cfg  # the downward run requested LP/HB/BP detection.

    hsrc = (AUTO_H / "bertonrestricted_task020_ha3_hscaled.f90").read_text()
    assert "ZH=(z-z_seed)/1000" in hsrc
    assert "UH=(u-u_seed)/(5 m/s)" in hsrc


def test_task020_branch_outputs_parse_scaled_control_and_labels() -> None:
    branch = pd.read_csv(OUT / "auto_branch_summary.csv")
    assert {"q-plus", "q-minus", "hscaled-plus", "hscaled-minus"}.issubset(set(branch.run))
    assert (branch.H_a3 - (0.61 + 0.001 * branch.q_H_scaled)).abs().max() < 1e-12
    assert (branch.M_log_ratio - 10.0 * branch.P_log_ratio_over_10).abs().max() < 1e-12

    qminus = branch[branch.run == "q-minus"]
    assert len(qminus) > 10
    assert qminus.H_a3.min() < 0.598
    assert (qminus.type == "LP").any()
    assert not (branch.type == "HB").any()

    qplus = branch[branch.run == "q-plus"]
    assert qplus.H_a3.max() > 0.6109
    assert qplus.H_a3.max() < 0.612


def test_task020_python_diagnostics_and_comparisons_are_conservative() -> None:
    diag = pd.read_csv(OUT / "python_residual_eigen_diagnostics.csv")
    assert diag.scaled_restricted_residual_norm.max() < 1e-6
    assert diag.full_stable_eigenvalue_count.min() <= 3
    assert diag.full_critical_real_s_inv.max() > 0

    py = pd.read_csv(OUT / "python_restricted_ha3_local_continuation.csv")
    assert bool(py.loc[py.H_a3.eq(0.62), "success"].iloc[0])
    assert not bool(py.loc[py.H_a3.eq(0.595), "success"].iloc[0])

    comp = pd.read_csv(OUT / "task012_python_probe_comparison.csv")
    assert {0.4, 0.625, 0.85}.issubset(set(comp.H_a3.round(3)))
    assert comp.z_abs_error_m.max() > 300.0  # TASK-012 probe is not branch-geometry evidence.


def test_task020_verdict_documents_no_auto_supported_hopf() -> None:
    verdict = json.loads((OUT / "task020_ha3_verdict.json").read_text())
    assert verdict["uses_task019_scaled_restricted_3d_gate"] is True
    assert verdict["task019_gate_passes_for_task020"] is True
    assert verdict["active_control_mapping"] == "q_H=(H_a3-0.61)/0.001"
    assert verdict["auto_supported_hopf_candidate"] is False
    assert verdict["auto_hb_labels"] == 0
    assert verdict["auto_lp_labels"] >= 1
    assert "inconclusiveness" in verdict["verdict"]

    note = DOC.read_text()
    assert "no AUTO-supported Hopf candidate" in note
    assert "TASK-019 restricted 3D AUTO formulation" in note
    assert "q_H=(H_a3-0.61)/0.001" in note
    assert "Python hint only" in note

    script = SCRIPT.read_text()
    assert "python_restricted_ha3_local_continuation.csv" in script
    assert "task020_ha3_verdict.json" in script
