"""TASK-026 Python pseudo-arclength continuation core for full Berton equilibria.

This module keeps the continuation algebra inspectable outside AUTO.  It uses
full four-dimensional Berton equilibrium residuals, transforms mass to
``log(m/kg)``, scales the state/control coordinates, and writes transparent
predictor/corrector diagnostics for a local ``W_a0`` branch step from the
TASK-011/TASK-012 equilibrium seed.

Run from the repository root with::

    uv run python episodes/10-full-model-python-continuation/scripts/berton_full_task026_continuation.py
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
EPISODE_ROOT = SCRIPT_DIR.parents[0]
REPO_ROOT = SCRIPT_DIR.parents[2]
OUT_DIR = EPISODE_ROOT / "outputs" / "task026"
TASK011_OUT = REPO_ROOT / "episodes" / "05-full-model-oscillatory-orbit" / "outputs" / "task011"
EP04_SCRIPTS = REPO_ROOT / "episodes" / "04-full-model-auto-equilibria" / "scripts"
if str(EP04_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(EP04_SCRIPTS))

from berton_full_auto_task009_validate import default_par, finite_difference_jacobian, python_rhs  # noqa: E402


@dataclass(frozen=True)
class Scaling:
    """Affine state/control scaling and residual row scaling.

    Scaled state is ``x = [(z-z_ref)/z_scale, (u-u_ref)/u_scale,
    (w-w_ref)/w_scale, log(m/kg)-log_m_ref]``.  The arclength control is
    ``lambda = (W_a0-W_a0_ref)/W_a0_scale``.
    """

    z_ref_m: float
    u_ref_m_s: float
    w_ref_m_s: float
    log_m_ref: float
    z_scale_m: float = 100.0
    u_scale_m_s: float = 1.0
    w_scale_m_s: float = 0.1
    log_m_scale: float = 1.0
    W_a0_ref_m_s: float = 0.6
    W_a0_scale_m_s: float = 0.1
    # Residual components are [z_dot, u_dot, w_dot, d(log m)/dt].
    residual_row_scales: tuple[float, float, float, float] = (10.0, 100.0, 100.0, 1.0e8)

    @property
    def state_scale_vector(self) -> np.ndarray:
        return np.array([self.z_scale_m, self.u_scale_m_s, self.w_scale_m_s, self.log_m_scale], dtype=float)

    @property
    def residual_scale_vector(self) -> np.ndarray:
        return np.array(self.residual_row_scales, dtype=float)

    def state_to_scaled(self, y: np.ndarray) -> np.ndarray:
        z, u, w, m = map(float, y)
        if m <= 0.0:
            raise ValueError(f"Mass must be positive for log transform, got {m}")
        return np.array(
            [
                (z - self.z_ref_m) / self.z_scale_m,
                (u - self.u_ref_m_s) / self.u_scale_m_s,
                (w - self.w_ref_m_s) / self.w_scale_m_s,
                (np.log(m) - self.log_m_ref) / self.log_m_scale,
            ],
            dtype=float,
        )

    def scaled_to_state(self, x: np.ndarray) -> np.ndarray:
        x = np.asarray(x, dtype=float)
        log_m = self.log_m_ref + self.log_m_scale * x[3]
        return np.array(
            [
                self.z_ref_m + self.z_scale_m * x[0],
                self.u_ref_m_s + self.u_scale_m_s * x[1],
                self.w_ref_m_s + self.w_scale_m_s * x[2],
                np.exp(log_m),
            ],
            dtype=float,
        )

    def control_to_scaled(self, W_a0_m_s: float) -> float:
        return (float(W_a0_m_s) - self.W_a0_ref_m_s) / self.W_a0_scale_m_s

    def scaled_to_control(self, lam: float) -> float:
        return self.W_a0_ref_m_s + self.W_a0_scale_m_s * float(lam)


@dataclass(frozen=True)
class ContinuationConfig:
    ds: float = 0.01
    max_newton_iterations: int = 12
    correction_tolerance: float = 1e-7
    finite_difference_step: float = 1e-5
    min_singular_value_warning: float = 1e-12


@dataclass
class CorrectorResult:
    accepted: bool
    q: np.ndarray
    iterations: list[dict[str, float | int | str]]
    reason: str
    final_augmented_norm: float
    final_residual_norm: float
    jacobian_condition: float
    singular_values: np.ndarray


def seed_state_and_parameters() -> tuple[np.ndarray, np.ndarray, Scaling]:
    seed = pd.read_csv(TASK011_OUT / "continuation_equilibrium_seed.csv").iloc[0]
    y = np.array([seed.z_m, seed.u_m_s, seed.w_m_s, seed.m_kg], dtype=float)
    par = default_par()
    par[0] = 9000.0  # z_W0, m
    par[1] = 0.6  # W_a0, m/s; continuation control for TASK-026
    par[3] = 0.61  # H_a3
    par[38] = 0.0  # eta_blend => altitude-dependent eta
    par[42] = 0.0  # no Coriolis, matching TASK-011 seed
    scaling = Scaling(z_ref_m=y[0], u_ref_m_s=y[1], w_ref_m_s=y[2], log_m_ref=float(np.log(y[3])))
    return y, par, scaling


def transformed_rhs_from_physical(y: np.ndarray, par: np.ndarray) -> np.ndarray:
    f = python_rhs(y, par)
    return np.array([f[0], f[1], f[2], f[3] / y[3]], dtype=float)


def residual_scaled(x: np.ndarray, lam: float, par_template: np.ndarray, scaling: Scaling) -> np.ndarray:
    y = scaling.scaled_to_state(x)
    par = par_template.copy()
    par[1] = scaling.scaled_to_control(lam)
    return scaling.residual_scale_vector * transformed_rhs_from_physical(y, par)


def q_residual(q: np.ndarray, par_template: np.ndarray, scaling: Scaling) -> np.ndarray:
    return residual_scaled(q[:4], float(q[4]), par_template, scaling)


def finite_difference_branch_jacobian(
    q: np.ndarray,
    par_template: np.ndarray,
    scaling: Scaling,
    h: float = 1e-5,
) -> np.ndarray:
    q = np.asarray(q, dtype=float)
    J = np.zeros((4, 5), dtype=float)
    for i in range(5):
        step = h * max(1.0, abs(q[i]))
        qp = q.copy(); qm = q.copy(); qp[i] += step; qm[i] -= step
        J[:, i] = (q_residual(qp, par_template, scaling) - q_residual(qm, par_template, scaling)) / (qp[i] - qm[i])
    return J


def tangent_from_jacobian(J: np.ndarray, previous: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray, float]:
    _u, singular_values, vh = np.linalg.svd(J)
    tangent = vh[-1, :]
    tangent = tangent / np.linalg.norm(tangent)
    if previous is not None and float(np.dot(tangent, previous)) < 0.0:
        tangent = -tangent
    elif previous is None and tangent[-1] < 0.0:
        tangent = -tangent
    cond = float(singular_values[0] / singular_values[-1]) if singular_values[-1] > 0.0 else float("inf")
    return tangent, singular_values, cond


def augmented_residual(q: np.ndarray, q_pred: np.ndarray, tangent: np.ndarray, par: np.ndarray, scaling: Scaling) -> np.ndarray:
    return np.r_[q_residual(q, par, scaling), np.dot(q - q_pred, tangent)]


def augmented_jacobian(J_branch: np.ndarray, tangent: np.ndarray) -> np.ndarray:
    return np.vstack([J_branch, tangent])


def corrector(
    q_pred: np.ndarray,
    tangent: np.ndarray,
    par_template: np.ndarray,
    scaling: Scaling,
    config: ContinuationConfig,
) -> CorrectorResult:
    q = np.array(q_pred, dtype=float)
    iterations: list[dict[str, float | int | str]] = []
    singular_values = np.full(5, np.nan)
    condition = float("nan")
    reason = "maximum Newton iterations reached"

    for k in range(config.max_newton_iterations):
        r = q_residual(q, par_template, scaling)
        aug = np.r_[r, np.dot(q - q_pred, tangent)]
        J = finite_difference_branch_jacobian(q, par_template, scaling, config.finite_difference_step)
        A = augmented_jacobian(J, tangent)
        singular_values = np.linalg.svd(A, compute_uv=False)
        condition = float(singular_values[0] / singular_values[-1]) if singular_values[-1] > 0.0 else float("inf")
        aug_norm = float(np.linalg.norm(aug))
        if aug_norm < config.correction_tolerance:
            reason = "converged"
            iterations.append(
                {
                    "iteration": k,
                    "residual_norm": float(np.linalg.norm(r)),
                    "augmented_norm": aug_norm,
                    "correction_norm": 0.0,
                    "jacobian_condition": condition,
                    "min_singular_value": float(singular_values[-1]),
                    "linear_solver": "not_needed",
                }
            )
            return CorrectorResult(True, q, iterations, reason, aug_norm, float(np.linalg.norm(r)), condition, singular_values)
        try:
            delta = np.linalg.solve(A, -aug)
            linear_reason = "solve"
        except np.linalg.LinAlgError:
            delta, *_ = np.linalg.lstsq(A, -aug, rcond=None)
            linear_reason = "lstsq_singular_augmented_jacobian"
        q = q + delta
        iterations.append(
            {
                "iteration": k,
                "residual_norm": float(np.linalg.norm(r)),
                "augmented_norm": aug_norm,
                "correction_norm": float(np.linalg.norm(delta)),
                "jacobian_condition": condition,
                "min_singular_value": float(singular_values[-1]),
                "linear_solver": linear_reason,
            }
        )
        if not np.all(np.isfinite(q)):
            reason = "non-finite Newton iterate"
            break

    final_r = q_residual(q, par_template, scaling) if np.all(np.isfinite(q)) else np.full(4, np.nan)
    final_aug = augmented_residual(q, q_pred, tangent, par_template, scaling) if np.all(np.isfinite(q)) else np.full(5, np.nan)
    return CorrectorResult(
        False,
        q,
        iterations,
        reason,
        float(np.linalg.norm(final_aug)),
        float(np.linalg.norm(final_r)),
        condition,
        singular_values,
    )


def local_continuation_step(config: ContinuationConfig | None = None) -> dict[str, Any]:
    config = config or ContinuationConfig()
    y_seed, par, scaling = seed_state_and_parameters()
    q0 = np.r_[scaling.state_to_scaled(y_seed), scaling.control_to_scaled(par[1])]
    residual0 = q_residual(q0, par, scaling)
    J0 = finite_difference_branch_jacobian(q0, par, scaling, config.finite_difference_step)
    tangent0, branch_singular_values, branch_condition = tangent_from_jacobian(J0)
    q_pred = q0 + config.ds * tangent0
    result = corrector(q_pred, tangent0, par, scaling, config)
    J1 = finite_difference_branch_jacobian(result.q, par, scaling, config.finite_difference_step)
    tangent1, branch_singular_values_1, branch_condition_1 = tangent_from_jacobian(J1, previous=tangent0)
    y_corrected = scaling.scaled_to_state(result.q[:4])
    par_corrected = par.copy(); par_corrected[1] = scaling.scaled_to_control(result.q[4])
    return {
        "config": config,
        "scaling": scaling,
        "seed_state": y_seed,
        "seed_parameters": par,
        "q0": q0,
        "seed_residual_scaled": residual0,
        "seed_residual_transformed": transformed_rhs_from_physical(y_seed, par),
        "seed_physical_residual": python_rhs(y_seed, par),
        "seed_physical_eigenvalues": np.linalg.eigvals(finite_difference_jacobian(y_seed, par)),
        "branch_jacobian_condition_seed": branch_condition,
        "branch_jacobian_singular_values_seed": branch_singular_values,
        "tangent0": tangent0,
        "q_pred": q_pred,
        "corrector": result,
        "q_corrected": result.q,
        "corrected_state": y_corrected,
        "corrected_parameters": par_corrected,
        "tangent1": tangent1,
        "branch_jacobian_condition_corrected": branch_condition_1,
        "branch_jacobian_singular_values_corrected": branch_singular_values_1,
        "corrected_physical_eigenvalues": np.linalg.eigvals(finite_difference_jacobian(y_corrected, par_corrected)),
    }


def write_outputs(run: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    scaling: Scaling = run["scaling"]
    config: ContinuationConfig = run["config"]
    result: CorrectorResult = run["corrector"]

    pd.DataFrame(
        [
            {
                "point": "seed",
                "z_m": run["seed_state"][0],
                "u_m_s": run["seed_state"][1],
                "w_m_s": run["seed_state"][2],
                "m_kg": run["seed_state"][3],
                "log_m_kg": np.log(run["seed_state"][3]),
                "W_a0_m_s": run["seed_parameters"][1],
                "scaled_residual_norm": float(np.linalg.norm(run["seed_residual_scaled"])),
                "physical_residual_norm": float(np.linalg.norm(run["seed_physical_residual"])),
                "transformed_residual_norm": float(np.linalg.norm(run["seed_residual_transformed"])),
            },
            {
                "point": "corrected",
                "z_m": run["corrected_state"][0],
                "u_m_s": run["corrected_state"][1],
                "w_m_s": run["corrected_state"][2],
                "m_kg": run["corrected_state"][3],
                "log_m_kg": np.log(run["corrected_state"][3]),
                "W_a0_m_s": run["corrected_parameters"][1],
                "scaled_residual_norm": result.final_residual_norm,
                "physical_residual_norm": float(np.linalg.norm(python_rhs(run["corrected_state"], run["corrected_parameters"]))),
                "transformed_residual_norm": float(np.linalg.norm(transformed_rhs_from_physical(run["corrected_state"], run["corrected_parameters"]))),
            },
        ]
    ).to_csv(OUT_DIR / "seed_and_corrected_points.csv", index=False)

    eig_rows = []
    for label, eigs in [("seed", run["seed_physical_eigenvalues"]), ("corrected", run["corrected_physical_eigenvalues"] )]:
        for i, eig in enumerate(eigs):
            eig_rows.append({"point": label, "eigenvalue_index": i, "real_s_inv": eig.real, "imag_s_inv": eig.imag})
    pd.DataFrame(eig_rows).to_csv(OUT_DIR / "seed_corrected_eigenvalues.csv", index=False)

    pd.DataFrame(result.iterations).to_csv(OUT_DIR / "corrector_iterations.csv", index=False)
    pd.DataFrame(
        [
            {"component": f"x{i}", "seed_tangent": run["tangent0"][i], "corrected_tangent": run["tangent1"][i]} for i in range(4)
        ] + [{"component": "lambda_W_a0", "seed_tangent": run["tangent0"][4], "corrected_tangent": run["tangent1"][4]}]
    ).to_csv(OUT_DIR / "tangent_estimates.csv", index=False)

    summary = {
        "coordinate_system": "scaled z,u,w,log(m/kg) with scaled W_a0 control",
        "state_scaled_definition": {
            "x0": "(z_m - z_ref_m) / z_scale_m",
            "x1": "(u_m_s - u_ref_m_s) / u_scale_m_s",
            "x2": "(w_m_s - w_ref_m_s) / w_scale_m_s",
            "x3": "(log(m_kg) - log_m_ref) / log_m_scale",
            "lambda": "(W_a0_m_s - W_a0_ref_m_s) / W_a0_scale_m_s",
        },
        "scaling": scaling.__dict__,
        "config": config.__dict__,
        "accepted": result.accepted,
        "failure_or_convergence_reason": result.reason,
        "arclength_ds_scaled": config.ds,
        "predicted_step_norm_scaled": float(np.linalg.norm(run["q_pred"] - run["q0"])),
        "accepted_step_norm_scaled": float(np.linalg.norm(run["q_corrected"] - run["q0"])),
        "control_step_W_a0_m_s": float(run["corrected_parameters"][1] - run["seed_parameters"][1]),
        "seed_scaled_residual_norm": float(np.linalg.norm(run["seed_residual_scaled"])),
        "corrected_scaled_residual_norm": result.final_residual_norm,
        "seed_branch_jacobian_condition": run["branch_jacobian_condition_seed"],
        "corrected_branch_jacobian_condition": run["branch_jacobian_condition_corrected"],
        "augmented_jacobian_condition_final": result.jacobian_condition,
        "branch_singular_values_seed": run["branch_jacobian_singular_values_seed"].tolist(),
        "branch_singular_values_corrected": run["branch_jacobian_singular_values_corrected"].tolist(),
        "augmented_singular_values_final": result.singular_values.tolist(),
        "residual_risk": "This is a local core validation step only; branch-length, step adaptation, and nonsmooth transition behavior remain follow-up work.",
        "output_files": [
            "seed_and_corrected_points.csv",
            "seed_corrected_eigenvalues.csv",
            "corrector_iterations.csv",
            "tangent_estimates.csv",
            "continuation_diagnostics.json",
        ],
    }
    (OUT_DIR / "continuation_diagnostics.json").write_text(json.dumps(summary, indent=2, sort_keys=True))


def main() -> None:
    run = local_continuation_step()
    write_outputs(run)
    result: CorrectorResult = run["corrector"]
    print(f"Wrote TASK-026 continuation diagnostics to {OUT_DIR}")
    print(f"Corrector accepted={result.accepted}, reason={result.reason}, residual_norm={result.final_residual_norm:.3e}")


if __name__ == "__main__":
    main()
