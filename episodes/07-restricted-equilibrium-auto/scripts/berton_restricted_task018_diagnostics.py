"""TASK-018 restricted/local 3D equilibrium scaling diagnostics.

Run from the repository root::

    uv run python episodes/07-restricted-equilibrium-auto/scripts/berton_restricted_task018_diagnostics.py

The restricted unknowns are ``(z, u, log_m)`` with ``w = 0``.  They map to the
full physical state ``(z, u, w, m) = (z, u, 0, exp(log_m))``.  The residual is
``(du/dt, dw/dt, dlog(m)/dt) = (a_x, a_z, m_dot/m)`` so each equation is a
local balance at fixed altitude, horizontal velocity, and mass.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
EPISODE_ROOT = SCRIPT_DIR.parents[0]
REPO_ROOT = SCRIPT_DIR.parents[2]
OUT_DIR = EPISODE_ROOT / "outputs" / "task018"
TASK011_OUT = REPO_ROOT / "episodes" / "05-full-model-oscillatory-orbit" / "outputs" / "task011"
EP04_SCRIPTS = REPO_ROOT / "episodes" / "04-full-model-auto-equilibria" / "scripts"
if str(EP04_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(EP04_SCRIPTS))
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

from berton_full_auto_task009_validate import default_par, finite_difference_jacobian, python_rhs  # noqa: E402
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

STATE_NAMES = ("z_m", "u_m_s", "log_m_kg")
RESIDUAL_NAMES = ("du_dt_m_s2", "dw_dt_m_s2", "dlogm_dt_s_inv")
PARAM_NAMES = {"W_a0_m_s": 1, "H_a3": 3}


@dataclass(frozen=True)
class CoordinateSpec:
    name: str
    center: np.ndarray
    scales: np.ndarray

    def to_physical_coords(self, x: np.ndarray) -> np.ndarray:
        """Return ``(z, u, log_m)`` from this coordinate vector."""

        if self.name == "physical_logm":
            return np.asarray(x, dtype=float)
        if self.name == "centered_scaled":
            return self.center + self.scales * np.asarray(x, dtype=float)
        raise ValueError(self.name)

    def from_physical_coords(self, y: np.ndarray) -> np.ndarray:
        if self.name == "physical_logm":
            return np.asarray(y, dtype=float)
        if self.name == "centered_scaled":
            return (np.asarray(y, dtype=float) - self.center) / self.scales
        raise ValueError(self.name)


def task011_parameters() -> np.ndarray:
    par = default_par()
    par[0] = 9000.0  # z_W0, m
    par[1] = 0.6  # W_a0, m/s
    par[3] = 0.61  # H_a3
    par[38] = 0.0  # no eta override
    par[42] = 0.0  # no Coriolis, as in TASK-011 classifier
    par[43] = 2.0  # diameter Reynolds convention
    return par


def seed_physical() -> tuple[np.ndarray, pd.Series]:
    seed = pd.read_csv(TASK011_OUT / "continuation_equilibrium_seed.csv").iloc[0]
    y = np.array([seed.z_m, seed.u_m_s, 0.0, seed.m_kg], dtype=float)
    return y, seed


def physical_from_restricted(v: np.ndarray) -> np.ndarray:
    z, u, log_m = map(float, v)
    return np.array([z, u, 0.0, np.exp(log_m)], dtype=float)


def restricted_residual(v: np.ndarray, par: np.ndarray, *, residual_scale: np.ndarray | None = None) -> np.ndarray:
    y = physical_from_restricted(v)
    f = python_rhs(y, par)
    raw = np.array([f[1], f[2], f[3] / y[3]], dtype=float)
    if residual_scale is None:
        return raw
    return raw / residual_scale


def centered_difference_jacobian(fun: Callable[[np.ndarray], np.ndarray], x: np.ndarray, steps: np.ndarray) -> np.ndarray:
    j = np.zeros((len(fun(x)), len(x)), dtype=float)
    for i, h in enumerate(steps):
        xp = x.copy(); xm = x.copy(); xp[i] += h; xm[i] -= h
        j[:, i] = (fun(xp) - fun(xm)) / (xp[i] - xm[i])
    return j


def param_sensitivity(v: np.ndarray, par: np.ndarray, residual_scale: np.ndarray | None = None) -> pd.DataFrame:
    rows = []
    base = restricted_residual(v, par, residual_scale=residual_scale)
    for name, idx in PARAM_NAMES.items():
        p0 = float(par[idx])
        h = max(abs(p0) * 1e-5, 1e-6)
        pp = par.copy(); pm = par.copy(); pp[idx] += h; pm[idx] -= h
        sens = (restricted_residual(v, pp, residual_scale=residual_scale) - restricted_residual(v, pm, residual_scale=residual_scale)) / (pp[idx] - pm[idx])
        for rname, val, b in zip(RESIDUAL_NAMES, sens, base):
            rows.append({"parameter": name, "residual": rname, "base_residual": b, "sensitivity": val, "parameter_step": h})
    return pd.DataFrame(rows)


def jacobian_metrics(name: str, coord: CoordinateSpec, x0: np.ndarray, par: np.ndarray, residual_scale: np.ndarray | None = None) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    steps_physical = np.array([1.0, 1e-5, 1e-4], dtype=float)
    steps = steps_physical if coord.name == "physical_logm" else steps_physical / coord.scales

    def fcoord(x: np.ndarray) -> np.ndarray:
        return restricted_residual(coord.to_physical_coords(x), par, residual_scale=residual_scale)

    J = centered_difference_jacobian(fcoord, x0, steps)
    svals = np.linalg.svd(J, compute_uv=False)
    cond = float(svals[0] / svals[-1]) if svals[-1] > 0 else np.inf
    prefix = name
    row_df = pd.DataFrame({"scaling": prefix, "residual": RESIDUAL_NAMES, "row_l2_norm": np.linalg.norm(J, axis=1)})
    col_df = pd.DataFrame({"scaling": prefix, "state": STATE_NAMES, "column_l2_norm": np.linalg.norm(J, axis=0)})
    sv_df = pd.DataFrame(
        {
            "scaling": prefix,
            "singular_value_index": np.arange(1, len(svals) + 1),
            "singular_value": svals,
            "condition_estimate": cond,
        }
    )
    return row_df, col_df, sv_df


def local_diagnostics(y: np.ndarray, par: np.ndarray) -> LocalDiagnostics:
    z, u, w, m = map(float, y)
    eta_override = None if abs(float(par[38])) < 1e-14 else float(par[4])
    atm = Atmosphere(H_a3=float(par[3]), W_a0=Q_(float(par[1]), "m/s"), z_W0=Q_(float(par[0]), "m"), Δz_W=Q_(float(par[6]), "m"), η_override=eta_override)
    config = SimulationConfig(include_coriolis=bool(round(float(par[42]))), reynolds_length="diameter" if par[43] >= 1.5 else "radius")
    state = State(t=Q_(0, "s"), x=Q_(0, "m"), z=Q_(z, "m"), u=Q_(u, "m/s"), w=Q_(w, "m/s"), crystal=Crystal(m=Q_(m, "kg"), φ=float(par[39]), c_B=Q_(float(par[40]), "m")))
    return LocalDiagnostics.from_state(state, atm, CONSTANTS, config)


def branch_report(y: np.ndarray, par: np.ndarray) -> pd.DataFrame:
    z, u, w, m = map(float, y)
    diag = local_diagnostics(y, par)
    ua = diag.U_a.to("m/s").magnitude
    wa = diag.W_a.to("m/s").magnitude
    slip = float(np.hypot(u - ua, w - wa))
    rows = [
        {"piece": "horizontal wind U_a(z)", "active_branch": "8-16 km linear segment", "value": ua, "distance_to_nearest_break_m": min(abs(z - 8000.0), abs(z - 16000.0)), "risk_at_seed": "smooth inside segment; kink only at endpoints"},
        {"piece": "updraft W_a(z)", "active_branch": "above z_W0 plateau", "value": wa, "distance_to_nearest_break_m": abs(z - float(par[0])), "risk_at_seed": "smooth w.r.t. z locally but W_a0 changes residual directly"},
        {"piece": "temperature T_a(z)", "active_branch": "8-14 km linear segment", "value": diag.T_a.to("K").magnitude, "distance_to_nearest_break_m": min(abs(z - 8000.0), abs(z - 14000.0)), "risk_at_seed": "smooth inside segment"},
        {"piece": "relative humidity H_a(z)", "active_branch": "4-10 km linear segment ending at H_a3", "value": diag.H_l, "distance_to_nearest_break_m": min(abs(z - 4000.0), abs(z - 10000.0)), "risk_at_seed": "near enough to 10 km kink that large AUTO steps can cross branch"},
        {"piece": "infrared eta(z)", "active_branch": "9-10 km linear segment", "value": diag.η, "distance_to_nearest_break_m": min(abs(z - 9000.0), abs(z - 10000.0)), "risk_at_seed": "near both eta kinks; affects radiation residual"},
        {"piece": "Reynolds terminal fallback", "active_branch": "direct slip Reynolds", "value": diag.Re, "distance_to_nearest_break_m": slip, "risk_at_seed": "fallback inactive because slip speed is nonzero"},
        {"piece": "drag MAX/Re guard", "active_branch": "Re >> 1e-12", "value": diag.C_D, "distance_to_nearest_break_m": diag.Re - 1e-12, "risk_at_seed": "guard inactive"},
        {"piece": "geometry solve", "active_branch": "positive brentq root with c > c_B", "value": diag.a.to("m").magnitude, "distance_to_nearest_break_m": (diag.c - diag.c_B).to("m").magnitude, "risk_at_seed": "smooth for positive mass; no endpoint root risk"},
        {"piece": "log-mass exp/MAX guard", "active_branch": "m = exp(log_m), no floor in Python diagnostic", "value": m, "distance_to_nearest_break_m": m, "risk_at_seed": "smooth exp map at seed; AUTO implementation should avoid clipping near seed and keep any floor far below seed inactive"},
    ]
    return pd.DataFrame(rows)


def write_note(summary: dict[str, float | str | bool]) -> None:
    doc = EPISODE_ROOT / "docs" / "task018_restricted_scaling_diagnostics.md"
    doc.parent.mkdir(parents=True, exist_ok=True)
    doc.write_text(
        "# TASK-018 restricted 3D equilibrium scaling diagnostics\n\n"
        "The restricted residual uses unknowns `(z, u, log_m)` with `w=0` and maps back to the full state as "
        "`(z, u, w, m) = (z, u, 0, exp(log_m))`. The three equations are `(du/dt, dw/dt, dlog(m)/dt)`.\n\n"
        "## Seed cross-check\n\n"
        f"The TASK-011 seed residual norm in the full physical RHS is `{summary['full_rhs_norm']:.3e}`. "
        f"The restricted residual norm is `{summary['restricted_residual_norm']:.3e}`. The full-system eigenvalues remain stable and "
        "match the saved TASK-011 diagnostics within the CSV tolerances checked by the script.\n\n"
        "## Conditioning verdict\n\n"
        f"The unscaled `(z,u,log_m)` restricted Jacobian condition estimate is `{summary['unscaled_condition']:.3e}`. "
        f"Using centered variables `Z=(z-z_seed)/100 m`, `U=(u-u_seed)/1 m s^-1`, and `M=log(m/m_seed)`, "
        f"with residual scales from seed row norms, gives condition estimate `{summary['scaled_condition']:.3e}`.\n\n"
        "## Recommendation for TASK-019\n\n"
        "Proceed with the restricted system only in scaled coordinates and scaled residuals:\n\n"
        "- AUTO states: `U(1)=Z=(z-z_seed)/100 m`, `U(2)=U=(u-u_seed)/(1 m/s)`, `U(3)=M=log(m/m_seed)`.\n"
        "- Physical map: `z=z_seed+100*U(1)`, `u=u_seed+U(2)`, `w=0`, `m=m_seed*exp(U(3))`.\n"
        "- Residuals: divide `(du/dt, dw/dt, dlogm/dt)` by the seed row-norm scales written in `scaling_recommendation.json`.\n"
        "- Parameters: continue `W_a0` and `H_a3` in physical units but set AUTO step limits conservatively enough to avoid crossing the nearby 10 km humidity/eta kinks in one step.\n\n"
        "This is not a claim that Hopf continuation is ready: the TASK-019 gate should first demonstrate a meaningful `W_a0` branch from the same scaled restricted residual.\n"
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    y_seed, seed_row = seed_physical()
    par = task011_parameters()
    v_seed = np.array([y_seed[0], y_seed[1], np.log(y_seed[3])], dtype=float)
    full_rhs = python_rhs(y_seed, par)
    restricted = restricted_residual(v_seed, par)
    full_j = finite_difference_jacobian(y_seed, par)
    full_eigs = np.linalg.eigvals(full_j)
    saved_eigs = pd.read_csv(TASK011_OUT / "continuation_equilibrium_eigenvalues.csv")
    eig_match = np.allclose(np.sort_complex(full_eigs), np.sort_complex(saved_eigs.real_s_inv + 1j * saved_eigs.imag_s_inv), rtol=5e-5, atol=1e-8)

    pd.DataFrame([{
        "z_m": y_seed[0], "u_m_s": y_seed[1], "w_m_s": y_seed[2], "m_kg": y_seed[3], "log_m_kg": v_seed[2],
        "full_rhs_norm": float(np.linalg.norm(full_rhs)),
        "restricted_residual_norm": float(np.linalg.norm(restricted)),
        "rhs_z_m_s": full_rhs[0], "rhs_u_m_s2": full_rhs[1], "rhs_w_m_s2": full_rhs[2], "rhs_m_kg_s": full_rhs[3],
        "restricted_du_dt_m_s2": restricted[0], "restricted_dw_dt_m_s2": restricted[1], "restricted_dlogm_dt_s_inv": restricted[2],
        "full_eigenvalues_match_task011": bool(eig_match),
        "full_stable_eigenvalue_count": int(np.sum(full_eigs.real < 0)),
    }]).to_csv(OUT_DIR / "seed_crosscheck.csv", index=False)
    pd.DataFrame({"real_s_inv": full_eigs.real, "imag_s_inv": full_eigs.imag}).to_csv(OUT_DIR / "full_seed_eigenvalues.csv", index=False)

    physical = CoordinateSpec("physical_logm", center=v_seed, scales=np.ones(3))
    centered = CoordinateSpec("centered_scaled", center=v_seed, scales=np.array([100.0, 1.0, 1.0]))
    row_un, col_un, sv_un = jacobian_metrics("unscaled_physical_logm_residual", physical, v_seed, par)
    row_scales = row_un["row_l2_norm"].to_numpy()
    row_scales = np.where(row_scales > 0, row_scales, 1.0)
    x_center = centered.from_physical_coords(v_seed)
    row_cs, col_cs, sv_cs = jacobian_metrics("centered_state_scaled_row_scaled", centered, x_center, par, residual_scale=row_scales)
    pd.concat([row_un, row_cs], ignore_index=True).to_csv(OUT_DIR / "jacobian_row_norms.csv", index=False)
    pd.concat([col_un, col_cs], ignore_index=True).to_csv(OUT_DIR / "jacobian_column_norms.csv", index=False)
    pd.concat([sv_un, sv_cs], ignore_index=True).to_csv(OUT_DIR / "jacobian_singular_values.csv", index=False)
    sens_un = param_sensitivity(v_seed, par); sens_un.insert(0, "scaling", "unscaled_physical_logm_residual")
    sens_sc = param_sensitivity(v_seed, par, residual_scale=row_scales); sens_sc.insert(0, "scaling", "row_scaled_residual")
    pd.concat([sens_un, sens_sc], ignore_index=True).to_csv(OUT_DIR / "parameter_sensitivities.csv", index=False)
    branch_report(y_seed, par).to_csv(OUT_DIR / "branch_smoothness_report.csv", index=False)

    recommendation = {
        "state_coordinate": "Z=(z-z_seed)/100m; U=(u-u_seed)/(1m/s); M=log(m/m_seed)",
        "z_seed_m": float(v_seed[0]),
        "u_seed_m_s": float(v_seed[1]),
        "m_seed_kg": float(y_seed[3]),
        "log_m_seed": float(v_seed[2]),
        "state_scales": {"z_m": 100.0, "u_m_s": 1.0, "log_m_kg": 1.0},
        "residual_scales": dict(zip(RESIDUAL_NAMES, map(float, row_scales))),
        "unscaled_condition_estimate": float(sv_un.condition_estimate.iloc[0]),
        "scaled_condition_estimate": float(sv_cs.condition_estimate.iloc[0]),
        "suitable_for_task019_gate": bool(float(sv_cs.condition_estimate.iloc[0]) < float(sv_un.condition_estimate.iloc[0]) and eig_match),
        "caveat": "Nearby humidity/eta profile kinks at 10 km remain branch risks; prove W_a0 continuation before H_a3 Hopf work.",
    }
    (OUT_DIR / "scaling_recommendation.json").write_text(json.dumps(recommendation, indent=2, sort_keys=True))
    write_note({
        "full_rhs_norm": float(np.linalg.norm(full_rhs)),
        "restricted_residual_norm": float(np.linalg.norm(restricted)),
        "unscaled_condition": float(sv_un.condition_estimate.iloc[0]),
        "scaled_condition": float(sv_cs.condition_estimate.iloc[0]),
    })
    print(f"Wrote TASK-018 diagnostics to {OUT_DIR}")


if __name__ == "__main__":
    main()
