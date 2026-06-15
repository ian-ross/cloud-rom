from pathlib import Path

import numpy as np
import pandas as pd

EPISODE = Path(__file__).resolve().parents[1] / "episodes" / "05-full-model-oscillatory-orbit"
OUT = EPISODE / "outputs" / "task011"


def test_task011_episode_artifacts_exist():
    assert (EPISODE / "README.md").exists()
    assert (EPISODE / "notebooks" / "task011_case0_long_integration.ipynb").exists()
    assert (EPISODE / "docs" / "task011_case0_long_integration.md").exists()
    for name in [
        "case0_bdf_500h.csv",
        "case0_lsoda_500h.csv",
        "summary.csv",
        "solver_agreement.csv",
        "equilibrium.csv",
        "eigenvalues.csv",
        "continuation_equilibrium_seed.csv",
        "case0_long_timeseries.png",
        "case0_late_envelope.png",
        "case0_solver_agreement.png",
    ]:
        assert (OUT / name).exists()


def test_task011_bdf_lsoda_cover_required_and_extended_horizons():
    for method in ["bdf", "lsoda"]:
        df = pd.read_csv(OUT / f"case0_{method}_500h.csv")
        assert df["t_h"].max() >= 500.0
        assert (df["t_h"] >= 200.0).any()
        assert df["method"].str.upper().eq(method.upper()).all()

    summary = pd.read_csv(OUT / "summary.csv")
    assert set(summary["method"]) == {"BDF", "LSODA"}
    assert np.all(summary["base_duration_h"] >= 200.0)
    assert np.all(summary["duration_h"] >= 500.0)
    assert np.all(summary["z_amp_150_200h_m"] > 1.0)
    assert np.all(summary["z_amp_450_500h_m"] < 0.02)
    assert np.all(summary["classification"] == "damped/equilibrium-like")


def test_task011_equilibrium_seed_has_stable_complex_pair():
    seed = pd.read_csv(OUT / "continuation_equilibrium_seed.csv")
    assert seed.loc[0, "seed_type"] == "late-time equilibrium estimate"
    assert seed.loc[0, "rhs_norm"] < 1e-9
    assert 9600.0 < seed.loc[0, "z_m"] < 9630.0

    eig = pd.read_csv(OUT / "eigenvalues.csv")
    complex_pair = eig[np.abs(eig["imag_s_inv"]) > 0]
    assert len(complex_pair) == 2
    assert np.all(complex_pair["real_s_inv"] < 0.0)
    assert np.allclose(complex_pair["period_h_if_complex"], 10.19, atol=0.05)
    assert np.allclose(complex_pair["e_folding_h"], 39.34, atol=0.2)


def test_task011_note_documents_no_explicit_euler_classification():
    note = (EPISODE / "docs" / "task011_case0_long_integration.md").read_text()
    assert "BDF" in note and "LSODA" in note
    assert "no explicit-Euler long integration" in note
    assert "damped/equilibrium-like" in note
    assert "stable spiral mode" in note
