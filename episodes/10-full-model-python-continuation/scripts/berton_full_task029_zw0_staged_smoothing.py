"""TASK-029 staged full-model Python z_W0 continuation with smoothed updraft.

Run from repository root::

    uv run python episodes/10-full-model-python-continuation/scripts/berton_full_task029_zw0_staged_smoothing.py

The workflow reuses the TASK-026 full-model pseudo-arclength scaling and the
TASK-023/TASK-024 softplus smooth-clip updraft, but explores a staged sequence
of smoothing widths before the sharper 50 m width used in those AUTO tasks.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
EPISODE_ROOT = SCRIPT_DIR.parents[0]
REPO_ROOT = SCRIPT_DIR.parents[2]
OUT_DIR = EPISODE_ROOT / "outputs" / "task029"
DOC = EPISODE_ROOT / "docs" / "task029_zw0_staged_smoothing.md"
EP04_SCRIPTS = REPO_ROOT / "episodes" / "04-full-model-auto-equilibria" / "scripts"
if str(EP04_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(EP04_SCRIPTS))
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

from berton_full_auto_task009_validate import finite_difference_jacobian  # noqa: E402
from berton_full_task026_continuation import (  # noqa: E402
    ContinuationConfig,
    CorrectorResult,
    Scaling,
    seed_state_and_parameters,
    tangent_from_jacobian,
    transformed_rhs_from_physical,
)
from cloud_rom.berton2023 import (  # noqa: E402
    Atmosphere,
    CONSTANTS,
    Crystal,
    LocalDiagnostics,
    Q_,
    SimulationConfig,
    State,
    accelerations,
)

DELTA_Z_W_M = 300.0
WIDTH_SCHEDULE_M = [300.0, 150.0, 100.0, 50.0]
ANCHORS_M = [7000.0, 7500.0, 8000.0, 8500.0, 9000.0, 9500.0, 9600.0, 9700.0, 9800.0, 9900.0, 10000.0]
TRANSITION_MIN_M = 9600.0
TRANSITION_MAX_M = 10000.0


def softplus(x: float | np.ndarray) -> float | np.ndarray:
    arr = np.asarray(x, dtype=float)
    out = np.empty_like(arr, dtype=float)
    hi = arr > 40.0; lo = arr < -40.0; mid = ~(hi | lo)
    out[hi] = arr[hi]
    out[lo] = np.exp(arr[lo])
    out[mid] = np.log1p(np.exp(arr[mid]))
    return float(out) if out.ndim == 0 else out


def smooth_clip01(x: float | np.ndarray, eps: float) -> float | np.ndarray:
    return eps * (softplus(np.asarray(x) / eps) - softplus((np.asarray(x) - 1.0) / eps))


def smoothed_updraft_value(z_m: float, z_w0_m: float, w_a0: float = 0.6, delta_z_w: float = DELTA_Z_W_M, width_m: float = 50.0) -> float:
    eps = width_m / delta_z_w
    x = (z_m - (z_w0_m - delta_z_w)) / delta_z_w
    return float(w_a0 * smooth_clip01(x, eps))


def piecewise_updraft_value(z_m: float, z_w0_m: float, w_a0: float = 0.6, delta_z_w: float = DELTA_Z_W_M) -> float:
    x = (z_m - (z_w0_m - delta_z_w)) / delta_z_w
    return float(w_a0 * min(max(x, 0.0), 1.0))


class SmoothAtmosphere(Atmosphere):
    smooth_width_m: float = 50.0

    def updraft(self, z):  # type: ignore[override]
        return Q_(
            smoothed_updraft_value(
                z.to("m").magnitude,
                self.z_W0.to("m").magnitude,
                self.W_a0.to("m/s").magnitude,
                self.Δz_W.to("m").magnitude,
                self.smooth_width_m,
            ),
            "m/s",
        )


def python_rhs_smoothed(y: np.ndarray, par: np.ndarray, width_m: float) -> np.ndarray:
    z, u, w, m = map(float, y)
    eta_blend = float(par[38])
    eta_override = None if abs(eta_blend) < 1e-14 else float(par[4])
    atm = SmoothAtmosphere(
        H_a3=float(par[3]), W_a0=Q_(float(par[1]), "m/s"), z_W0=Q_(float(par[0]), "m"),
        Δz_W=Q_(float(par[6]), "m"), η_override=eta_override,
    )
    atm.smooth_width_m = float(width_m)
    crystal = Crystal(m=Q_(m, "kg"), φ=float(par[39]), c_B=Q_(float(par[40]), "m"))
    state = State(t=Q_(0, "s"), x=Q_(0, "m"), z=Q_(z, "m"), u=Q_(u, "m/s"), w=Q_(w, "m/s"), crystal=crystal)
    config = SimulationConfig(include_coriolis=bool(round(float(par[42]))), reynolds_length="diameter" if par[43] >= 1.5 else "radius")
    diag = LocalDiagnostics.from_state(state, atm, CONSTANTS, config)
    ax, az = accelerations(state, diag, CONSTANTS, config)
    return np.array([w, ax.to("m/s^2").magnitude, az.to("m/s^2").magnitude, diag.m_dot.to("kg/s").magnitude])


@dataclass(frozen=True)
class Zw0Scaling(Scaling):
    z_W0_ref_m: float = 9000.0
    z_W0_scale_m: float = 1000.0

    def control_to_scaled(self, z_W0_m: float) -> float:  # type: ignore[override]
        return (float(z_W0_m) - self.z_W0_ref_m) / self.z_W0_scale_m

    def scaled_to_control(self, lam: float) -> float:  # type: ignore[override]
        return self.z_W0_ref_m + self.z_W0_scale_m * float(lam)


@dataclass(frozen=True)
class Zw0Config:
    lower_target_z_W0_m: float = 7000.0
    upper_target_z_W0_m: float = 10000.0
    ds_initial: float = 0.16
    ds_min: float = 0.0025
    ds_max: float = 0.22
    max_steps_per_direction: int = 360
    residual_acceptance_tolerance: float = 3.0e-6
    newton_tolerance: float = 1.0e-7


def zw0_seed_state_and_parameters() -> tuple[np.ndarray, np.ndarray, Zw0Scaling]:
    y, par, base = seed_state_and_parameters()
    par[0] = 9000.0; par[1] = 0.6; par[3] = 0.61; par[38] = 0.0; par[42] = 0.0
    return y, par, Zw0Scaling(
        z_ref_m=base.z_ref_m, u_ref_m_s=base.u_ref_m_s, w_ref_m_s=base.w_ref_m_s, log_m_ref=base.log_m_ref,
        z_scale_m=base.z_scale_m, u_scale_m_s=base.u_scale_m_s, w_scale_m_s=base.w_scale_m_s,
        log_m_scale=base.log_m_scale, W_a0_ref_m_s=base.W_a0_ref_m_s, W_a0_scale_m_s=base.W_a0_scale_m_s,
        residual_row_scales=base.residual_row_scales, z_W0_ref_m=9000.0, z_W0_scale_m=1000.0,
    )


def transformed_rhs_smoothed(y: np.ndarray, par: np.ndarray, width_m: float) -> np.ndarray:
    f = python_rhs_smoothed(y, par, width_m)
    return np.array([f[0], f[1], f[2], f[3] / y[3]], dtype=float)


def residual_scaled(x: np.ndarray, lam: float, par_template: np.ndarray, scaling: Zw0Scaling, width_m: float) -> np.ndarray:
    y = scaling.scaled_to_state(x)
    par = par_template.copy(); par[0] = scaling.scaled_to_control(lam)
    return scaling.residual_scale_vector * transformed_rhs_smoothed(y, par, width_m)


def q_residual(q: np.ndarray, par_template: np.ndarray, scaling: Zw0Scaling, width_m: float) -> np.ndarray:
    return residual_scaled(q[:4], float(q[4]), par_template, scaling, width_m)


def finite_difference_branch_jacobian(q: np.ndarray, par_template: np.ndarray, scaling: Zw0Scaling, width_m: float, h: float = 1e-5) -> np.ndarray:
    q = np.asarray(q, dtype=float)
    J = np.zeros((4, 5), dtype=float)
    for i in range(5):
        step = h * max(1.0, abs(q[i]))
        qp = q.copy(); qm = q.copy(); qp[i] += step; qm[i] -= step
        J[:, i] = (q_residual(qp, par_template, scaling, width_m) - q_residual(qm, par_template, scaling, width_m)) / (qp[i] - qm[i])
    return J


def fd_jacobian_physical_smoothed(y: np.ndarray, par: np.ndarray, width_m: float) -> np.ndarray:
    J = np.zeros((4, 4))
    steps = np.array([1.0, 1e-5, 1e-5, max(abs(y[3]) * 1e-4, 1e-14)])
    for i, h in enumerate(steps):
        yp = y.copy(); ym = y.copy(); yp[i] += h; ym[i] -= h
        if i == 3 and ym[i] <= 0.0:
            ym[i] = y[i] * (1.0 - 1e-4)
        J[:, i] = (python_rhs_smoothed(yp, par, width_m) - python_rhs_smoothed(ym, par, width_m)) / (yp[i] - ym[i])
    return J


def corrector(q_pred: np.ndarray, tangent: np.ndarray, par_template: np.ndarray, scaling: Zw0Scaling, width_m: float, config: ContinuationConfig) -> CorrectorResult:
    q = np.array(q_pred, dtype=float)
    iterations: list[dict[str, float | int | str]] = []
    singular_values = np.full(5, np.nan); condition = float("nan"); reason = "maximum Newton iterations reached"
    for k in range(config.max_newton_iterations):
        r = q_residual(q, par_template, scaling, width_m)
        aug = np.r_[r, np.dot(q - q_pred, tangent)]
        J = finite_difference_branch_jacobian(q, par_template, scaling, width_m, config.finite_difference_step)
        A = np.vstack([J, tangent])
        singular_values = np.linalg.svd(A, compute_uv=False)
        condition = float(singular_values[0] / singular_values[-1]) if singular_values[-1] > 0 else float("inf")
        aug_norm = float(np.linalg.norm(aug))
        if aug_norm < config.correction_tolerance:
            iterations.append({"iteration": k, "residual_norm": float(np.linalg.norm(r)), "augmented_norm": aug_norm, "correction_norm": 0.0, "jacobian_condition": condition, "min_singular_value": float(singular_values[-1]), "linear_solver": "not_needed"})
            return CorrectorResult(True, q, iterations, "converged", aug_norm, float(np.linalg.norm(r)), condition, singular_values)
        try:
            delta = np.linalg.solve(A, -aug); solver = "solve"
        except np.linalg.LinAlgError:
            delta, *_ = np.linalg.lstsq(A, -aug, rcond=None); solver = "lstsq_singular_augmented_jacobian"
        q = q + delta
        iterations.append({"iteration": k, "residual_norm": float(np.linalg.norm(r)), "augmented_norm": aug_norm, "correction_norm": float(np.linalg.norm(delta)), "jacobian_condition": condition, "min_singular_value": float(singular_values[-1]), "linear_solver": solver})
        if not np.all(np.isfinite(q)):
            reason = "non-finite Newton iterate"; break
    final_r = q_residual(q, par_template, scaling, width_m) if np.all(np.isfinite(q)) else np.full(4, np.nan)
    final_aug = np.r_[final_r, np.dot(q - q_pred, tangent)] if np.all(np.isfinite(q)) else np.full(5, np.nan)
    return CorrectorResult(False, q, iterations, reason, float(np.linalg.norm(final_aug)), float(np.linalg.norm(final_r)), condition, singular_values)


def _point_record(stage_index: int, width_m: float, run: str, step_index: int, q: np.ndarray, par_template: np.ndarray, scaling: Zw0Scaling, tangent: np.ndarray, branch_singular_values: np.ndarray, branch_condition: float, corrector_iterations: int, corrector_reason: str, ds_scaled: float) -> dict[str, Any]:
    y = scaling.scaled_to_state(q[:4])
    par = par_template.copy(); par[0] = scaling.scaled_to_control(q[4])
    rhs = python_rhs_smoothed(y, par, width_m)
    transformed = transformed_rhs_smoothed(y, par, width_m)
    scaled = q_residual(q, par_template, scaling, width_m)
    eig = np.linalg.eigvals(fd_jacobian_physical_smoothed(y, par, width_m))
    critical = eig[np.argmax(eig.real)]
    w_s = smoothed_updraft_value(float(y[0]), float(par[0]), float(par[1]), float(par[6]), width_m)
    w_p = piecewise_updraft_value(float(y[0]), float(par[0]), float(par[1]), float(par[6]))
    return {
        "stage_index": int(stage_index), "smooth_width_m": float(width_m), "run": run, "step_index": int(step_index), "accepted": True,
        "z_W0_m": float(par[0]), "z_W0_km": float(par[0] / 1000.0), "q_z_W0_scaled": float(q[4]),
        "z_m": float(y[0]), "u_m_s": float(y[1]), "w_m_s": float(y[2]), "m_kg": float(y[3]), "log_m_kg": float(np.log(y[3])),
        "scaled_x0_z": float(q[0]), "scaled_x1_u": float(q[1]), "scaled_x2_w": float(q[2]), "scaled_x3_log_m": float(q[3]),
        "physical_residual_norm": float(np.linalg.norm(rhs)), "transformed_residual_norm": float(np.linalg.norm(transformed)),
        "scaled_residual_norm": float(np.linalg.norm(scaled)), "max_abs_scaled_residual": float(np.max(np.abs(scaled))),
        "critical_real_s_inv": float(critical.real), "critical_imag_s_inv": float(critical.imag), "stable_eigenvalue_count": int(np.sum(eig.real < 0.0)),
        "branch_jacobian_condition": float(branch_condition), "branch_min_singular_value": float(branch_singular_values[-1]), "branch_max_singular_value": float(branch_singular_values[0]),
        "tangent_lambda_z_W0": float(tangent[4]), "ds_scaled": float(ds_scaled), "corrector_iterations": int(corrector_iterations), "corrector_reason": corrector_reason,
        "delta_z_W_m": float(par[6]), "eps_dimensionless": float(width_m / par[6]), "smoothed_W_a_m_s": float(w_s), "piecewise_W_a_m_s": float(w_p),
        "updraft_difference_m_s": float(w_s - w_p), "distance_to_z_W0_m": float(y[0] - par[0]), "distance_to_ramp_base_m": float(y[0] - (par[0] - par[6])),
        "in_paper_7_10_km_interval": bool(7000.0 <= par[0] <= 10000.0), "in_9p6_10_km_transition_region": bool(TRANSITION_MIN_M <= par[0] <= TRANSITION_MAX_M),
    }


def _eigen_records(stage_index: int, width_m: float, run: str, step_index: int, q: np.ndarray, par_template: np.ndarray, scaling: Zw0Scaling) -> list[dict[str, Any]]:
    y = scaling.scaled_to_state(q[:4]); par = par_template.copy(); par[0] = scaling.scaled_to_control(q[4])
    eigs = np.linalg.eigvals(fd_jacobian_physical_smoothed(y, par, width_m))
    return [{"stage_index": stage_index, "smooth_width_m": width_m, "run": run, "step_index": step_index, "z_W0_m": float(par[0]), "eigenvalue_index": i, "real_s_inv": float(e.real), "imag_s_inv": float(e.imag)} for i, e in enumerate(eigs)]


def continue_direction(stage_index: int, width_m: float, run: str, q_seed: np.ndarray, tangent_seed: np.ndarray, par: np.ndarray, scaling: Zw0Scaling, target_z: float, config: Zw0Config):
    cont_cfg = ContinuationConfig(ds=config.ds_initial, correction_tolerance=config.newton_tolerance)
    direction = 1.0 if target_z > scaling.scaled_to_control(q_seed[4]) else -1.0
    tangent = np.array(tangent_seed, dtype=float)
    if np.sign(tangent[4]) != np.sign(direction): tangent = -tangent
    q = np.array(q_seed, dtype=float); ds = config.ds_initial
    rows: list[dict[str, Any]] = []; eig_rows: list[dict[str, Any]] = []; iter_rows: list[dict[str, Any]] = []; failures: list[dict[str, Any]] = []
    J = finite_difference_branch_jacobian(q, par, scaling, width_m, cont_cfg.finite_difference_step)
    tangent, sv, cond = tangent_from_jacobian(J, previous=tangent)
    if np.sign(tangent[4]) != np.sign(direction): tangent = -tangent
    rows.append(_point_record(stage_index, width_m, run, 0, q, par, scaling, tangent, sv, cond, 0, "seed", 0.0))
    eig_rows.extend(_eigen_records(stage_index, width_m, run, 0, q, par, scaling))
    for step in range(1, config.max_steps_per_direction + 1):
        current_z = scaling.scaled_to_control(q[4])
        if (direction > 0 and current_z >= target_z - 1e-9) or (direction < 0 and current_z <= target_z + 1e-9): break
        predicted_dz = scaling.z_W0_scale_m * ds * tangent[4]; remaining = target_z - current_z; trial_ds = ds
        if predicted_dz != 0 and abs(predicted_dz) > abs(remaining):
            trial_ds = max(config.ds_min, abs(0.98 * remaining / (scaling.z_W0_scale_m * tangent[4])))
        result = corrector(q + trial_ds * tangent, tangent, par, scaling, width_m, ContinuationConfig(ds=trial_ds, correction_tolerance=config.newton_tolerance))
        if not result.accepted or result.final_residual_norm > config.residual_acceptance_tolerance:
            failures.append({"stage_index": stage_index, "smooth_width_m": width_m, "run": run, "attempted_step_index": step, "start_z_W0_m": float(current_z), "trial_ds_scaled": float(trial_ds), "accepted": bool(result.accepted), "reason": result.reason, "final_scaled_residual_norm": float(result.final_residual_norm), "augmented_jacobian_condition": float(result.jacobian_condition)})
            ds *= 0.5
            if ds < config.ds_min: break
            continue
        q_new = result.q; new_z = scaling.scaled_to_control(q_new[4])
        if (new_z - current_z) * direction <= 0.0:
            failures.append({"stage_index": stage_index, "smooth_width_m": width_m, "run": run, "attempted_step_index": step, "start_z_W0_m": float(current_z), "trial_ds_scaled": float(trial_ds), "accepted": True, "reason": "corrected point moved opposite requested z_W0 direction", "final_scaled_residual_norm": float(result.final_residual_norm), "augmented_jacobian_condition": float(result.jacobian_condition)})
            ds *= 0.5
            if ds < config.ds_min: break
            continue
        for it in result.iterations:
            row = dict(it); row.update({"stage_index": stage_index, "smooth_width_m": width_m, "run": run, "step_index": step, "z_W0_m": float(new_z), "ds_scaled": float(trial_ds)})
            iter_rows.append(row)
        J_new = finite_difference_branch_jacobian(q_new, par, scaling, width_m, cont_cfg.finite_difference_step)
        tangent_new, sv_new, cond_new = tangent_from_jacobian(J_new, previous=tangent)
        if np.sign(tangent_new[4]) != np.sign(direction): tangent_new = -tangent_new
        rows.append(_point_record(stage_index, width_m, run, step, q_new, par, scaling, tangent_new, sv_new, cond_new, len(result.iterations), result.reason, trial_ds))
        eig_rows.extend(_eigen_records(stage_index, width_m, run, step, q_new, par, scaling))
        q = q_new; tangent = tangent_new; ds = min(config.ds_max, max(config.ds_min, trial_ds * 1.25 if len(result.iterations) <= 5 else trial_ds))
    return rows, eig_rows, iter_rows, failures


def solve_anchor(stage_index: int, width_m: float, anchor_z: float, branch: pd.DataFrame, par: np.ndarray, scaling: Zw0Scaling, tolerance: float = 1e-8):
    b = branch.sort_values("z_W0_m").drop_duplicates("z_W0_m")
    q = np.array([np.interp(anchor_z, b.z_W0_m, b.scaled_x0_z), np.interp(anchor_z, b.z_W0_m, b.scaled_x1_u), np.interp(anchor_z, b.z_W0_m, b.scaled_x2_w), np.interp(anchor_z, b.z_W0_m, b.scaled_x3_log_m), scaling.control_to_scaled(anchor_z)], dtype=float)
    iterations: list[dict[str, Any]] = []
    reason = "maximum anchor Newton iterations reached"
    for k in range(12):
        r = q_residual(q, par, scaling, width_m); norm = float(np.linalg.norm(r))
        if norm < tolerance:
            reason = "converged"; break
        J = finite_difference_branch_jacobian(q, par, scaling, width_m)[:, :4]
        try:
            delta = np.linalg.solve(J, -r); solver = "solve"
        except np.linalg.LinAlgError:
            delta, *_ = np.linalg.lstsq(J, -r, rcond=None); solver = "lstsq_singular_state_jacobian"
        q[:4] += delta
        iterations.append({"stage_index": stage_index, "smooth_width_m": width_m, "run": "anchor", "step_index": int(round(anchor_z)), "z_W0_m": anchor_z, "iteration": k, "residual_norm": norm, "augmented_norm": norm, "correction_norm": float(np.linalg.norm(delta)), "jacobian_condition": float(np.linalg.cond(J)), "min_singular_value": float(np.linalg.svd(J, compute_uv=False)[-1]), "linear_solver": solver, "ds_scaled": 0.0})
        if not np.all(np.isfinite(q)):
            reason = "non-finite anchor Newton iterate"; break
    J = finite_difference_branch_jacobian(q, par, scaling, width_m); tangent, sv, cond = tangent_from_jacobian(J)
    row = _point_record(stage_index, width_m, "anchor", int(round(anchor_z)), q, par, scaling, tangent, sv, cond, len(iterations), reason, 0.0)
    return row, _eigen_records(stage_index, width_m, "anchor", int(round(anchor_z)), q, par, scaling), iterations


def anchor_points(stage_index: int, width_m: float, directional: pd.DataFrame, par: np.ndarray, scaling: Zw0Scaling):
    rows = []; eigs = []; iters = []
    if directional.empty: return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    lo, hi = directional.z_W0_m.min(), directional.z_W0_m.max()
    for anchor in ANCHORS_M:
        if lo - 1e-9 <= anchor <= hi + 1e-9:
            row, erows, irows = solve_anchor(stage_index, width_m, anchor, directional, par, scaling)
            rows.append(row); eigs.extend(erows); iters.extend(irows)
    return pd.DataFrame(rows), pd.DataFrame(eigs), pd.DataFrame(iters)


def run_stage(stage_index: int, width_m: float, config: Zw0Config):
    y_seed, par, scaling = zw0_seed_state_and_parameters()
    q_seed = np.r_[scaling.state_to_scaled(y_seed), scaling.control_to_scaled(par[0])]
    J0 = finite_difference_branch_jacobian(q_seed, par, scaling, width_m)
    tangent0, _sv0, _cond0 = tangent_from_jacobian(J0)
    down = continue_direction(stage_index, width_m, "downward", q_seed, -tangent0, par, scaling, config.lower_target_z_W0_m, config)
    up = continue_direction(stage_index, width_m, "upward", q_seed, tangent0, par, scaling, config.upper_target_z_W0_m, config)
    directional = pd.concat([pd.DataFrame(down[0]), pd.DataFrame(up[0])], ignore_index=True)
    anchor_df, anchor_eigs, anchor_iters = anchor_points(stage_index, width_m, directional, par, scaling)
    branch = pd.concat([directional, anchor_df], ignore_index=True)
    unique = branch.sort_values(["smooth_width_m", "z_W0_m", "run"]).drop_duplicates(["smooth_width_m", "z_W0_m"], keep="first")
    failures = pd.concat([pd.DataFrame(down[3]), pd.DataFrame(up[3])], ignore_index=True) if (down[3] or up[3]) else pd.DataFrame()
    iterations = pd.concat([pd.DataFrame(down[2]), pd.DataFrame(up[2]), anchor_iters], ignore_index=True) if (down[2] or up[2] or not anchor_iters.empty) else pd.DataFrame()
    eigen = pd.concat([pd.DataFrame(down[1]), pd.DataFrame(up[1]), anchor_eigs], ignore_index=True)
    return {"branch": branch, "unique": unique, "failures": failures, "iterations": iterations, "eigenvalues": eigen}


def classify_fragility(final_unique: pd.DataFrame, final_failures: pd.DataFrame, schedule: pd.DataFrame) -> tuple[str, str]:
    if final_unique.empty:
        return "unresolved_numerical_failure", "The sharp-width run accepted no useful non-seed branch points."
    covers_7_10 = final_unique.z_W0_m.min() <= 7000.0 + 1e-6 and final_unique.z_W0_m.max() >= 10000.0 - 1e-6
    transition_count = int(final_unique.in_9p6_10_km_transition_region.sum())
    cond_transition = float(final_unique.loc[final_unique.in_9p6_10_km_transition_region, "branch_jacobian_condition"].max()) if transition_count else float("nan")
    sharp_reaches_less = bool(schedule.loc[schedule.smooth_width_m == 50.0, "z_W0_max_m"].max() + 1e-6 < schedule.z_W0_max_m.max())
    if covers_7_10 and transition_count >= 3:
        return "branch_geometry_not_transition_fragility", "The 50 m smoothed branch covers the full 7--10 km interval with multiple accepted transition-region points; the earlier AUTO fragility is not reproduced by the Python branch geometry."
    if sharp_reaches_less:
        return "smoothing_or_nonsmoothness_sensitive", "Easier smoothing widths reach farther than the 50 m width, so transition fragility remains smoothing-width/nonsmoothness sensitive."
    if transition_count and cond_transition > 1e8:
        return "branch_geometry_or_conditioning", "Accepted transition-region points exist but show elevated branch-Jacobian conditioning, pointing to branch geometry/conditioning rather than only raw scaling."
    if not final_failures.empty:
        return "unresolved_numerical_failure", "The run stops through corrector failures before complete interval coverage; available diagnostics do not isolate geometry versus smoothing."
    return "scaling_not_primary", "Residual scaling is unchanged from successful W_a0/H_a3 Python gates and accepted residuals remain small; no evidence that q_z scaling alone is the primary limitation."


def write_doc(summary: dict[str, Any]) -> None:
    DOC.write_text(
        "# TASK-029 — staged full-model Python z_W0 continuation\n\n"
        "This episode-10 workflow follows the full Berton equilibrium branch in `z_W0` using Python pseudo-arclength continuation and the TASK-023/TASK-024 softplus-smoothed updraft.\n\n"
        "## Reproducibility\n\n```bash\nuv run python episodes/10-full-model-python-continuation/scripts/berton_full_task029_zw0_staged_smoothing.py\n```\n\n"
        "## Smoothing and physical mapping\n\n"
        "The active coordinate is `q_z=(z_W0-9000 m)/1000 m`, with inverse `z_W0=9000 m + 1000 m q_z`. "
        "The updraft is `W_a0 * eps * (softplus(x/eps)-softplus((x-1)/eps))`, where `x=(z-(z_W0-Delta_z_W))/Delta_z_W`, `eps=width/Delta_z_W`, and `Delta_z_W=300 m`. "
        f"The staged widths are `{summary['smoothing_width_schedule_m']}` m; the final width is the TASK-023/TASK-024 `50 m` setting.\n\n"
        "## Coverage\n\n"
        f"The sharp 50 m stage covers `z_W0=[{summary['final_width_z_W0_min_m']:.3f}, {summary['final_width_z_W0_max_m']:.3f}] m` with `{summary['final_width_unique_points']}` unique accepted points. "
        f"Full 7--10 km coverage: `{summary['final_width_covers_7_10_km']}`. Transition-region accepted points in 9.6--10 km: `{summary['final_width_transition_region_points']}`.\n\n"
        "## Verdict\n\n"
        f"Classification: `{summary['fragility_classification']}`. {summary['fragility_reason']}\n\n"
        "The verdict is limited to accepted equilibrium branch points saved in `full_zw0_staged_branch_points.csv`; rejected corrector steps and conditioning diagnostics are saved separately.\n"
    )


def run_all(config: Zw0Config | None = None):
    config = config or Zw0Config()
    stages = [run_stage(i, width, config) for i, width in enumerate(WIDTH_SCHEDULE_M, start=1)]
    branch = pd.concat([s["branch"] for s in stages], ignore_index=True)
    unique = pd.concat([s["unique"] for s in stages], ignore_index=True)
    failures = pd.concat([s["failures"] for s in stages if not s["failures"].empty], ignore_index=True) if any(not s["failures"].empty for s in stages) else pd.DataFrame()
    iterations = pd.concat([s["iterations"] for s in stages if not s["iterations"].empty], ignore_index=True) if any(not s["iterations"].empty for s in stages) else pd.DataFrame()
    eigen = pd.concat([s["eigenvalues"] for s in stages], ignore_index=True)
    schedule = unique.groupby("smooth_width_m").agg(z_W0_min_m=("z_W0_m", "min"), z_W0_max_m=("z_W0_m", "max"), unique_points=("z_W0_m", "nunique"), transition_region_points=("in_9p6_10_km_transition_region", "sum"), max_scaled_residual_norm=("scaled_residual_norm", "max"), max_branch_jacobian_condition=("branch_jacobian_condition", "max")).reset_index().sort_values("smooth_width_m", ascending=False)
    final_unique = unique[unique.smooth_width_m == 50.0]
    final_failures = failures[failures.smooth_width_m == 50.0] if not failures.empty and "smooth_width_m" in failures else pd.DataFrame()
    classification, reason = classify_fragility(final_unique, final_failures, schedule)
    return {"config": config, "branch": branch, "unique": unique, "failures": failures, "iterations": iterations, "eigenvalues": eigen, "schedule": schedule, "classification": classification, "reason": reason}


def write_outputs(run: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    run["branch"].to_csv(OUT_DIR / "full_zw0_staged_branch_points.csv", index=False)
    run["unique"].to_csv(OUT_DIR / "full_zw0_staged_unique_points.csv", index=False)
    run["eigenvalues"].to_csv(OUT_DIR / "full_zw0_staged_eigenvalues.csv", index=False)
    run["iterations"].to_csv(OUT_DIR / "full_zw0_staged_corrector_iterations.csv", index=False)
    run["failures"].to_csv(OUT_DIR / "full_zw0_staged_rejected_steps.csv", index=False)
    run["schedule"].to_csv(OUT_DIR / "smoothing_stage_summary.csv", index=False)
    final = run["unique"][run["unique"].smooth_width_m == 50.0]
    summary = {
        "task": "TASK-029", "coordinate_system": "TASK-026 scaled z,u,w,log(m/kg) with q_z=(z_W0-9000 m)/1000 m", "config": asdict(run["config"]),
        "smoothing_formula": "W_a0 * eps * (softplus(x/eps)-softplus((x-1)/eps)); x=(z-(z_W0-Delta_z_W))/Delta_z_W; eps=width/Delta_z_W",
        "delta_z_W_m": DELTA_Z_W_M, "smoothing_width_schedule_m": WIDTH_SCHEDULE_M, "physical_inverse_mapping": "z_W0_m = 9000 + 1000*q_z_W0_scaled",
        "accepted_points_total": int(len(run["branch"])), "accepted_unique_points_total": int(len(run["unique"])),
        "final_width_z_W0_min_m": float(final.z_W0_m.min()) if not final.empty else float("nan"), "final_width_z_W0_max_m": float(final.z_W0_m.max()) if not final.empty else float("nan"),
        "final_width_unique_points": int(len(final)), "final_width_covers_7_10_km": bool((not final.empty) and final.z_W0_m.min() <= 7000.0 + 1e-6 and final.z_W0_m.max() >= 10000.0 - 1e-6),
        "final_width_transition_region_points": int(final.in_9p6_10_km_transition_region.sum()) if not final.empty else 0,
        "final_width_anchor_values_reached_m": [float(z) for z in sorted(set(final.loc[final.run == "anchor", "z_W0_m"].round(9)))] if not final.empty else [],
        "max_scaled_residual_norm": float(run["unique"].scaled_residual_norm.max()), "max_branch_jacobian_condition": float(run["unique"].branch_jacobian_condition.max()),
        "rejected_step_count": int(len(run["failures"])), "fragility_classification": run["classification"], "fragility_reason": run["reason"],
        "output_files": ["full_zw0_staged_branch_points.csv", "full_zw0_staged_unique_points.csv", "full_zw0_staged_eigenvalues.csv", "full_zw0_staged_corrector_iterations.csv", "full_zw0_staged_rejected_steps.csv", "smoothing_stage_summary.csv", "task029_zw0_staged_verdict.json"],
    }
    (OUT_DIR / "task029_zw0_staged_verdict.json").write_text(json.dumps(summary, indent=2, sort_keys=True))
    write_doc(summary)


def main() -> None:
    run = run_all()
    write_outputs(run)
    summary = json.loads((OUT_DIR / "task029_zw0_staged_verdict.json").read_text())
    print(f"Wrote TASK-029 z_W0 staged diagnostics to {OUT_DIR}")
    print(f"Verdict={summary['fragility_classification']}: {summary['fragility_reason']}")


if __name__ == "__main__":
    main()
