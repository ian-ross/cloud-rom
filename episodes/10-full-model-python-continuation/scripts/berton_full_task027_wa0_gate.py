"""TASK-027 full-model Python continuation gate in W_a0.

Run from the repository root with::

    uv run python episodes/10-full-model-python-continuation/scripts/berton_full_task027_wa0_gate.py

This script applies the TASK-026 pseudo-arclength core to a longer full-model
Berton equilibrium branch in ``W_a0`` before any Hopf-focused controls.
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
OUT_DIR = EPISODE_ROOT / "outputs" / "task027"
DOC = EPISODE_ROOT / "docs" / "task027_wa0_full_model_gate.md"
TASK012_PROBE = REPO_ROOT / "episodes" / "06-full-model-auto-seed-continuation" / "outputs" / "task012" / "python_equilibrium_control_probe.csv"
TASK019_OUT = REPO_ROOT / "episodes" / "07-restricted-equilibrium-auto" / "outputs" / "task019"

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from berton_full_task026_continuation import (  # noqa: E402
    ContinuationConfig,
    Scaling,
    corrector,
    finite_difference_branch_jacobian,
    q_residual,
    seed_state_and_parameters,
    tangent_from_jacobian,
    transformed_rhs_from_physical,
)
from berton_full_auto_task009_validate import finite_difference_jacobian, python_rhs  # noqa: E402


ANCHORS = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2]
COMPARISON_ANCHORS = [0.5, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2]


@dataclass(frozen=True)
class GateConfig:
    upward_target_W_a0_m_s: float = 1.2
    downward_target_W_a0_m_s: float = 0.1
    ds_initial: float = 0.20
    ds_min: float = 0.01
    ds_max: float = 0.35
    max_steps_per_direction: int = 120
    residual_acceptance_tolerance: float = 2.0e-6
    newton_tolerance: float = 1.0e-7


def _point_record(
    run: str,
    step_index: int,
    q: np.ndarray,
    par_template: np.ndarray,
    scaling: Scaling,
    tangent: np.ndarray,
    branch_singular_values: np.ndarray,
    branch_condition: float,
    corrector_iterations: int,
    corrector_reason: str,
    ds_scaled: float,
) -> dict[str, Any]:
    y = scaling.scaled_to_state(q[:4])
    par = par_template.copy(); par[1] = scaling.scaled_to_control(q[4])
    physical_rhs = python_rhs(y, par)
    transformed_rhs = transformed_rhs_from_physical(y, par)
    scaled_residual = q_residual(q, par_template, scaling)
    eig = np.linalg.eigvals(finite_difference_jacobian(y, par))
    critical = eig[np.argmax(eig.real)]
    stable_count = int(np.sum(eig.real < 0.0))
    return {
        "run": run,
        "step_index": step_index,
        "accepted": True,
        "W_a0_m_s": float(par[1]),
        "lambda_W_a0_scaled": float(q[4]),
        "z_m": float(y[0]),
        "u_m_s": float(y[1]),
        "w_m_s": float(y[2]),
        "m_kg": float(y[3]),
        "log_m_kg": float(np.log(y[3])),
        "scaled_x0_z": float(q[0]),
        "scaled_x1_u": float(q[1]),
        "scaled_x2_w": float(q[2]),
        "scaled_x3_log_m": float(q[3]),
        "physical_residual_norm": float(np.linalg.norm(physical_rhs)),
        "transformed_residual_norm": float(np.linalg.norm(transformed_rhs)),
        "scaled_residual_norm": float(np.linalg.norm(scaled_residual)),
        "max_abs_scaled_residual": float(np.max(np.abs(scaled_residual))),
        "critical_real_s_inv": float(critical.real),
        "critical_imag_s_inv": float(critical.imag),
        "stable_eigenvalue_count": stable_count,
        "branch_jacobian_condition": float(branch_condition),
        "branch_min_singular_value": float(branch_singular_values[-1]),
        "branch_max_singular_value": float(branch_singular_values[0]),
        "tangent_lambda_W_a0": float(tangent[4]),
        "ds_scaled": float(ds_scaled),
        "corrector_iterations": int(corrector_iterations),
        "corrector_reason": corrector_reason,
    }


def _eigen_records(run: str, step_index: int, q: np.ndarray, par_template: np.ndarray, scaling: Scaling) -> list[dict[str, Any]]:
    y = scaling.scaled_to_state(q[:4])
    par = par_template.copy(); par[1] = scaling.scaled_to_control(q[4])
    eigs = np.linalg.eigvals(finite_difference_jacobian(y, par))
    return [
        {
            "run": run,
            "step_index": step_index,
            "W_a0_m_s": float(par[1]),
            "eigenvalue_index": i,
            "real_s_inv": float(e.real),
            "imag_s_inv": float(e.imag),
        }
        for i, e in enumerate(eigs)
    ]


def continue_direction(
    run: str,
    q_seed: np.ndarray,
    tangent_seed: np.ndarray,
    par: np.ndarray,
    scaling: Scaling,
    target_W: float,
    config: GateConfig,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Follow one oriented W_a0 direction with adaptive pseudo-arclength steps."""
    cont_cfg = ContinuationConfig(ds=config.ds_initial, correction_tolerance=config.newton_tolerance)
    direction = 1.0 if target_W > scaling.scaled_to_control(q_seed[4]) else -1.0
    tangent = np.array(tangent_seed, dtype=float)
    if np.sign(tangent[4]) != np.sign(direction):
        tangent = -tangent
    q = np.array(q_seed, dtype=float)
    ds = config.ds_initial
    rows: list[dict[str, Any]] = []
    eig_rows: list[dict[str, Any]] = []
    iter_rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []

    J = finite_difference_branch_jacobian(q, par, scaling, cont_cfg.finite_difference_step)
    tangent, sv, cond = tangent_from_jacobian(J, previous=tangent)
    if np.sign(tangent[4]) != np.sign(direction):
        tangent = -tangent
    rows.append(_point_record(run, 0, q, par, scaling, tangent, sv, cond, 0, "seed", 0.0))
    eig_rows.extend(_eigen_records(run, 0, q, par, scaling))

    for step in range(1, config.max_steps_per_direction + 1):
        current_W = scaling.scaled_to_control(q[4])
        if (direction > 0 and current_W >= target_W - 1e-9) or (direction < 0 and current_W <= target_W + 1e-9):
            break
        # Avoid deliberate overshoot of the requested endpoint in control space.
        predicted_dW = scaling.W_a0_scale_m_s * ds * tangent[4]
        remaining = target_W - current_W
        trial_ds = ds
        if predicted_dW != 0 and abs(predicted_dW) > abs(remaining):
            trial_ds = max(config.ds_min, abs(0.98 * remaining / (scaling.W_a0_scale_m_s * tangent[4])))
        q_pred = q + trial_ds * tangent
        trial_cfg = ContinuationConfig(ds=trial_ds, correction_tolerance=config.newton_tolerance)
        result = corrector(q_pred, tangent, par, scaling, trial_cfg)
        if not result.accepted or result.final_residual_norm > config.residual_acceptance_tolerance:
            failures.append({
                "run": run,
                "attempted_step_index": step,
                "start_W_a0_m_s": float(current_W),
                "trial_ds_scaled": float(trial_ds),
                "accepted": bool(result.accepted),
                "reason": result.reason,
                "final_scaled_residual_norm": float(result.final_residual_norm),
                "augmented_jacobian_condition": float(result.jacobian_condition),
            })
            ds *= 0.5
            if ds < config.ds_min:
                break
            continue

        q_new = result.q
        new_W = scaling.scaled_to_control(q_new[4])
        if (new_W - current_W) * direction <= 0.0:
            failures.append({
                "run": run,
                "attempted_step_index": step,
                "start_W_a0_m_s": float(current_W),
                "trial_ds_scaled": float(trial_ds),
                "accepted": True,
                "reason": "corrected point moved opposite requested W_a0 direction",
                "final_scaled_residual_norm": float(result.final_residual_norm),
                "augmented_jacobian_condition": float(result.jacobian_condition),
            })
            ds *= 0.5
            if ds < config.ds_min:
                break
            continue

        for it in result.iterations:
            row = dict(it)
            row.update({"run": run, "step_index": step, "W_a0_m_s": float(new_W), "ds_scaled": float(trial_ds)})
            iter_rows.append(row)
        J_new = finite_difference_branch_jacobian(q_new, par, scaling, cont_cfg.finite_difference_step)
        tangent_new, sv_new, cond_new = tangent_from_jacobian(J_new, previous=tangent)
        if np.sign(tangent_new[4]) != np.sign(direction):
            tangent_new = -tangent_new
        rows.append(_point_record(run, step, q_new, par, scaling, tangent_new, sv_new, cond_new, len(result.iterations), result.reason, trial_ds))
        eig_rows.extend(_eigen_records(run, step, q_new, par, scaling))
        q = q_new
        tangent = tangent_new
        ds = min(config.ds_max, max(config.ds_min, trial_ds * 1.25 if len(result.iterations) <= 5 else trial_ds))

    return rows, eig_rows, iter_rows, failures


def solve_fixed_control_anchor(
    anchor_W: float,
    branch: pd.DataFrame,
    par: np.ndarray,
    scaling: Scaling,
    tolerance: float = 1e-9,
    max_iterations: int = 10,
) -> tuple[np.ndarray, list[dict[str, Any]], str]:
    """Newton-refine an accepted branch point at an exact W_a0 anchor."""
    b = branch.sort_values("W_a0_m_s").drop_duplicates("W_a0_m_s")
    q0 = np.array([
        np.interp(anchor_W, b.W_a0_m_s, b.scaled_x0_z),
        np.interp(anchor_W, b.W_a0_m_s, b.scaled_x1_u),
        np.interp(anchor_W, b.W_a0_m_s, b.scaled_x2_w),
        np.interp(anchor_W, b.W_a0_m_s, b.scaled_x3_log_m),
        scaling.control_to_scaled(anchor_W),
    ], dtype=float)
    q = q0.copy()
    iterations: list[dict[str, Any]] = []
    for k in range(max_iterations):
        r = q_residual(q, par, scaling)
        norm = float(np.linalg.norm(r))
        if norm < tolerance:
            return q, iterations, "converged"
        J = finite_difference_branch_jacobian(q, par, scaling)[:, :4]
        cond = float(np.linalg.cond(J))
        try:
            delta = np.linalg.solve(J, -r)
            solver = "solve"
        except np.linalg.LinAlgError:
            delta, *_ = np.linalg.lstsq(J, -r, rcond=None)
            solver = "lstsq_singular_state_jacobian"
        q[:4] += delta
        iterations.append({
            "run": "anchor",
            "step_index": int(round(anchor_W * 1000)),
            "W_a0_m_s": float(anchor_W),
            "iteration": k,
            "residual_norm": norm,
            "augmented_norm": norm,
            "correction_norm": float(np.linalg.norm(delta)),
            "jacobian_condition": cond,
            "min_singular_value": float(np.linalg.svd(J, compute_uv=False)[-1]),
            "linear_solver": solver,
            "ds_scaled": 0.0,
        })
        if not np.all(np.isfinite(q)):
            return q, iterations, "non-finite anchor Newton iterate"
    return q, iterations, "maximum anchor Newton iterations reached"


def anchor_points(branch: pd.DataFrame, anchors: list[float], par: np.ndarray, scaling: Scaling) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rows: list[dict[str, Any]] = []
    eig_rows: list[dict[str, Any]] = []
    iter_rows: list[dict[str, Any]] = []
    b = branch.sort_values("W_a0_m_s").drop_duplicates("W_a0_m_s")
    for i, anchor in enumerate(anchors, start=1):
        if anchor < b.W_a0_m_s.min() - 1e-9 or anchor > b.W_a0_m_s.max() + 1e-9:
            continue
        q, iterations, reason = solve_fixed_control_anchor(anchor, b, par, scaling)
        iter_rows.extend(iterations)
        J = finite_difference_branch_jacobian(q, par, scaling)
        tangent, sv, cond = tangent_from_jacobian(J)
        rows.append(_point_record("anchor", i, q, par, scaling, tangent, sv, cond, len(iterations), reason, 0.0))
        eig_rows.extend(_eigen_records("anchor", i, q, par, scaling))
    return pd.DataFrame(rows), pd.DataFrame(eig_rows), pd.DataFrame(iter_rows)


def interpolate_branch(branch: pd.DataFrame, anchors: list[float]) -> pd.DataFrame:
    rows = []
    b = branch.sort_values("W_a0_m_s").drop_duplicates("W_a0_m_s")
    for anchor in anchors:
        if anchor < b.W_a0_m_s.min() - 1e-9 or anchor > b.W_a0_m_s.max() + 1e-9:
            rows.append({"W_a0": anchor, "reachable": False})
            continue
        rec: dict[str, Any] = {"W_a0": anchor, "reachable": True}
        for col in ["z_m", "u_m_s", "w_m_s", "m_kg", "physical_residual_norm", "scaled_residual_norm", "critical_real_s_inv", "critical_imag_s_inv", "branch_jacobian_condition"]:
            rec[f"full_{col}"] = float(np.interp(anchor, b.W_a0_m_s, b[col]))
        nearest = b.iloc[(b.W_a0_m_s - anchor).abs().to_numpy().argmin()]
        rec["nearest_accepted_W_a0_m_s"] = float(nearest.W_a0_m_s)
        rec["nearest_abs_delta_W_a0_m_s"] = abs(float(nearest.W_a0_m_s) - anchor)
        rows.append(rec)
    return pd.DataFrame(rows)


def compare_geometry(branch: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    interp = interpolate_branch(branch, COMPARISON_ANCHORS)
    probe = pd.read_csv(TASK012_PROBE)
    probe = probe[(probe.control == "W_a0") & (probe.success)].copy()
    py_rows = []
    for row in interp.itertuples():
        rec = row._asdict()
        p = probe[np.isclose(probe.control_value, row.W_a0)]
        if row.reachable and not p.empty:
            p0 = p.iloc[0]
            rec.update({
                "task012_z_m": float(p0.z_m),
                "task012_u_m_s": float(p0.u_m_s),
                "task012_w_m_s": float(p0.w_m_s),
                "task012_m_kg": float(p0.m_kg),
                "task012_rhs_norm": float(p0.rhs_norm),
                "z_abs_error_vs_task012_m": abs(rec["full_z_m"] - float(p0.z_m)),
                "u_abs_error_vs_task012_m_s": abs(rec["full_u_m_s"] - float(p0.u_m_s)),
                "w_abs_error_vs_task012_m_s": abs(rec["full_w_m_s"] - float(p0.w_m_s)),
                "relative_m_error_vs_task012": abs(rec["full_m_kg"] - float(p0.m_kg)) / float(p0.m_kg),
            })
        py_rows.append(rec)
    py_compare = pd.DataFrame(py_rows)

    restricted = pd.read_csv(TASK019_OUT / "python_probe_comparison.csv")
    restricted_rows = []
    for row in py_compare.itertuples():
        rec = row._asdict()
        r = restricted[np.isclose(restricted.W_a0, row.W_a0)]
        if bool(row.reachable) and not r.empty:
            r0 = r.iloc[0]
            rec.update({
                "task019_restricted_z_m": float(r0.auto_z_m),
                "task019_restricted_u_m_s": float(r0.auto_u_m_s),
                "task019_restricted_m_kg": float(r0.auto_m_kg),
                "z_abs_error_vs_task019_restricted_m": abs(row.full_z_m - float(r0.auto_z_m)),
                "u_abs_error_vs_task019_restricted_m_s": abs(row.full_u_m_s - float(r0.auto_u_m_s)),
                "relative_m_error_vs_task019_restricted": abs(row.full_m_kg - float(r0.auto_m_kg)) / float(r0.auto_m_kg),
            })
        restricted_rows.append(rec)
    restricted_compare = pd.DataFrame(restricted_rows)
    return interp, py_compare, restricted_compare


def run_gate(config: GateConfig | None = None) -> dict[str, Any]:
    config = config or GateConfig()
    y_seed, par, scaling = seed_state_and_parameters()
    q_seed = np.r_[scaling.state_to_scaled(y_seed), scaling.control_to_scaled(par[1])]
    J0 = finite_difference_branch_jacobian(q_seed, par, scaling)
    tangent0, _sv0, _cond0 = tangent_from_jacobian(J0)
    up = continue_direction("upward", q_seed, tangent0, par, scaling, config.upward_target_W_a0_m_s, config)
    down = continue_direction("downward", q_seed, -tangent0, par, scaling, config.downward_target_W_a0_m_s, config)
    directional_branch = pd.concat([pd.DataFrame(down[0]), pd.DataFrame(up[0])], ignore_index=True)
    anchors_df, anchor_eigs, anchor_iters = anchor_points(directional_branch, ANCHORS, par, scaling)
    branch = pd.concat([directional_branch, anchors_df], ignore_index=True)
    # Keep duplicate seed/directional rows explicit in per-direction output, but prefer exact anchor rows for comparisons.
    comparison_branch = branch.sort_values(["W_a0_m_s", "run"]).drop_duplicates("W_a0_m_s", keep="first")
    anchor = interpolate_branch(comparison_branch, ANCHORS)
    _comparison_anchor, py_compare, restricted_compare = compare_geometry(comparison_branch)
    failures = pd.concat([pd.DataFrame(down[3]), pd.DataFrame(up[3])], ignore_index=True) if (down[3] or up[3]) else pd.DataFrame(columns=["run", "attempted_step_index", "start_W_a0_m_s", "trial_ds_scaled", "accepted", "reason", "final_scaled_residual_norm", "augmented_jacobian_condition"])
    iterations = pd.concat([pd.DataFrame(down[2]), pd.DataFrame(up[2]), anchor_iters], ignore_index=True) if (down[2] or up[2] or not anchor_iters.empty) else pd.DataFrame()
    eigen = pd.concat([pd.DataFrame(down[1]), pd.DataFrame(up[1]), anchor_eigs], ignore_index=True)
    return {
        "config": config,
        "scaling": scaling,
        "branch": branch,
        "comparison_branch": comparison_branch,
        "anchor_reachability": anchor,
        "python_probe_comparison": py_compare,
        "restricted_task019_comparison": restricted_compare,
        "failures": failures,
        "iterations": iterations,
        "eigenvalues": eigen,
    }


def write_doc(summary: dict[str, Any], py_compare: pd.DataFrame, restricted_compare: pd.DataFrame) -> None:
    verdict_word = "passes" if summary["verdict"] == "pass" else "fails"
    DOC.write_text(
        "# TASK-027 — full-model Python W_a0 continuation gate\n\n"
        "TASK-027 applies the TASK-026 scaled Python pseudo-arclength continuation core to the full four-dimensional Berton equilibrium branch in `W_a0`. "
        "This is the conditioning/control sanity gate before attempting `H_a3` or `z_W0` Hopf-focused studies.\n\n"
        "## Reproducibility command\n\n"
        "```bash\n"
        "uv run python episodes/10-full-model-python-continuation/scripts/berton_full_task027_wa0_gate.py\n"
        "```\n\n"
        "Curated outputs are written to `episodes/10-full-model-python-continuation/outputs/task027/`.\n\n"
        "## Gate result\n\n"
        f"The full-model continuation reached `W_a0=[{summary['control_min_W_a0_m_s']:.3f}, {summary['control_max_W_a0_m_s']:.3f}]` m/s with "
        f"`{summary['accepted_unique_points']}` unique accepted control points. The maximum scaled residual norm is "
        f"`{summary['max_scaled_residual_norm']:.3e}` and the maximum physical RHS residual norm is `{summary['max_physical_residual_norm']:.3e}`. "
        f"The largest branch Jacobian condition estimate is `{summary['max_branch_jacobian_condition']:.3e}`.\n\n"
        "Accepted branch diagnostics include full-RHS residual norms, transformed/scaled residual norms, eigenvalues, tangent components, branch singular values, and Newton corrector histories.\n\n"
        "## Comparison to previous probes\n\n"
        f"Against the previous TASK-012 Python `W_a0` probe, the maximum matched-anchor altitude discrepancy is `{summary['max_z_error_vs_task012_m']:.3e}` m and "
        f"the maximum relative mass discrepancy is `{summary['max_relative_m_error_vs_task012']:.3e}` over reachable comparison anchors.\n\n"
        f"Against the restricted TASK-019 behavior, the full-model branch agrees at the same anchors to maximum altitude discrepancy `{summary['max_z_error_vs_task019_m']:.3e}` m and "
        f"maximum relative mass discrepancy `{summary['max_relative_m_error_vs_task019']:.3e}`. The full model retains the explicit vertical-velocity coordinate, but the accepted gate stays on the same `w≈0` equilibrium geometry.\n\n"
        "## Verdict\n\n"
        f"The W_a0 gate **{verdict_word}**: {summary['verdict_reason']}\n"
    )


def write_outputs(run: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    branch = run["branch"]
    unique = run["comparison_branch"]
    branch.to_csv(OUT_DIR / "full_wa0_branch_points.csv", index=False)
    run["eigenvalues"].to_csv(OUT_DIR / "full_wa0_eigenvalues.csv", index=False)
    run["iterations"].to_csv(OUT_DIR / "full_wa0_corrector_iterations.csv", index=False)
    run["failures"].to_csv(OUT_DIR / "full_wa0_rejected_steps.csv", index=False)
    run["anchor_reachability"].to_csv(OUT_DIR / "anchor_reachability.csv", index=False)
    run["python_probe_comparison"].to_csv(OUT_DIR / "python_probe_comparison.csv", index=False)
    run["restricted_task019_comparison"].to_csv(OUT_DIR / "restricted_task019_comparison.csv", index=False)

    py = run["python_probe_comparison"]
    restricted = run["restricted_task019_comparison"]
    reachable_anchors = run["anchor_reachability"][run["anchor_reachability"].reachable == True]  # noqa: E712
    reaches_12 = bool((unique.W_a0_m_s.max() >= 1.2 - 1e-6) and (run["anchor_reachability"].query("W_a0 == 1.2 and reachable").shape[0] == 1))
    residuals_ok = bool(unique.scaled_residual_norm.max() < run["config"].residual_acceptance_tolerance)
    comparison_ok = bool(py["z_abs_error_vs_task012_m"].dropna().max() < 5e-4 and py["relative_m_error_vs_task012"].dropna().max() < 5e-4)
    verdict = "pass" if reaches_12 and residuals_ok and comparison_ok else "fail"
    reason = (
        "full-model pseudo-arclength continuation reaches the required W_a0 anchors through 1.2 m/s with small residuals and reproduces prior W_a0 geometry"
        if verdict == "pass"
        else "one or more required gates failed: endpoint reachability, residual tolerance, or comparison to prior W_a0 geometry"
    )
    summary = {
        "task": "TASK-027",
        "coordinate_system": "TASK-026 scaled z,u,w,log(m/kg) with scaled W_a0 control",
        "config": asdict(run["config"]),
        "scaling": run["scaling"].__dict__,
        "accepted_points_including_directional_seed_duplicates": int(len(branch)),
        "accepted_unique_points": int(len(unique)),
        "control_min_W_a0_m_s": float(unique.W_a0_m_s.min()),
        "control_max_W_a0_m_s": float(unique.W_a0_m_s.max()),
        "reaches_W_a0_1_2_m_s": reaches_12,
        "reachable_anchor_count": int(len(reachable_anchors)),
        "max_scaled_residual_norm": float(unique.scaled_residual_norm.max()),
        "max_physical_residual_norm": float(unique.physical_residual_norm.max()),
        "max_transformed_residual_norm": float(unique.transformed_residual_norm.max()),
        "max_branch_jacobian_condition": float(unique.branch_jacobian_condition.max()),
        "min_branch_singular_value": float(unique.branch_min_singular_value.min()),
        "max_z_error_vs_task012_m": float(py["z_abs_error_vs_task012_m"].dropna().max()),
        "max_u_error_vs_task012_m_s": float(py["u_abs_error_vs_task012_m_s"].dropna().max()),
        "max_relative_m_error_vs_task012": float(py["relative_m_error_vs_task012"].dropna().max()),
        "max_z_error_vs_task019_m": float(restricted["z_abs_error_vs_task019_restricted_m"].dropna().max()),
        "max_u_error_vs_task019_m_s": float(restricted["u_abs_error_vs_task019_restricted_m_s"].dropna().max()),
        "max_relative_m_error_vs_task019": float(restricted["relative_m_error_vs_task019_restricted"].dropna().max()),
        "rejected_step_count": int(len(run["failures"])),
        "verdict": verdict,
        "verdict_reason": reason,
        "output_files": [
            "full_wa0_branch_points.csv",
            "full_wa0_eigenvalues.csv",
            "full_wa0_corrector_iterations.csv",
            "full_wa0_rejected_steps.csv",
            "anchor_reachability.csv",
            "python_probe_comparison.csv",
            "restricted_task019_comparison.csv",
            "task027_wa0_gate_verdict.json",
        ],
    }
    (OUT_DIR / "task027_wa0_gate_verdict.json").write_text(json.dumps(summary, indent=2, sort_keys=True))
    write_doc(summary, py, restricted)


def main() -> None:
    run = run_gate()
    write_outputs(run)
    summary = json.loads((OUT_DIR / "task027_wa0_gate_verdict.json").read_text())
    print(f"Wrote TASK-027 W_a0 gate diagnostics to {OUT_DIR}")
    print(f"Verdict={summary['verdict']}: {summary['verdict_reason']}")


if __name__ == "__main__":
    main()
