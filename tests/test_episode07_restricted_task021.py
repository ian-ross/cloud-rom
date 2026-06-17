from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

EP = Path("episodes/07-restricted-equilibrium-auto")
AUTO = EP / "auto" / "berton_restricted_task021_minimal"
OUT = EP / "outputs" / "task021"
DOC = EP / "docs" / "task021_minimal_wa0_auto_diagnostic.md"
NOTEBOOK = EP / "notebooks" / "task021_minimal_wa0_auto_diagnostic.ipynb"
SCRIPT = EP / "scripts" / "berton_restricted_task021_minimal_auto.py"


def test_task021_minimal_auto_config_is_stripped_and_separate() -> None:
    src = (AUTO / "bertonrestricted_task021_minimal.f90").read_text()
    assert "TASK-021 minimal restricted/scaled 3D equilibrium gate" in src
    assert "CALL restricted_scaled_rhs(U(1:3),PAR,F(1:3))" in src
    assert "TASK-021 intentionally supplies no analytic/user Jacobian" in src
    assert "Deliberately empty: TASK-021 strips PVLS diagnostic bookkeeping" in src
    assert "CALL set_pvls" not in src.split("SUBROUTINE PVLS", 1)[1]

    plus = (AUTO / "c.bertonrestricted-task021-minimal-wA0-plus").read_text()
    minus = (AUTO / "c.bertonrestricted-task021-minimal-wA0-minus").read_text()
    for text in (plus, minus):
        assert "ICP = ['W_a0']" in text
        assert "ISP=0" in text
        assert "ILP=0" in text
        assert "JAC=0" in text
        assert "NPAR=53" in text
        assert "sigma_S" not in text
        assert "R_zeta" not in text
        assert "z_phys" not in text
    assert "DS=0.001" in plus
    assert "DS=-0.001" in minus
    assert (AUTO / "b.task021-minimal-wA0-plus").exists()
    assert (AUTO / "b.task021-minimal-wA0-minus").exists()


def test_task021_curated_outputs_record_minimal_failure() -> None:
    cfg = pd.read_csv(OUT / "minimal_config_summary.csv")
    assert set(cfg.run) == {"minimal-wA0-plus", "minimal-wA0-minus"}
    assert (cfg.icp == "['W_a0']").all()
    assert (cfg.isp == 0).all()
    assert (cfg.jac == 0).all()
    assert (cfg.ilp == 0).all()
    assert not cfg.has_pvls_diagnostic_icp.any()

    summary = pd.read_csv(OUT / "minimal_continuation_summary.csv").iloc[0]
    assert int(summary.auto_total_points) == 2
    assert int(summary.auto_nontrivial_points) == 0
    assert summary.auto_control_min == 0.6
    assert summary.auto_control_max == 0.6
    assert not bool(summary.accepted_beyond_0p6)
    assert summary.task017_control_min == 0.6
    assert summary.task017_control_max == 0.6
    assert int(summary.task017_nontrivial_points) == 0
    assert summary.python_probe_min == 0.1
    assert summary.python_probe_max == 1.2
    assert bool(summary.python_probe_all_stable)
    assert "NaN" in summary.minimal_failure_mode
    assert "not solely diagnostic/PVLS/supplied-Jacobian" in summary.interpretation


def test_task021_verdict_and_note_compare_against_task017_and_task012() -> None:
    verdict = json.loads((OUT / "task021_minimal_auto_verdict.json").read_text())
    assert verdict["minimal_icp"] == ["W_a0"]
    assert verdict["isp"] == 0
    assert verdict["jac"] == 0
    assert verdict["pvls_callback"] == "empty"
    assert verdict["wA0_auto_covered_range_m_s"] == [0.6, 0.6]
    assert verdict["accepted_beyond_0p6"] is False
    assert verdict["wA0_python_expected_range_m_s"] == [0.1, 1.2]
    assert "failure persists in stripped configuration" in verdict["interpretation"]

    note = DOC.read_text()
    assert "TASK-021 minimal W_a0 AUTO diagnostic" in note
    assert "`ICP=['W_a0']`" in note
    assert "`ISP=0`, `ILP=0`, `JAC=0`, `NPAR=53`" in note
    assert "no nontrivial point beyond `W_a0=0.6` was accepted" in note
    assert "TASK-017 also accepted only the seed" in note
    assert "TASK-012 Python W_a0 probe successfully follows stable equilibria" in note
    assert "unlikely to be caused solely by TASK-017 diagnostic metadata/PVLS/Jacobian bookkeeping" in note


def test_task021_reproducibility_artifacts_exist() -> None:
    assert SCRIPT.exists()
    assert NOTEBOOK.exists()
    nb = json.loads(NOTEBOOK.read_text())
    sources = "\n".join("".join(cell.get("source", [])) for cell in nb["cells"])
    assert "run_auto.sh" in sources
    assert "ICP=['W_a0']" in sources
    assert "berton_restricted_task021_minimal_auto.py" in sources
