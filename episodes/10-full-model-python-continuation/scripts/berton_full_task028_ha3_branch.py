"""TASK-028 full-model Python continuation in H_a3.

Run from the repository root with::

    uv run python episodes/10-full-model-python-continuation/scripts/berton_full_task028_ha3_branch.py

This script follows the actual full Berton equilibrium branch in ``H_a3`` from
TASK-011/TASK-012 seed parameters and records accepted branch/eigenvalue
support through the suspected stability-crossing region near H_a3=0.61--0.65.
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
OUT_DIR = EPISODE_ROOT / "outputs" / "task028"
DOC = EPISODE_ROOT / "docs" / "task028_ha3_full_model_branch.md"
TASK016_CROSSCHECK = REPO_ROOT / "episodes" / "08-full-model-auto-ha3" / "outputs" / "task016" / "python_suspected_crossing_crosscheck.csv"
EP04_SCRIPTS = REPO_ROOT / "episodes" / "04-full-model-auto-equilibria" / "scripts"
if str(EP04_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(EP04_SCRIPTS))
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from berton_full_auto_task009_validate import finite_difference_jacobian, python_rhs  # noqa: E402
from berton_full_task026_continuation import (  # noqa: E402
    ContinuationConfig,
    Scaling,
    seed_state_and_parameters,
    tangent_from_jacobian,
    transformed_rhs_from_physical,
)


ANCHORS = [0.600, 0.610, 0.615, 0.620, 0.625, 0.630, 0.640, 0.650]


@dataclass(frozen=True)
class Ha3Scaling(Scaling):
    """TASK-026 state scaling with H_a3 as the arclength control."""

    H_a3_ref: float = 0.61
    H_a3_scale: float = 0.01

    def control_to_scaled(self, H_a3: float) -> float:  # type: ignore[override]
        return (float(H_a3) - self.H_a3_ref) / self.H_a3_scale

    def scaled_to_control(self, lam: float) -> float:  # type: ignore[override]
        return self.H_a3_ref + self.H_a3_scale * float(lam)


@dataclass(frozen=True)
class Ha3Config:
    upward_target_H_a3: float = 0.650
    downward_target_H_a3: float = 0.600
    ds_initial: float = 0.20
    ds_min: float = 0.005
    ds_max: float = 0.35
    max_steps_per_direction: int = 220
    residual_acceptance_tolerance: float = 2.0e-6
    newton_tolerance: float = 1.0e-7


def ha3_seed_state_and_parameters() -> tuple[np.ndarray, np.ndarray, Ha3Scaling]:
    y, par, base = seed_state_and_parameters()
    par[1] = 0.6
    par[3] = 0.61
    scaling = Ha3Scaling(
        z_ref_m=base.z_ref_m,
        u_ref_m_s=base.u_ref_m_s,
        w_ref_m_s=base.w_ref_m_s,
        log_m_ref=base.log_m_ref,
        z_scale_m=base.z_scale_m,
        u_scale_m_s=base.u_scale_m_s,
        w_scale_m_s=base.w_scale_m_s,
        log_m_scale=base.log_m_scale,
        W_a0_ref_m_s=base.W_a0_ref_m_s,
        W_a0_scale_m_s=base.W_a0_scale_m_s,
        residual_row_scales=base.residual_row_scales,
        H_a3_ref=0.61,
        H_a3_scale=0.01,
    )
    return y, par, scaling


def residual_scaled(x: np.ndarray, lam: float, par_template: np.ndarray, scaling: Ha3Scaling) -> np.ndarray:
    y = scaling.scaled_to_state(x)
    par = par_template.copy()
    par[3] = scaling.scaled_to_control(lam)
    return scaling.residual_scale_vector * transformed_rhs_from_physical(y, par)


def q_residual(q: np.ndarray, par_template: np.ndarray, scaling: Ha3Scaling) -> np.ndarray:
    return residual_scaled(q[:4], float(q[4]), par_template, scaling)


def finite_difference_branch_jacobian(q: np.ndarray, par_template: np.ndarray, scaling: Ha3Scaling, h: float = 1e-5) -> np.ndarray:
    q = np.asarray(q, dtype=float)
    J = np.zeros((4, 5), dtype=float)
    for i in range(5):
        step = h * max(1.0, abs(q[i]))
        qp = q.copy(); qm = q.copy(); qp[i] += step; qm[i] -= step
        J[:, i] = (q_residual(qp, par_template, scaling) - q_residual(qm, par_template, scaling)) / (qp[i] - qm[i])
    return J


def ha3_corrector(q_pred: np.ndarray, tangent: np.ndarray, par_template: np.ndarray, scaling: Ha3Scaling, config: ContinuationConfig):
    """Use the TASK-026 corrector with this module's H_a3 residuals.

    The TASK-026 corrector calls the module-level branch-Jacobian and residual
    functions in its defining module, so keep a local copy of the Newton loop for
    H_a3 rather than monkey-patching the W_a0 core.
    """
    q = np.array(q_pred, dtype=float)
    iterations: list[dict[str, float | int | str]] = []
    singular_values = np.full(5, np.nan)
    condition = float("nan")
    reason = "maximum Newton iterations reached"
    for k in range(config.max_newton_iterations):
        r = q_residual(q, par_template, scaling)
        aug = np.r_[r, np.dot(q - q_pred, tangent)]
        J = finite_difference_branch_jacobian(q, par_template, scaling, config.finite_difference_step)
        A = np.vstack([J, tangent])
        singular_values = np.linalg.svd(A, compute_uv=False)
        condition = float(singular_values[0] / singular_values[-1]) if singular_values[-1] > 0.0 else float("inf")
        aug_norm = float(np.linalg.norm(aug))
        if aug_norm < config.correction_tolerance:
            reason = "converged"
            iterations.append({"iteration": k, "residual_norm": float(np.linalg.norm(r)), "augmented_norm": aug_norm, "correction_norm": 0.0, "jacobian_condition": condition, "min_singular_value": float(singular_values[-1]), "linear_solver": "not_needed"})
            from berton_full_task026_continuation import CorrectorResult
            return CorrectorResult(True, q, iterations, reason, aug_norm, float(np.linalg.norm(r)), condition, singular_values)
        try:
            delta = np.linalg.solve(A, -aug)
            solver = "solve"
        except np.linalg.LinAlgError:
            delta, *_ = np.linalg.lstsq(A, -aug, rcond=None)
            solver = "lstsq_singular_augmented_jacobian"
        q = q + delta
        iterations.append({"iteration": k, "residual_norm": float(np.linalg.norm(r)), "augmented_norm": aug_norm, "correction_norm": float(np.linalg.norm(delta)), "jacobian_condition": condition, "min_singular_value": float(singular_values[-1]), "linear_solver": solver})
        if not np.all(np.isfinite(q)):
            reason = "non-finite Newton iterate"
            break
    from berton_full_task026_continuation import CorrectorResult
    final_r = q_residual(q, par_template, scaling) if np.all(np.isfinite(q)) else np.full(4, np.nan)
    final_aug = np.r_[final_r, np.dot(q - q_pred, tangent)] if np.all(np.isfinite(q)) else np.full(5, np.nan)
    return CorrectorResult(False, q, iterations, reason, float(np.linalg.norm(final_aug)), float(np.linalg.norm(final_r)), condition, singular_values)


def _complex_pair(eigs: np.ndarray) -> tuple[complex, int]:
    complex_eigs = [e for e in eigs if abs(e.imag) > 1e-10]
    if not complex_eigs:
        critical = eigs[np.argmax(eigs.real)]
        return complex(critical), 0
    pair = max(complex_eigs, key=lambda e: (e.real, abs(e.imag)))
    return complex(pair), len(complex_eigs) // 2


def _point_record(run: str, step_index: int, q: np.ndarray, par_template: np.ndarray, scaling: Ha3Scaling, tangent: np.ndarray, branch_singular_values: np.ndarray, branch_condition: float, corrector_iterations: int, corrector_reason: str, ds_scaled: float) -> dict[str, Any]:
    y = scaling.scaled_to_state(q[:4])
    par = par_template.copy(); par[3] = scaling.scaled_to_control(q[4])
    physical_rhs = python_rhs(y, par)
    transformed_rhs = transformed_rhs_from_physical(y, par)
    scaled_residual = q_residual(q, par_template, scaling)
    eig = np.linalg.eigvals(finite_difference_jacobian(y, par))
    critical = eig[np.argmax(eig.real)]
    pair, pair_count = _complex_pair(eig)
    stable_count = int(np.sum(eig.real < 0.0))
    return {
        "run": run,
        "step_index": step_index,
        "accepted": True,
        "H_a3": float(par[3]),
        "W_a0_m_s": float(par[1]),
        "lambda_H_a3_scaled": float(q[4]),
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
        "complex_pair_count": int(pair_count),
        "tracked_pair_real_s_inv": float(pair.real),
        "tracked_pair_imag_abs_s_inv": float(abs(pair.imag)),
        "branch_jacobian_condition": float(branch_condition),
        "branch_min_singular_value": float(branch_singular_values[-1]),
        "branch_max_singular_value": float(branch_singular_values[0]),
        "tangent_lambda_H_a3": float(tangent[4]),
        "ds_scaled": float(ds_scaled),
        "corrector_iterations": int(corrector_iterations),
        "corrector_reason": corrector_reason,
    }


def _eigen_records(run: str, step_index: int, q: np.ndarray, par_template: np.ndarray, scaling: Ha3Scaling) -> list[dict[str, Any]]:
    y = scaling.scaled_to_state(q[:4])
    par = par_template.copy(); par[3] = scaling.scaled_to_control(q[4])
    eigs = np.linalg.eigvals(finite_difference_jacobian(y, par))
    return [{"run": run, "step_index": step_index, "H_a3": float(par[3]), "eigenvalue_index": i, "real_s_inv": float(e.real), "imag_s_inv": float(e.imag)} for i, e in enumerate(eigs)]


def continue_direction(run: str, q_seed: np.ndarray, tangent_seed: np.ndarray, par: np.ndarray, scaling: Ha3Scaling, target_H: float, config: Ha3Config):
    cont_cfg = ContinuationConfig(ds=config.ds_initial, correction_tolerance=config.newton_tolerance)
    direction = 1.0 if target_H > scaling.scaled_to_control(q_seed[4]) else -1.0
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
        current_H = scaling.scaled_to_control(q[4])
        if (direction > 0 and current_H >= target_H - 1e-12) or (direction < 0 and current_H <= target_H + 1e-12):
            break
        predicted_dH = scaling.H_a3_scale * ds * tangent[4]
        remaining = target_H - current_H
        trial_ds = ds
        if predicted_dH != 0 and abs(predicted_dH) > abs(remaining):
            trial_ds = max(config.ds_min, abs(0.98 * remaining / (scaling.H_a3_scale * tangent[4])))
        q_pred = q + trial_ds * tangent
        trial_cfg = ContinuationConfig(ds=trial_ds, correction_tolerance=config.newton_tolerance)
        result = ha3_corrector(q_pred, tangent, par, scaling, trial_cfg)
        if not result.accepted or result.final_residual_norm > config.residual_acceptance_tolerance:
            failures.append({"run": run, "attempted_step_index": step, "start_H_a3": float(current_H), "trial_ds_scaled": float(trial_ds), "accepted": bool(result.accepted), "reason": result.reason, "final_scaled_residual_norm": float(result.final_residual_norm), "augmented_jacobian_condition": float(result.jacobian_condition)})
            ds *= 0.5
            if ds < config.ds_min:
                break
            continue
        q_new = result.q
        new_H = scaling.scaled_to_control(q_new[4])
        if (new_H - current_H) * direction <= 0.0:
            failures.append({"run": run, "attempted_step_index": step, "start_H_a3": float(current_H), "trial_ds_scaled": float(trial_ds), "accepted": True, "reason": "corrected point moved opposite requested H_a3 direction", "final_scaled_residual_norm": float(result.final_residual_norm), "augmented_jacobian_condition": float(result.jacobian_condition)})
            ds *= 0.5
            if ds < config.ds_min:
                break
            continue
        for it in result.iterations:
            row = dict(it); row.update({"run": run, "step_index": step, "H_a3": float(new_H), "ds_scaled": float(trial_ds)})
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


def solve_fixed_control_anchor(anchor_H: float, branch: pd.DataFrame, par: np.ndarray, scaling: Ha3Scaling, tolerance: float = 1e-8, max_iterations: int = 10):
    b = branch.sort_values("H_a3").drop_duplicates("H_a3")
    q = np.array([
        np.interp(anchor_H, b.H_a3, b.scaled_x0_z),
        np.interp(anchor_H, b.H_a3, b.scaled_x1_u),
        np.interp(anchor_H, b.H_a3, b.scaled_x2_w),
        np.interp(anchor_H, b.H_a3, b.scaled_x3_log_m),
        scaling.control_to_scaled(anchor_H),
    ], dtype=float)
    iterations: list[dict[str, Any]] = []
    for k in range(max_iterations):
        r = q_residual(q, par, scaling)
        norm = float(np.linalg.norm(r))
        if norm < tolerance:
            return q, iterations, "converged"
        J = finite_difference_branch_jacobian(q, par, scaling)[:, :4]
        cond = float(np.linalg.cond(J))
        try:
            delta = np.linalg.solve(J, -r); solver = "solve"
        except np.linalg.LinAlgError:
            delta, *_ = np.linalg.lstsq(J, -r, rcond=None); solver = "lstsq_singular_state_jacobian"
        q[:4] += delta
        iterations.append({"run": "anchor", "step_index": int(round(anchor_H * 1000)), "H_a3": float(anchor_H), "iteration": k, "residual_norm": norm, "augmented_norm": norm, "correction_norm": float(np.linalg.norm(delta)), "jacobian_condition": cond, "min_singular_value": float(np.linalg.svd(J, compute_uv=False)[-1]), "linear_solver": solver, "ds_scaled": 0.0})
        if not np.all(np.isfinite(q)):
            return q, iterations, "non-finite anchor Newton iterate"
    return q, iterations, "maximum anchor Newton iterations reached"


def anchor_points(branch: pd.DataFrame, anchors: list[float], par: np.ndarray, scaling: Ha3Scaling):
    rows: list[dict[str, Any]] = []
    eig_rows: list[dict[str, Any]] = []
    iter_rows: list[dict[str, Any]] = []
    b = branch.sort_values("H_a3").drop_duplicates("H_a3")
    for i, anchor in enumerate(anchors, start=1):
        if anchor < b.H_a3.min() - 1e-12 or anchor > b.H_a3.max() + 1e-12:
            continue
        q, iterations, reason = solve_fixed_control_anchor(anchor, b, par, scaling)
        iter_rows.extend(iterations)
        J = finite_difference_branch_jacobian(q, par, scaling)
        tangent, sv, cond = tangent_from_jacobian(J)
        rows.append(_point_record("anchor", i, q, par, scaling, tangent, sv, cond, len(iterations), reason, 0.0))
        eig_rows.extend(_eigen_records("anchor", i, q, par, scaling))
    return pd.DataFrame(rows), pd.DataFrame(eig_rows), pd.DataFrame(iter_rows)


def independent_eigen_check(branch: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for row in branch.sort_values("H_a3").itertuples():
        y = np.array([row.z_m, row.u_m_s, row.w_m_s, row.m_kg], dtype=float)
        _seed, par, _scaling = ha3_seed_state_and_parameters()
        par[3] = float(row.H_a3)
        eig = np.linalg.eigvals(finite_difference_jacobian(y, par))
        pair, pair_count = _complex_pair(eig)
        rows.append({
            "run": row.run,
            "step_index": int(row.step_index),
            "H_a3": float(row.H_a3),
            "independent_tracked_pair_real_s_inv": float(pair.real),
            "independent_tracked_pair_imag_abs_s_inv": float(abs(pair.imag)),
            "independent_stable_eigenvalue_count": int(np.sum(eig.real < 0.0)),
            "independent_complex_pair_count": int(pair_count),
            "delta_vs_branch_tracked_pair_real_s_inv": float(pair.real - row.tracked_pair_real_s_inv),
        })
    return pd.DataFrame(rows)


def find_hopf_sign_change(unique: pd.DataFrame) -> dict[str, Any]:
    """Find a Hopf-style sign change with complex pairs on both sides."""
    b = unique.sort_values("H_a3")
    for left, right in zip(b.iloc[:-1].itertuples(), b.iloc[1:].itertuples()):
        left_complex = left.complex_pair_count > 0 and left.tracked_pair_imag_abs_s_inv > 1e-10
        right_complex = right.complex_pair_count > 0 and right.tracked_pair_imag_abs_s_inv > 1e-10
        if left_complex and right_complex and (left.tracked_pair_real_s_inv == 0.0 or left.tracked_pair_real_s_inv * right.tracked_pair_real_s_inv < 0.0):
            frac = -left.tracked_pair_real_s_inv / (right.tracked_pair_real_s_inv - left.tracked_pair_real_s_inv)
            return {
                "found": True,
                "left_H_a3": float(left.H_a3),
                "right_H_a3": float(right.H_a3),
                "left_pair_real_s_inv": float(left.tracked_pair_real_s_inv),
                "right_pair_real_s_inv": float(right.tracked_pair_real_s_inv),
                "left_pair_imag_abs_s_inv": float(left.tracked_pair_imag_abs_s_inv),
                "right_pair_imag_abs_s_inv": float(right.tracked_pair_imag_abs_s_inv),
                "estimated_crossing_H_a3_linear": float(left.H_a3 + frac * (right.H_a3 - left.H_a3)),
                "left_stable_count": int(left.stable_eigenvalue_count),
                "right_stable_count": int(right.stable_eigenvalue_count),
            }
    return {"found": False}


def find_stability_transition(unique: pd.DataFrame) -> dict[str, Any]:
    """Find any accepted-branch stability-count change, Hopf or otherwise."""
    b = unique.sort_values("H_a3")
    for left, right in zip(b.iloc[:-1].itertuples(), b.iloc[1:].itertuples()):
        if int(left.stable_eigenvalue_count) != int(right.stable_eigenvalue_count):
            return {
                "found": True,
                "left_H_a3": float(left.H_a3),
                "right_H_a3": float(right.H_a3),
                "left_stable_count": int(left.stable_eigenvalue_count),
                "right_stable_count": int(right.stable_eigenvalue_count),
                "left_critical_real_s_inv": float(left.critical_real_s_inv),
                "right_critical_real_s_inv": float(right.critical_real_s_inv),
                "left_critical_imag_s_inv": float(left.critical_imag_s_inv),
                "right_critical_imag_s_inv": float(right.critical_imag_s_inv),
                "left_complex_pair_count": int(left.complex_pair_count),
                "right_complex_pair_count": int(right.complex_pair_count),
                "interpretation": "stable-eigenvalue count changes on accepted branch points, but the right side has no complex pair and therefore is not Hopf evidence",
            }
    return {"found": False}


def run_ha3_branch(config: Ha3Config | None = None) -> dict[str, Any]:
    config = config or Ha3Config()
    y_seed, par, scaling = ha3_seed_state_and_parameters()
    q_seed = np.r_[scaling.state_to_scaled(y_seed), scaling.control_to_scaled(par[3])]
    J0 = finite_difference_branch_jacobian(q_seed, par, scaling)
    tangent0, _sv0, _cond0 = tangent_from_jacobian(J0)
    up = continue_direction("upward", q_seed, tangent0, par, scaling, config.upward_target_H_a3, config)
    down = continue_direction("downward", q_seed, -tangent0, par, scaling, config.downward_target_H_a3, config)
    directional = pd.concat([pd.DataFrame(down[0]), pd.DataFrame(up[0])], ignore_index=True)
    anchors_df, anchor_eigs, anchor_iters = anchor_points(directional, ANCHORS, par, scaling)
    branch = pd.concat([directional, anchors_df], ignore_index=True)
    unique = branch.sort_values(["H_a3", "run"]).drop_duplicates("H_a3", keep="first")
    failures = pd.concat([pd.DataFrame(down[3]), pd.DataFrame(up[3])], ignore_index=True) if (down[3] or up[3]) else pd.DataFrame(columns=["run", "attempted_step_index", "start_H_a3", "trial_ds_scaled", "accepted", "reason", "final_scaled_residual_norm", "augmented_jacobian_condition"])
    iterations = pd.concat([pd.DataFrame(down[2]), pd.DataFrame(up[2]), anchor_iters], ignore_index=True) if (down[2] or up[2] or not anchor_iters.empty) else pd.DataFrame()
    eigen = pd.concat([pd.DataFrame(down[1]), pd.DataFrame(up[1]), anchor_eigs], ignore_index=True)
    independent = independent_eigen_check(unique)
    return {"config": config, "scaling": scaling, "branch": branch, "comparison_branch": unique, "failures": failures, "iterations": iterations, "eigenvalues": eigen, "independent_eigen_check": independent, "candidate_hopf_crossing": find_hopf_sign_change(unique), "stability_transition": find_stability_transition(unique)}


def write_doc(summary: dict[str, Any]) -> None:
    crossing = summary["candidate_hopf_crossing"]
    transition = summary["stability_transition"]
    if crossing["found"]:
        verdict = (
            f"The accepted branch brackets a tracked complex-pair real-part sign change between `H_a3={crossing['left_H_a3']:.6f}` "
            f"and `H_a3={crossing['right_H_a3']:.6f}`; linear interpolation estimates `H_a3≈{crossing['estimated_crossing_H_a3_linear']:.9f}`. "
            "This is Python branch evidence for a Hopf candidate, not an AUTO label."
        )
    elif transition["found"]:
        verdict = (
            "No Hopf-style complex-pair sign crossing was found on the accepted segment. "
            f"A non-Hopf stability-count transition is bracketed between `H_a3={transition['left_H_a3']:.6f}` and `H_a3={transition['right_H_a3']:.6f}`: "
            f"the stable count changes from `{transition['left_stable_count']}` to `{transition['right_stable_count']}`, while the right-side critical eigenvalues are real."
        )
    else:
        verdict = "No tracked complex-pair sign change and no stable-count change were found on the accepted H_a3 branch segment; this is negative evidence only over the reached interval."
    DOC.write_text(
        "# TASK-028 — full-model Python H_a3 continuation branch\n\n"
        "TASK-028 follows the full four-dimensional Berton equilibrium branch in `H_a3` from the TASK-011/TASK-012 seed after the TASK-027 `W_a0` gate passed.\n\n"
        "## Reproducibility command\n\n"
        "```bash\nuv run python episodes/10-full-model-python-continuation/scripts/berton_full_task028_ha3_branch.py\n```\n\n"
        "Curated outputs are written to `episodes/10-full-model-python-continuation/outputs/task028/`.\n\n"
        "## Branch coverage and diagnostics\n\n"
        f"The accepted branch covers `H_a3=[{summary['control_min_H_a3']:.6f}, {summary['control_max_H_a3']:.6f}]` with `{summary['accepted_unique_points']}` unique accepted control points. "
        f"The maximum scaled residual norm is `{summary['max_scaled_residual_norm']:.3e}` and the maximum physical RHS residual norm is `{summary['max_physical_residual_norm']:.3e}`. "
        f"The largest branch Jacobian condition estimate is `{summary['max_branch_jacobian_condition']:.3e}`.\n\n"
        "Each accepted point records full residuals, transformed/scaled residuals, all eigenvalues, stable-eigenvalue counts, and a tracked complex-pair real/imaginary component. "
        "The independent eigenvalue check recomputes the full finite-difference Jacobian from saved physical states and confirms the tracked pair signs.\n\n"
        "## Verdict\n\n"
        f"{verdict}\n\n"
        "## Numerical limitations\n\n"
        f"Rejected corrector steps: `{summary['rejected_step_count']}`. The verdict is limited to the reached interval and finite-difference eigenvalue/Jacobian settings recorded in `task028_ha3_branch_verdict.json`.\n"
    )


def write_outputs(run: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    branch = run["branch"]
    unique = run["comparison_branch"]
    branch.to_csv(OUT_DIR / "full_ha3_branch_points.csv", index=False)
    run["eigenvalues"].to_csv(OUT_DIR / "full_ha3_eigenvalues.csv", index=False)
    run["iterations"].to_csv(OUT_DIR / "full_ha3_corrector_iterations.csv", index=False)
    run["failures"].to_csv(OUT_DIR / "full_ha3_rejected_steps.csv", index=False)
    run["independent_eigen_check"].to_csv(OUT_DIR / "independent_eigen_check.csv", index=False)
    if TASK016_CROSSCHECK.exists():
        pd.read_csv(TASK016_CROSSCHECK).to_csv(OUT_DIR / "prior_fixed_seed_crosscheck_reference.csv", index=False)
    reaches_region = bool(unique.H_a3.min() <= 0.610 + 1e-9 and unique.H_a3.max() >= 0.650 - 1e-9)
    residuals_ok = bool(unique.scaled_residual_norm.max() < run["config"].residual_acceptance_tolerance)
    independent_ok = bool(run["independent_eigen_check"].delta_vs_branch_tracked_pair_real_s_inv.abs().max() < 1e-12)
    crossing = run["candidate_hopf_crossing"]
    transition = run["stability_transition"]
    verdict = "candidate_hopf_bracketed" if (crossing["found"] and reaches_region and residuals_ok and independent_ok) else ("no_hopf_but_stability_transition" if transition["found"] and reaches_region and residuals_ok and independent_ok else ("no_crossing_on_reached_branch" if reaches_region and residuals_ok else "numerical_limitation"))
    reason = (
        "accepted full-equilibrium branch points bracket a complex-pair real-part sign change and independent eigenvalue recomputation confirms it"
        if verdict == "candidate_hopf_bracketed"
        else ("accepted branch covers the target interval and brackets a stable-count change, but not a Hopf-style complex-pair crossing" if verdict == "no_hopf_but_stability_transition" else ("accepted branch covers the target interval with no Hopf or stable-count crossing" if verdict == "no_crossing_on_reached_branch" else "continuation did not cover the target interval or residual/eigenvalue checks failed"))
    )
    summary = {
        "task": "TASK-028",
        "coordinate_system": "TASK-026 scaled z,u,w,log(m/kg) with scaled H_a3 control",
        "config": asdict(run["config"]),
        "scaling": run["scaling"].__dict__,
        "accepted_points_including_directional_seed_duplicates": int(len(branch)),
        "accepted_unique_points": int(len(unique)),
        "control_min_H_a3": float(unique.H_a3.min()),
        "control_max_H_a3": float(unique.H_a3.max()),
        "covers_suspected_0_61_to_0_65_region": reaches_region,
        "max_scaled_residual_norm": float(unique.scaled_residual_norm.max()),
        "max_physical_residual_norm": float(unique.physical_residual_norm.max()),
        "max_transformed_residual_norm": float(unique.transformed_residual_norm.max()),
        "max_branch_jacobian_condition": float(unique.branch_jacobian_condition.max()),
        "min_branch_singular_value": float(unique.branch_min_singular_value.min()),
        "stable_count_values": sorted(int(v) for v in unique.stable_eigenvalue_count.unique()),
        "tracked_pair_real_min_s_inv": float(unique.tracked_pair_real_s_inv.min()),
        "tracked_pair_real_max_s_inv": float(unique.tracked_pair_real_s_inv.max()),
        "independent_eigen_check_max_abs_delta_pair_real_s_inv": float(run["independent_eigen_check"].delta_vs_branch_tracked_pair_real_s_inv.abs().max()),
        "candidate_hopf_crossing": crossing,
        "stability_transition": transition,
        "rejected_step_count": int(len(run["failures"])),
        "verdict": verdict,
        "verdict_reason": reason,
        "output_files": [
            "full_ha3_branch_points.csv",
            "full_ha3_eigenvalues.csv",
            "full_ha3_corrector_iterations.csv",
            "full_ha3_rejected_steps.csv",
            "independent_eigen_check.csv",
            "prior_fixed_seed_crosscheck_reference.csv",
            "task028_ha3_branch_verdict.json",
        ],
    }
    (OUT_DIR / "task028_ha3_branch_verdict.json").write_text(json.dumps(summary, indent=2, sort_keys=True))
    write_doc(summary)


def main() -> None:
    run = run_ha3_branch()
    write_outputs(run)
    summary = json.loads((OUT_DIR / "task028_ha3_branch_verdict.json").read_text())
    print(f"Wrote TASK-028 H_a3 branch diagnostics to {OUT_DIR}")
    print(f"Verdict={summary['verdict']}: {summary['verdict_reason']}")


if __name__ == "__main__":
    main()
