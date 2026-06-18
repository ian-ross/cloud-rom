"""TASK-032 full-model sensitivity map for updraft smoothing width.

Run from repository root::

    uv run python episodes/10-full-model-python-continuation/scripts/berton_full_task032_smoothing_width_map.py

This workflow treats the updraft smoothing width as a continuation/sensitivity
parameter.  It reuses the TASK-029 smoothed full-model residual and maps fixed
``z_W0`` equilibria as the width is sharpened through and below the 50 m
TASK-023/TASK-024 setting.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
EPISODE_ROOT = SCRIPT_DIR.parents[0]
OUT_DIR = EPISODE_ROOT / "outputs" / "task032"
DOC = EPISODE_ROOT / "docs" / "task032_smoothing_width_sensitivity.md"
TASK029_OUT = EPISODE_ROOT / "outputs" / "task029"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from berton_full_task026_continuation import tangent_from_jacobian  # noqa: E402
from berton_full_task029_zw0_staged_smoothing import (  # noqa: E402
    DELTA_Z_W_M,
    TRANSITION_MAX_M,
    TRANSITION_MIN_M,
    Zw0Scaling,
    fd_jacobian_physical_smoothed,
    finite_difference_branch_jacobian as z_branch_jacobian,
    piecewise_updraft_value,
    python_rhs_smoothed,
    q_residual as z_q_residual,
    smoothed_updraft_value,
    transformed_rhs_smoothed,
    zw0_seed_state_and_parameters,
)

WIDTH_ANCHORS_M = [300.0, 200.0, 150.0, 100.0, 75.0, 50.0, 35.0, 25.0, 10.0]
FIXED_Z_ANCHORS_M = [9600.0, 9700.0, 9800.0, 9900.0, 9930.0]
MAP_Z_ANCHORS_M = [9600.0, 9700.0, 9800.0, 9900.0, 9930.0, 9950.0, 10000.0]
WIDTH_REF_M = 50.0


@dataclass(frozen=True)
class Task032Config:
    residual_tolerance: float = 3.0e-6
    newton_tolerance: float = 1.0e-8
    max_newton_iterations: int = 14
    fd_step: float = 1.0e-5


def width_to_mu(width_m: float) -> float:
    """Positive-width continuation coordinate: ``mu=log(width/50 m)``."""
    if width_m <= 0.0:
        raise ValueError(f"width must be positive, got {width_m}")
    return float(np.log(width_m / WIDTH_REF_M))


def mu_to_width(mu: float) -> float:
    return float(WIDTH_REF_M * np.exp(mu))


def scaled_residual_fixed_width(x: np.ndarray, z_w0_m: float, width_m: float, par_template: np.ndarray, scaling: Zw0Scaling) -> np.ndarray:
    """Scaled residual with a finite sentinel for invalid Newton trials."""
    try:
        y = scaling.scaled_to_state(x)
        if not np.all(np.isfinite(y)) or y[3] <= 0.0:
            return np.full(4, 1.0e30)
        par = par_template.copy(); par[0] = float(z_w0_m)
        r = scaling.residual_scale_vector * transformed_rhs_smoothed(y, par, width_m)
        return r if np.all(np.isfinite(r)) else np.full(4, 1.0e30)
    except Exception:
        return np.full(4, 1.0e30)


def fixed_state_jacobian(x: np.ndarray, z_w0_m: float, width_m: float, par_template: np.ndarray, scaling: Zw0Scaling, h: float = 1e-5) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    J = np.zeros((4, 4), dtype=float)
    for i in range(4):
        step = h * max(1.0, abs(x[i]))
        xp = x.copy(); xm = x.copy(); xp[i] += step; xm[i] -= step
        J[:, i] = (scaled_residual_fixed_width(xp, z_w0_m, width_m, par_template, scaling) - scaled_residual_fixed_width(xm, z_w0_m, width_m, par_template, scaling)) / (xp[i] - xm[i])
    return J


def width_branch_residual(q: np.ndarray, z_w0_m: float, par_template: np.ndarray, scaling: Zw0Scaling) -> np.ndarray:
    return scaled_residual_fixed_width(q[:4], z_w0_m, mu_to_width(float(q[4])), par_template, scaling)


def width_branch_jacobian(q: np.ndarray, z_w0_m: float, par_template: np.ndarray, scaling: Zw0Scaling, h: float = 1e-5) -> np.ndarray:
    q = np.asarray(q, dtype=float)
    J = np.zeros((4, 5), dtype=float)
    for i in range(5):
        step = h * max(1.0, abs(q[i]))
        qp = q.copy(); qm = q.copy(); qp[i] += step; qm[i] -= step
        J[:, i] = (width_branch_residual(qp, z_w0_m, par_template, scaling) - width_branch_residual(qm, z_w0_m, par_template, scaling)) / (qp[i] - qm[i])
    return J


def solve_fixed_point(
    x0: np.ndarray,
    z_w0_m: float,
    width_m: float,
    par_template: np.ndarray,
    scaling: Zw0Scaling,
    config: Task032Config,
) -> tuple[bool, np.ndarray, list[dict[str, Any]], str]:
    x = np.array(x0, dtype=float)
    iterations: list[dict[str, Any]] = []
    reason = "maximum Newton iterations reached"
    accepted = False
    for k in range(config.max_newton_iterations):
        r = scaled_residual_fixed_width(x, z_w0_m, width_m, par_template, scaling)
        norm = float(np.linalg.norm(r))
        if norm < config.newton_tolerance:
            reason = "converged"
            accepted = True
            break
        J = fixed_state_jacobian(x, z_w0_m, width_m, par_template, scaling, config.fd_step)
        sv = np.linalg.svd(J, compute_uv=False)
        cond = float(sv[0] / sv[-1]) if sv[-1] > 0.0 else float("inf")
        try:
            delta = np.linalg.solve(J, -r); solver = "solve"
        except np.linalg.LinAlgError:
            delta, *_ = np.linalg.lstsq(J, -r, rcond=None); solver = "lstsq_singular_state_jacobian"
        # Damped Newton: reject steps that leave the physically evaluable basin.
        step_factor = 1.0
        x_trial = x + delta
        trial_norm = float(np.linalg.norm(scaled_residual_fixed_width(x_trial, z_w0_m, width_m, par_template, scaling)))
        while (not np.isfinite(trial_norm) or trial_norm > max(norm, 1.0e-20)) and step_factor > 1.0e-4:
            step_factor *= 0.5
            x_trial = x + step_factor * delta
            trial_norm = float(np.linalg.norm(scaled_residual_fixed_width(x_trial, z_w0_m, width_m, par_template, scaling)))
        x = x_trial
        iterations.append({
            "iteration": k, "residual_norm": norm, "correction_norm": float(np.linalg.norm(step_factor * delta)),
            "state_jacobian_condition": cond, "state_jacobian_min_singular_value": float(sv[-1]), "linear_solver": solver, "step_factor": float(step_factor),
        })
        if not np.all(np.isfinite(x)):
            reason = "non-finite Newton iterate"
            break
    final_norm = float(np.linalg.norm(scaled_residual_fixed_width(x, z_w0_m, width_m, par_template, scaling))) if np.all(np.isfinite(x)) else float("inf")
    if final_norm < config.residual_tolerance:
        accepted = True
        if reason == "maximum Newton iterations reached":
            reason = "residual accepted after maximum iterations"
    return accepted, x, iterations, reason


def initial_guess_from_task029(z_w0_m: float, width_m: float, scaling: Zw0Scaling) -> np.ndarray:
    branch = pd.read_csv(TASK029_OUT / "full_zw0_staged_unique_points.csv")
    available = sorted(branch.smooth_width_m.unique(), key=lambda w: abs(w - width_m))
    for w in available:
        subset = branch[branch.smooth_width_m == w].sort_values("z_W0_m")
        if subset.z_W0_m.min() - 1e-6 <= z_w0_m <= subset.z_W0_m.max() + 1e-6:
            return np.array([
                np.interp(z_w0_m, subset.z_W0_m, subset.scaled_x0_z),
                np.interp(z_w0_m, subset.z_W0_m, subset.scaled_x1_u),
                np.interp(z_w0_m, subset.z_W0_m, subset.scaled_x2_w),
                np.interp(z_w0_m, subset.z_W0_m, subset.scaled_x3_log_m),
            ], dtype=float)
    # Fallback to the physical seed state.
    y, _par, _scaling = zw0_seed_state_and_parameters()
    return scaling.state_to_scaled(y)


def point_record(
    experiment: str,
    z_w0_m: float,
    width_m: float,
    x: np.ndarray,
    par_template: np.ndarray,
    scaling: Zw0Scaling,
    accepted: bool,
    reason: str,
    iterations: int,
) -> dict[str, Any]:
    y = scaling.scaled_to_state(x)
    par = par_template.copy(); par[0] = float(z_w0_m)
    rhs = python_rhs_smoothed(y, par, width_m)
    transformed = transformed_rhs_smoothed(y, par, width_m)
    scaled = scaled_residual_fixed_width(x, z_w0_m, width_m, par_template, scaling)
    state_J = fixed_state_jacobian(x, z_w0_m, width_m, par_template, scaling)
    state_sv = np.linalg.svd(state_J, compute_uv=False)
    width_q = np.r_[x, width_to_mu(width_m)]
    width_J = width_branch_jacobian(width_q, z_w0_m, par_template, scaling)
    width_tangent, width_sv, width_cond = tangent_from_jacobian(width_J)
    z_q = np.r_[x, scaling.control_to_scaled(z_w0_m)]
    z_J = z_branch_jacobian(z_q, par_template, scaling, width_m)
    z_tangent, z_sv, z_cond = tangent_from_jacobian(z_J)
    eig = np.linalg.eigvals(fd_jacobian_physical_smoothed(y, par, width_m))
    critical = eig[np.argmax(eig.real)]
    w_s = smoothed_updraft_value(float(y[0]), float(z_w0_m), float(par[1]), float(par[6]), width_m)
    w_p = piecewise_updraft_value(float(y[0]), float(z_w0_m), float(par[1]), float(par[6]))
    return {
        "experiment": experiment, "accepted": bool(accepted), "reason": reason, "z_W0_m": float(z_w0_m), "z_W0_km": float(z_w0_m / 1000.0),
        "smooth_width_m": float(width_m), "mu_log_width_over_50m": float(width_to_mu(width_m)), "width_inverse_mapping": "width_m = 50*exp(mu)",
        "q_z_W0_scaled": float(scaling.control_to_scaled(z_w0_m)), "z_m": float(y[0]), "u_m_s": float(y[1]), "w_m_s": float(y[2]), "m_kg": float(y[3]),
        "scaled_x0_z": float(x[0]), "scaled_x1_u": float(x[1]), "scaled_x2_w": float(x[2]), "scaled_x3_log_m": float(x[3]),
        "physical_residual_norm": float(np.linalg.norm(rhs)), "transformed_residual_norm": float(np.linalg.norm(transformed)), "scaled_residual_norm": float(np.linalg.norm(scaled)),
        "max_abs_scaled_residual": float(np.max(np.abs(scaled))), "newton_iterations": int(iterations),
        "state_jacobian_condition": float(state_sv[0] / state_sv[-1]) if state_sv[-1] > 0 else float("inf"),
        "state_jacobian_min_singular_value": float(state_sv[-1]), "state_jacobian_max_singular_value": float(state_sv[0]),
        "width_branch_condition": float(width_cond), "width_branch_min_singular_value": float(width_sv[-1]), "width_branch_max_singular_value": float(width_sv[0]),
        "width_tangent_mu": float(width_tangent[4]), "width_tangent_state_norm": float(np.linalg.norm(width_tangent[:4])),
        "z_branch_condition": float(z_cond), "z_branch_min_singular_value": float(z_sv[-1]), "z_branch_max_singular_value": float(z_sv[0]), "z_tangent_lambda": float(z_tangent[4]),
        "critical_real_s_inv": float(critical.real), "critical_imag_s_inv": float(critical.imag), "stable_eigenvalue_count": int(np.sum(eig.real < 0.0)),
        "smoothed_W_a_m_s": float(w_s), "piecewise_W_a_m_s": float(w_p), "updraft_difference_m_s": float(w_s - w_p),
        "distance_to_z_W0_m": float(y[0] - z_w0_m), "distance_to_ramp_base_m": float(y[0] - (z_w0_m - par[6])),
        "in_transition_region": bool(TRANSITION_MIN_M <= z_w0_m <= TRANSITION_MAX_M),
    }


def eigen_records(record: dict[str, Any], x: np.ndarray, par_template: np.ndarray, scaling: Zw0Scaling) -> list[dict[str, Any]]:
    y = scaling.scaled_to_state(x)
    par = par_template.copy(); par[0] = float(record["z_W0_m"])
    eigs = np.linalg.eigvals(fd_jacobian_physical_smoothed(y, par, float(record["smooth_width_m"])))
    return [{"experiment": record["experiment"], "z_W0_m": record["z_W0_m"], "smooth_width_m": record["smooth_width_m"], "eigenvalue_index": i, "real_s_inv": float(e.real), "imag_s_inv": float(e.imag)} for i, e in enumerate(eigs)]


def run_fixed_z_paths(config: Task032Config, par: np.ndarray, scaling: Zw0Scaling):
    rows: list[dict[str, Any]] = []
    eig_rows: list[dict[str, Any]] = []
    iter_rows: list[dict[str, Any]] = []
    reject_rows: list[dict[str, Any]] = []
    for z_w0 in FIXED_Z_ANCHORS_M:
        x = initial_guess_from_task029(z_w0, 300.0, scaling)
        for width in WIDTH_ANCHORS_M:
            accepted, x_new, iterations, reason = solve_fixed_point(x, z_w0, width, par, scaling, config)
            for it in iterations:
                rr = dict(it); rr.update({"experiment": "fixed_z_width_path", "z_W0_m": z_w0, "smooth_width_m": width})
                iter_rows.append(rr)
            rec = point_record("fixed_z_width_path", z_w0, width, x_new, par, scaling, accepted, reason, len(iterations))
            if accepted:
                rows.append(rec); eig_rows.extend(eigen_records(rec, x_new, par, scaling)); x = x_new
            else:
                reject_rows.append(rec)
                # Keep the previous accepted state for the next width rather than following a failed Newton iterate.
    return pd.DataFrame(rows), pd.DataFrame(eig_rows), pd.DataFrame(iter_rows), pd.DataFrame(reject_rows)


def run_two_parameter_map(config: Task032Config, par: np.ndarray, scaling: Zw0Scaling, fixed_rows: pd.DataFrame):
    rows: list[dict[str, Any]] = []
    eig_rows: list[dict[str, Any]] = []
    reject_rows: list[dict[str, Any]] = []
    iter_rows: list[dict[str, Any]] = []
    last_by_width: dict[float, np.ndarray] = {}
    for width in WIDTH_ANCHORS_M:
        for z_w0 in MAP_Z_ANCHORS_M:
            seed_candidates = fixed_rows[(np.isclose(fixed_rows.smooth_width_m, width)) & (np.isclose(fixed_rows.z_W0_m, z_w0))] if not fixed_rows.empty else pd.DataFrame()
            if not seed_candidates.empty:
                r = seed_candidates.iloc[0]
                x0 = np.array([r.scaled_x0_z, r.scaled_x1_u, r.scaled_x2_w, r.scaled_x3_log_m], dtype=float)
            elif width in last_by_width:
                x0 = last_by_width[width]
            else:
                x0 = initial_guess_from_task029(z_w0, width, scaling)
            accepted, x_new, iterations, reason = solve_fixed_point(x0, z_w0, width, par, scaling, config)
            for it in iterations:
                rr = dict(it); rr.update({"experiment": "two_parameter_map", "z_W0_m": z_w0, "smooth_width_m": width})
                iter_rows.append(rr)
            rec = point_record("two_parameter_map", z_w0, width, x_new, par, scaling, accepted, reason, len(iterations))
            if accepted:
                rows.append(rec); eig_rows.extend(eigen_records(rec, x_new, par, scaling)); last_by_width[width] = x_new
            else:
                reject_rows.append(rec)
    return pd.DataFrame(rows), pd.DataFrame(eig_rows), pd.DataFrame(iter_rows), pd.DataFrame(reject_rows)


def classify(summary_map: pd.DataFrame, rejects: pd.DataFrame) -> tuple[str, str]:
    if summary_map.empty:
        return "unresolved_numerical_failure", "No accepted smoothing-width sensitivity points were obtained."
    sharp = summary_map[np.isclose(summary_map.smooth_width_m, 50.0)]
    subsharp = summary_map[summary_map.smooth_width_m < 50.0]
    reaches_10000_50 = bool((np.isclose(sharp.z_W0_m, 10000.0)).any())
    reaches_9930_sub = bool((subsharp.z_W0_m >= 9930.0).any())
    max_state_cond = float(summary_map.state_jacobian_condition.max())
    min_state_sv = float(summary_map.state_jacobian_min_singular_value.min())
    max_width_cond = float(summary_map.width_branch_condition.max())
    if reaches_10000_50 and reaches_9930_sub and (max_state_cond > 1.0e8 or max_width_cond > 1.0e8):
        return "near_singular_sharp_limit_not_50m_nonexistence", "Fixed-z_W0 solves reach the previously obstructed 50 m and sub-50 m region, so the TASK-029 z-continuation stop is not evidence of equilibrium nonexistence at 50 m; however conditioning grows sharply as the profile is further sharpened, supporting a near-singular smoothing-limit interpretation."
    if reaches_10000_50 and reaches_9930_sub and max_state_cond < 1.0e6:
        return "path_dependent_not_fold_limited", "Fixed-width and fixed-z_W0 Newton/continuation solves reach the previously obstructed region without near-singular state Jacobians; the TASK-029 obstruction is more path/regularity sensitive than a hard equilibrium nonexistence boundary."
    if min_state_sv < 1.0e-6 or max_state_cond > 1.0e8 or max_width_cond > 1.0e8:
        return "near_singular_branch_geometry", "Accepted points show very small state/branch singular values or very large condition estimates, supporting a fold-like or near-singular branch-geometry interpretation."
    if not rejects.empty and (rejects.smooth_width_m <= 50.0).any():
        return "singular_smoothing_or_numerical_limit", "Failures concentrate at or below the 50 m smoothing width without decisive singular-Jacobian evidence, so the obstruction remains a singular smoothing/nonsmoothness or unresolved numerical-limit effect."
    return "regularity_sensitive_no_fold_detected", "The smoothing-width map does not show fold-like singular diagnostics over accepted points; sensitivity appears tied to regularity/path dependence rather than q_z scaling."


def write_doc(summary: dict[str, Any]) -> None:
    DOC.write_text(
        "# TASK-032 — smoothing-width sensitivity map\n\n"
        "TASK-032 treats updraft smoothing width as a scientific parameter rather than only a numerical staging aid.\n\n"
        "## Reproducibility\n\n```bash\nuv run python episodes/10-full-model-python-continuation/scripts/berton_full_task032_smoothing_width_map.py\n```\n\n"
        "## Coordinates\n\n"
        "The fixed-z_W0 smoothing continuation uses `mu=log(width_m/50 m)`, with inverse `width_m=50*exp(mu)`. "
        "The z_W0 coordinate remains `q_z=(z_W0-9000 m)/1000 m`.\n\n"
        "## Coverage\n\n"
        f"Fixed-z_W0 anchors: `{summary['fixed_z_anchors_m']}` m. Width anchors: `{summary['width_anchors_m']}` m. "
        f"Accepted fixed-z path points: `{summary['fixed_z_accepted_points']}`; accepted two-parameter map points: `{summary['map_accepted_points']}`.\n\n"
        "## Geometry diagnostics\n\n"
        f"Minimum accepted fixed-control state-Jacobian singular value: `{summary['min_state_jacobian_singular_value']:.3e}`. "
        f"Maximum state-Jacobian condition: `{summary['max_state_jacobian_condition']:.3e}`. "
        f"Maximum width-branch condition: `{summary['max_width_branch_condition']:.3e}`.\n\n"
        "## Verdict\n\n"
        f"Classification: `{summary['classification']}`. {summary['classification_reason']}\n\n"
        "This verdict is limited to Newton-refined equilibrium points and pseudo-arclength-style width branch diagnostics; it does not by itself prove a global two-parameter bifurcation diagram.\n"
    )


def run_all(config: Task032Config | None = None) -> dict[str, Any]:
    config = config or Task032Config()
    _y, par, scaling = zw0_seed_state_and_parameters()
    fixed, fixed_eigs, fixed_iters, fixed_rejects = run_fixed_z_paths(config, par, scaling)
    mapped, map_eigs, map_iters, map_rejects = run_two_parameter_map(config, par, scaling, fixed)
    all_accepted = pd.concat([fixed, mapped], ignore_index=True)
    all_rejects = pd.concat([fixed_rejects, map_rejects], ignore_index=True) if (not fixed_rejects.empty or not map_rejects.empty) else pd.DataFrame()
    classification, reason = classify(all_accepted, all_rejects)
    return {"config": config, "fixed": fixed, "fixed_eigs": fixed_eigs, "fixed_iters": fixed_iters, "fixed_rejects": fixed_rejects, "map": mapped, "map_eigs": map_eigs, "map_iters": map_iters, "map_rejects": map_rejects, "all_accepted": all_accepted, "all_rejects": all_rejects, "classification": classification, "reason": reason}


def write_outputs(run: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    run["fixed"].to_csv(OUT_DIR / "fixed_z_width_continuation_points.csv", index=False)
    run["fixed_eigs"].to_csv(OUT_DIR / "fixed_z_width_eigenvalues.csv", index=False)
    run["fixed_iters"].to_csv(OUT_DIR / "fixed_z_width_newton_iterations.csv", index=False)
    fixed_rejects = run["fixed_rejects"] if not run["fixed_rejects"].empty else pd.DataFrame(columns=run["fixed"].columns)
    fixed_rejects.to_csv(OUT_DIR / "fixed_z_width_rejected_points.csv", index=False)
    run["map"].to_csv(OUT_DIR / "zw0_width_map_points.csv", index=False)
    run["map_eigs"].to_csv(OUT_DIR / "zw0_width_map_eigenvalues.csv", index=False)
    run["map_iters"].to_csv(OUT_DIR / "zw0_width_map_newton_iterations.csv", index=False)
    map_rejects = run["map_rejects"] if not run["map_rejects"].empty else pd.DataFrame(columns=run["map"].columns)
    map_rejects.to_csv(OUT_DIR / "zw0_width_map_rejected_points.csv", index=False)
    accepted = run["all_accepted"]
    grid = accepted.groupby("smooth_width_m").agg(z_W0_min_m=("z_W0_m", "min"), z_W0_max_m=("z_W0_m", "max"), accepted_points=("z_W0_m", "count"), max_state_jacobian_condition=("state_jacobian_condition", "max"), min_state_jacobian_singular_value=("state_jacobian_min_singular_value", "min"), max_width_branch_condition=("width_branch_condition", "max")).reset_index() if not accepted.empty else pd.DataFrame()
    grid.to_csv(OUT_DIR / "width_summary.csv", index=False)
    summary = {
        "task": "TASK-032", "config": asdict(run["config"]), "fixed_z_anchors_m": FIXED_Z_ANCHORS_M, "map_z_anchors_m": MAP_Z_ANCHORS_M, "width_anchors_m": WIDTH_ANCHORS_M,
        "width_coordinate": "mu=log(width_m/50 m)", "width_inverse_mapping": "width_m=50*exp(mu)", "z_W0_coordinate": "q_z=(z_W0-9000 m)/1000 m",
        "fixed_z_accepted_points": int(len(run["fixed"])), "fixed_z_rejected_points": int(len(run["fixed_rejects"])), "map_accepted_points": int(len(run["map"])), "map_rejected_points": int(len(run["map_rejects"])),
        "accepted_points_total": int(len(accepted)), "rejected_points_total": int(len(run["all_rejects"])),
        "min_state_jacobian_singular_value": float(accepted.state_jacobian_min_singular_value.min()) if not accepted.empty else float("nan"),
        "max_state_jacobian_condition": float(accepted.state_jacobian_condition.max()) if not accepted.empty else float("nan"),
        "max_width_branch_condition": float(accepted.width_branch_condition.max()) if not accepted.empty else float("nan"),
        "max_z_branch_condition": float(accepted.z_branch_condition.max()) if not accepted.empty else float("nan"),
        "max_scaled_residual_norm": float(accepted.scaled_residual_norm.max()) if not accepted.empty else float("nan"),
        "accepted_50m_z_values_m": sorted(float(v) for v in accepted.loc[np.isclose(accepted.smooth_width_m, 50.0), "z_W0_m"].unique()) if not accepted.empty else [],
        "accepted_below_50m_z_values_m": sorted(float(v) for v in accepted.loc[accepted.smooth_width_m < 50.0, "z_W0_m"].unique()) if not accepted.empty else [],
        "classification": run["classification"], "classification_reason": run["reason"],
        "output_files": ["fixed_z_width_continuation_points.csv", "fixed_z_width_eigenvalues.csv", "fixed_z_width_newton_iterations.csv", "fixed_z_width_rejected_points.csv", "zw0_width_map_points.csv", "zw0_width_map_eigenvalues.csv", "zw0_width_map_newton_iterations.csv", "zw0_width_map_rejected_points.csv", "width_summary.csv", "task032_smoothing_width_verdict.json"],
    }
    (OUT_DIR / "task032_smoothing_width_verdict.json").write_text(json.dumps(summary, indent=2, sort_keys=True))
    write_doc(summary)


def main() -> None:
    run = run_all()
    write_outputs(run)
    summary = json.loads((OUT_DIR / "task032_smoothing_width_verdict.json").read_text())
    print(f"Wrote TASK-032 smoothing-width sensitivity diagnostics to {OUT_DIR}")
    print(f"Verdict={summary['classification']}: {summary['classification_reason']}")


if __name__ == "__main__":
    main()
