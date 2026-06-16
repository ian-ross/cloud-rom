from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

EP = Path("episodes/07-restricted-equilibrium-auto")
SCRIPT = EP / "scripts" / "berton_restricted_task018_diagnostics.py"
OUT = EP / "outputs" / "task018"
DOC = EP / "docs" / "task018_restricted_scaling_diagnostics.md"


def test_task018_script_defines_restricted_residual_and_physical_map() -> None:
    text = SCRIPT.read_text()
    assert "def physical_from_restricted" in text
    assert "return np.array([z, u, 0.0, np.exp(log_m)]" in text
    assert "def restricted_residual" in text
    assert "np.array([f[1], f[2], f[3] / y[3]]" in text
    assert "STATE_NAMES = (\"z_m\", \"u_m_s\", \"log_m_kg\")" in text


def test_task018_seed_crosscheck_matches_task011_stable_equilibrium() -> None:
    seed = pd.read_csv(OUT / "seed_crosscheck.csv").iloc[0]
    assert abs(seed["z_m"] - 9618.027532260936) < 1e-9
    assert abs(seed["u_m_s"] - 1.9098623386953226) < 1e-12
    assert abs(seed["log_m_kg"] - (-20.646092418309163)) < 1e-12
    assert seed["full_rhs_norm"] < 1e-10
    assert seed["restricted_residual_norm"] < 1e-10
    assert bool(seed["full_eigenvalues_match_task011"])
    assert int(seed["full_stable_eigenvalue_count"]) == 4

    eig = pd.read_csv(OUT / "full_seed_eigenvalues.csv")
    assert (eig["real_s_inv"] < 0).all()
    assert (eig["imag_s_inv"].abs() > 1e-4).any()


def test_task018_conditioning_and_parameter_sensitivity_are_reported() -> None:
    rows = pd.read_csv(OUT / "jacobian_row_norms.csv")
    cols = pd.read_csv(OUT / "jacobian_column_norms.csv")
    svals = pd.read_csv(OUT / "jacobian_singular_values.csv")
    sens = pd.read_csv(OUT / "parameter_sensitivities.csv")

    assert set(rows["residual"]) == {"du_dt_m_s2", "dw_dt_m_s2", "dlogm_dt_s_inv"}
    assert set(cols["state"]) == {"z_m", "u_m_s", "log_m_kg"}
    assert {"unscaled_physical_logm_residual", "centered_state_scaled_row_scaled"} <= set(svals["scaling"])
    unscaled_cond = svals.loc[svals.scaling == "unscaled_physical_logm_residual", "condition_estimate"].iloc[0]
    scaled_cond = svals.loc[svals.scaling == "centered_state_scaled_row_scaled", "condition_estimate"].iloc[0]
    assert unscaled_cond > 1e6
    assert scaled_cond < 20.0
    assert set(sens["parameter"]) == {"W_a0_m_s", "H_a3"}
    assert len(sens) == 12


def test_task018_branch_risks_and_recommendation_are_curated() -> None:
    branch = pd.read_csv(OUT / "branch_smoothness_report.csv")
    assert branch["piece"].str.contains("relative humidity H_a").any()
    assert branch["piece"].str.contains("infrared eta").any()
    assert branch["piece"].str.contains("Reynolds terminal fallback").any()
    assert branch["piece"].str.contains("geometry solve").any()
    assert branch["risk_at_seed"].str.contains("kink|fallback inactive|smooth|guard inactive", regex=True).all()

    rec = json.loads((OUT / "scaling_recommendation.json").read_text())
    assert rec["state_coordinate"] == "Z=(z-z_seed)/100m; U=(u-u_seed)/(1m/s); M=log(m/m_seed)"
    assert rec["scaled_condition_estimate"] < rec["unscaled_condition_estimate"]
    assert rec["suitable_for_task019_gate"] is True
    assert "prove W_a0 continuation before H_a3" in rec["caveat"]

    note = DOC.read_text()
    assert "This is not a claim that Hopf continuation is ready" in note
    assert "Residuals: divide" in note
    assert "nearby 10 km humidity/eta kinks" in note
