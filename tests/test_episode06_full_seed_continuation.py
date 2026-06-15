from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

EP = Path("episodes/06-full-model-auto-seed-continuation")
OUT = EP / "outputs" / "task012"
AUTO = EP / "auto" / "berton_full_task012"


def test_task012_reviews_task011_equilibrium_seed() -> None:
    seed = pd.read_csv(OUT / "task011_seed_review.csv")
    verdict = json.loads((OUT / "task011_verdict_review.json").read_text())

    assert seed.loc[0, "classification"] == "damped/equilibrium-like"
    assert seed.loc[0, "seed_type"] == "late-time equilibrium estimate"
    assert abs(seed.loc[0, "z_m"] - 9618.027532260936) < 1e-6
    assert seed.loc[0, "rhs_norm"] < 1e-10
    assert verdict["classification"] == "damped/equilibrium-like"


def test_task012_auto_runs_use_non_zW0_controls_and_record_failure_diagnostics() -> None:
    for name in ["wA0-plus", "wA0-minus", "Ha3-plus", "Ha3-minus"]:
        assert (AUTO / f"b.task012-{name}").exists()
        assert (AUTO / f"s.task012-{name}").exists()
        assert (AUTO / f"d.task012-{name}").exists()

    summary = pd.read_csv(OUT / "continuation_summary.csv")
    assert set(summary["control"]) == {"W_a0", "H_a3"}
    assert (summary["auto_accepted_non_mx_points"] >= 1).all()
    assert summary["main_failure_note"].str.contains("Retrying|No convergence", regex=True).all()

    notes = pd.read_csv(OUT / "auto_convergence_notes.csv")
    assert notes["message"].str.contains("No convergence with minimum step size").any()


def test_task012_eigenvalue_and_control_probe_outputs_are_present() -> None:
    eig = pd.read_csv(OUT / "auto_eigenvalue_diagnostics.csv")
    seed_eigs = eig[eig["label"] == 1]
    assert (seed_eigs["real_s_inv"] < 0).all()
    assert (seed_eigs["imag_s_inv"].abs() > 1e-4).any()

    probe = pd.read_csv(OUT / "python_equilibrium_control_probe.csv")
    assert set(probe["control"]) == {"W_a0", "H_a3"}
    assert probe["success"].all()
    assert probe["rhs_norm"].max() < 1e-9

    w = probe[probe["control"] == "W_a0"]
    assert w["control_value"].min() <= 0.1
    assert w["control_value"].max() >= 1.2
    assert w["z_m"].max() - w["z_m"].min() > 40.0
    assert (w["critical_real_s_inv"] < 0).all()

    h = probe[probe["control"] == "H_a3"]
    assert h["critical_real_s_inv"].min() < 0
    assert h["critical_real_s_inv"].max() > 0
    assert (OUT / "python_equilibrium_control_probe.png").exists()
