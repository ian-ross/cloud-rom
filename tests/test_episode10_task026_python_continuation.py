from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

EP = Path("episodes/10-full-model-python-continuation")
SCRIPT_DIR = EP / "scripts"
OUT = EP / "outputs" / "task026"
DOC = EP / "docs" / "task026_python_continuation_core.md"
if str(SCRIPT_DIR.resolve()) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR.resolve()))

from berton_full_task026_continuation import (  # noqa: E402
    ContinuationConfig,
    Scaling,
    finite_difference_branch_jacobian,
    local_continuation_step,
    q_residual,
    residual_scaled,
    seed_state_and_parameters,
    transformed_rhs_from_physical,
)


def test_task026_coordinate_round_trip_includes_log_mass_inverse() -> None:
    y_seed, par, scaling = seed_state_and_parameters()
    x = scaling.state_to_scaled(y_seed)
    y_roundtrip = scaling.scaled_to_state(x)
    assert np.allclose(y_roundtrip[:3], y_seed[:3], rtol=0.0, atol=1e-14)
    assert np.isclose(y_roundtrip[3], y_seed[3], rtol=1e-14, atol=0.0)

    lam = scaling.control_to_scaled(par[1])
    assert scaling.scaled_to_control(lam) == par[1]
    assert x.shape == (4,)
    assert np.isfinite(x).all()


def test_task026_residual_scaling_matches_transformed_full_rhs() -> None:
    y_seed, par, scaling = seed_state_and_parameters()
    x = scaling.state_to_scaled(y_seed)
    lam = scaling.control_to_scaled(par[1])
    transformed = transformed_rhs_from_physical(y_seed, par)
    scaled = residual_scaled(x, lam, par, scaling)
    assert np.allclose(scaled, scaling.residual_scale_vector * transformed)
    assert abs(transformed[3]) < 1e-12  # log-mass tendency is finite and near equilibrium
    assert np.linalg.norm(scaled) < 1e-6

    shifted_scaling = Scaling(
        z_ref_m=scaling.z_ref_m,
        u_ref_m_s=scaling.u_ref_m_s,
        w_ref_m_s=scaling.w_ref_m_s,
        log_m_ref=scaling.log_m_ref,
        residual_row_scales=(1.0, 1.0, 1.0, 1.0),
    )
    shifted_x = shifted_scaling.state_to_scaled(y_seed)
    unscaled_residual = residual_scaled(shifted_x, shifted_scaling.control_to_scaled(par[1]), par, shifted_scaling)
    assert np.allclose(unscaled_residual, transformed)


def test_task026_local_tangent_and_corrector_step_converges() -> None:
    run = local_continuation_step(ContinuationConfig(ds=0.005, correction_tolerance=1e-7))
    result = run["corrector"]
    assert result.accepted
    assert result.reason == "converged"
    assert result.final_residual_norm < 1e-6
    assert np.isclose(np.linalg.norm(run["tangent0"]), 1.0)
    assert run["tangent0"].shape == (5,)
    assert abs(run["tangent0"][4]) > 0.5  # local branch really moves the W_a0 control

    J = finite_difference_branch_jacobian(run["q_corrected"], run["seed_parameters"], run["scaling"])
    assert J.shape == (4, 5)
    assert np.linalg.matrix_rank(J) == 4
    assert np.linalg.norm(q_residual(run["q_corrected"], run["seed_parameters"], run["scaling"])) < 1e-6


def test_task026_curated_outputs_and_note_record_diagnostics() -> None:
    diagnostics = json.loads((OUT / "continuation_diagnostics.json").read_text())
    assert diagnostics["accepted"] is True
    assert diagnostics["failure_or_convergence_reason"] == "converged"
    assert diagnostics["coordinate_system"] == "scaled z,u,w,log(m/kg) with scaled W_a0 control"
    assert diagnostics["corrected_scaled_residual_norm"] < 1e-6
    assert diagnostics["control_step_W_a0_m_s"] > 0.0
    assert len(diagnostics["branch_singular_values_seed"]) == 4
    assert len(diagnostics["augmented_singular_values_final"]) == 5

    points = pd.read_csv(OUT / "seed_and_corrected_points.csv")
    assert set(points["point"]) == {"seed", "corrected"}
    assert (points["m_kg"] > 0.0).all()
    assert points.loc[points.point == "seed", "physical_residual_norm"].iloc[0] < 1e-10
    assert points.loc[points.point == "corrected", "scaled_residual_norm"].iloc[0] < 1e-6

    eig = pd.read_csv(OUT / "seed_corrected_eigenvalues.csv")
    assert set(eig["point"]) == {"seed", "corrected"}
    assert len(eig) == 8
    assert (eig.groupby("point")["imag_s_inv"].apply(lambda s: (s.abs() > 1e-4).any())).all()

    iterations = pd.read_csv(OUT / "corrector_iterations.csv")
    assert {"residual_norm", "augmented_norm", "correction_norm", "jacobian_condition", "linear_solver"}.issubset(iterations.columns)
    assert iterations["augmented_norm"].iloc[-1] < 1e-6

    tangents = pd.read_csv(OUT / "tangent_estimates.csv")
    assert set(tangents["component"]) == {"x0", "x1", "x2", "x3", "lambda_W_a0"}

    doc = DOC.read_text()
    assert "full four-dimensional Berton equilibrium state" in doc
    assert "Predictor/corrector diagnostics" in doc
    assert "Seed residual/eigenvalue cross-check" in doc
