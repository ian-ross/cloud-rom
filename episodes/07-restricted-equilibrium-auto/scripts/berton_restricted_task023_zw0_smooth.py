"""TASK-023 restricted z_W0 continuation with a smoothed updraft profile.

Run from the repository root after AUTO::

    bash episodes/07-restricted-equilibrium-auto/auto/berton_restricted_task023_zw0_smooth/run_auto.sh
    uv run python episodes/07-restricted-equilibrium-auto/scripts/berton_restricted_task023_zw0_smooth.py

The AUTO residual reuses the validated TASK-019 restricted coordinates
``Z=(z-z_seed)/100``, ``U=(u-u_seed)/(1 m/s)``, and ``P=M/10``.  The
active control is ``q_z=(z_W0-9000 m)/1000 m``.  The Berton piecewise updraft
``W_a0*clip((z-(z_W0-Delta_z_W))/Delta_z_W, 0, 1)`` is replaced by the smooth
clip
``eps*(softplus(x/eps)-softplus((x-1)/eps))`` with ``eps=50 m/Delta_z_W``.
"""

from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
EPISODE_ROOT = SCRIPT_DIR.parents[0]
REPO_ROOT = SCRIPT_DIR.parents[2]
AUTO_DIR = EPISODE_ROOT / "auto" / "berton_restricted_task023_zw0_smooth"
OUT_DIR = EPISODE_ROOT / "outputs" / "task023"
DOC = EPISODE_ROOT / "docs" / "task023_zw0_smooth_restricted_verdict.md"
TASK019_OUT = EPISODE_ROOT / "outputs" / "task019"
TASK020_OUT = EPISODE_ROOT / "outputs" / "task020"
TASK022_OUT = EPISODE_ROOT / "outputs" / "task022"

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

from berton_restricted_task018_diagnostics import (  # noqa: E402
    RESIDUAL_NAMES,
    seed_physical,
    task011_parameters,
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

Z_SEED = 9.61802753226093591e3
U_SEED = 1.90986233869532240
M_SEED = 1.08022939205920521e-9
LOG_M_SEED = math.log(M_SEED)
Z_W0_REF = 9000.0
Z_W0_SCALE = 1000.0
SMOOTHING_WIDTH_M = 50.0
DELTA_Z_W = 300.0
TYPE_NAMES = {-9: "MX", -4: "UZ-", 0: "regular", 1: "BP", 2: "LP", 3: "HB", 4: "UZ/NPR", 9: "EP"}


class SmoothAtmosphere(Atmosphere):
    def updraft(self, z):  # type: ignore[override]
        return Q_(
            smoothed_updraft_value(
                z.to("m").magnitude,
                self.z_W0.to("m").magnitude,
                self.W_a0.to("m/s").magnitude,
                self.Δz_W.to("m").magnitude,
                SMOOTHING_WIDTH_M,
            ),
            "m/s",
        )


RUNS = {
    "z-plus": {"file": "task023-zw0-smooth-plus", "direction": "upward", "anchors": [0.25, 0.5, 0.75, 1.0]},
    "z-minus": {"file": "task023-zw0-smooth-minus", "direction": "downward", "anchors": [-0.25, -0.5, -1.0, -1.5, -2.0]},
}


def softplus(x: float | np.ndarray) -> float | np.ndarray:
    arr = np.asarray(x, dtype=float)
    out = np.empty_like(arr, dtype=float)
    hi = arr > 40.0
    lo = arr < -40.0
    mid = ~(hi | lo)
    out[hi] = arr[hi]
    out[lo] = np.exp(arr[lo])
    out[mid] = np.log1p(np.exp(arr[mid]))
    return float(out) if out.ndim == 0 else out


def smooth_clip01(x: float | np.ndarray, eps: float) -> float | np.ndarray:
    return eps * (softplus(np.asarray(x) / eps) - softplus((np.asarray(x) - 1.0) / eps))


def smoothed_updraft_value(z_m: float, z_w0_m: float, w_a0: float = 0.6, delta_z_w: float = DELTA_Z_W, width_m: float = SMOOTHING_WIDTH_M) -> float:
    eps = width_m / delta_z_w
    x = (z_m - (z_w0_m - delta_z_w)) / delta_z_w
    return float(w_a0 * smooth_clip01(x, eps))


def piecewise_updraft_value(z_m: float, z_w0_m: float, w_a0: float = 0.6, delta_z_w: float = DELTA_Z_W) -> float:
    x = (z_m - (z_w0_m - delta_z_w)) / delta_z_w
    return float(w_a0 * min(max(x, 0.0), 1.0))


def residual_scales() -> np.ndarray:
    rec = json.loads((EPISODE_ROOT / "outputs" / "task018" / "scaling_recommendation.json").read_text())
    return np.array([rec["residual_scales"][name] for name in RESIDUAL_NAMES], dtype=float)


def python_rhs_smoothed(y: np.ndarray, par: np.ndarray) -> np.ndarray:
    z, u, w, m = map(float, y)
    z_w0 = float(par[0]); w_a0 = float(par[1]); delta = float(par[6])
    eta_blend = float(par[38])
    eta_override = None if abs(eta_blend) < 1e-14 else float(par[4])
    atm = SmoothAtmosphere(H_a3=float(par[3]), W_a0=Q_(w_a0, "m/s"), z_W0=Q_(z_w0, "m"), Δz_W=Q_(delta, "m"), η_override=eta_override)
    crystal = Crystal(m=Q_(m, "kg"), φ=float(par[39]), c_B=Q_(float(par[40]), "m"))
    state = State(t=Q_(0, "s"), x=Q_(0, "m"), z=Q_(z, "m"), u=Q_(u, "m/s"), w=Q_(w, "m/s"), crystal=crystal)
    config = SimulationConfig(include_coriolis=bool(round(float(par[42]))), reynolds_length="diameter" if par[43] >= 1.5 else "radius")
    diag = LocalDiagnostics.from_state(state, atm, CONSTANTS, config)
    ax, az = accelerations(state, diag, CONSTANTS, config)
    return np.array([w, ax.to("m/s^2").magnitude, az.to("m/s^2").magnitude, diag.m_dot.to("kg/s").magnitude])


def restricted_residual_smoothed(v: np.ndarray, par: np.ndarray, *, residual_scale: np.ndarray | None = None) -> np.ndarray:
    y = np.array([float(v[0]), float(v[1]), 0.0, math.exp(float(v[2]))])
    f = python_rhs_smoothed(y, par)
    raw = np.array([f[1], f[2], f[3] / y[3]])
    return raw if residual_scale is None else raw / residual_scale


def finite_difference_jacobian_smoothed(y: np.ndarray, par: np.ndarray) -> np.ndarray:
    J = np.zeros((4, 4))
    steps = np.array([1.0, 1e-5, 1e-5, max(abs(y[3]) * 1e-4, 1e-14)])
    for i, h in enumerate(steps):
        yp = y.copy(); ym = y.copy(); yp[i] += h; ym[i] -= h
        if i == 3 and ym[i] <= 0:
            ym[i] = y[i] * (1 - 1e-4)
        J[:, i] = (python_rhs_smoothed(yp, par) - python_rhs_smoothed(ym, par)) / (yp[i] - ym[i])
    return J


def parse_b(path: Path, run: str, meta: dict) -> pd.DataFrame:
    rows = []
    if not path.exists():
        return pd.DataFrame()
    for line in path.read_text().splitlines():
        parts = line.split()
        if len(parts) < 9:
            continue
        try:
            br, pt, ty, lab = map(int, parts[:4]); vals = list(map(float, parts[4:]))
        except ValueError:
            continue
        q, norm, z_scaled, u_scaled, p_scaled = vals[:5]
        z_w0 = Z_W0_REF + Z_W0_SCALE * q
        z = Z_SEED + 100.0 * z_scaled
        u = U_SEED + u_scaled
        M = 10.0 * p_scaled
        anchors = meta["anchors"]
        is_user = any(np.isclose(q, target, atol=5e-5) for target in anchors)
        typ = "UZ" if is_user else ("NPR" if ty == 4 else TYPE_NAMES.get(ty, f"TY={ty}"))
        w_s = smoothed_updraft_value(z, z_w0)
        w_p = piecewise_updraft_value(z, z_w0)
        rows.append({
            "run": run, "direction": meta["direction"], "branch": br, "point": pt, "ty": ty, "type": typ, "label": lab,
            "is_user_point": is_user, "is_special_point": ty in {1, 2, 3}, "q_zW0_scaled": q, "z_W0_m": z_w0,
            "z_W0_km": z_w0 / 1000.0, "scaled_l2_norm": norm, "Z_scaled": z_scaled, "U_scaled": u_scaled,
            "P_log_ratio_over_10": p_scaled, "M_log_ratio": M, "z_m": z, "u_m_s": u, "m_kg": M_SEED * math.exp(M),
            "smoothed_W_a_m_s": w_s, "piecewise_W_a_m_s": w_p, "updraft_difference_m_s": w_s - w_p,
            "distance_to_z_W0_m": z - z_w0, "distance_to_ramp_base_m": z - (z_w0 - DELTA_Z_W),
            "smooth_width_m": SMOOTHING_WIDTH_M,
        })
    return pd.DataFrame(rows)


def parse_d(path: Path, run: str) -> pd.DataFrame:
    rows = []
    if not path.exists():
        return pd.DataFrame(columns=["run", "line", "message"])
    tokens = ("NOTE:", "NaN", "DGEBAL", "floating-point", "Iterations", "Retrying step", "No convergence", "MX")
    for i, line in enumerate(path.read_text().splitlines(), start=1):
        text = line.strip()
        if any(t in text for t in tokens):
            rows.append({"run": run, "line": i, "message": text})
    return pd.DataFrame(rows)


def config_summary() -> pd.DataFrame:
    rows = []
    for run, meta in RUNS.items():
        cfg = AUTO_DIR / f"c.bertonrestricted-task023-{meta['file'].replace('task023-', '')}"
        text = cfg.read_text()
        find = lambda pat: (re.search(pat, text).group(1).strip() if re.search(pat, text) else "")
        rows.append({
            "run": run, "config_file": cfg.name, "icp": find(r"ICP\s*=\s*(.+)"), "isp": int(find(r"ISP=(\d+)") or -1),
            "jac": int(find(r"JAC=(\d+)") or -1), "ds": float(find(r"DS=([-+0-9.eE]+)") or "nan"),
            "uses_q_z_control": "q_z=(z_W0-9000 m)/1000 m" in text, "uses_smoothed_updraft": "softplus" in text,
            "uses_p_mass_coordinate": "P_log_ratio_over_10" in text, "smoothing_width_m": SMOOTHING_WIDTH_M,
        })
    return pd.DataFrame(rows)


def seed_smoothing_crosscheck() -> pd.DataFrame:
    y, _ = seed_physical(); par = task011_parameters(); scales = residual_scales(); v = np.array([y[0], y[1], math.log(y[3])])
    smooth = restricted_residual_smoothed(v, par, residual_scale=scales)
    w_s = smoothed_updraft_value(y[0], par[0]); w_p = piecewise_updraft_value(y[0], par[0])
    return pd.DataFrame([{
        "z_m": y[0], "z_W0_m": par[0], "smooth_width_m": SMOOTHING_WIDTH_M, "delta_z_W_m": par[6],
        "eps_dimensionless": SMOOTHING_WIDTH_M / par[6], "piecewise_W_a_m_s": w_p, "smoothed_W_a_m_s": w_s,
        "updraft_perturbation_m_s": w_s - w_p, "scaled_residual_norm_at_piecewise_seed": float(np.linalg.norm(smooth)),
        "residual_du_dt_scaled": smooth[0], "residual_dw_dt_scaled": smooth[1], "residual_dlogm_dt_scaled": smooth[2],
    }])


def representative_auto_points(branch: pd.DataFrame) -> pd.DataFrame:
    picks = []
    for _, grp in branch.groupby("run"):
        picks.extend([grp.iloc[0], grp.iloc[-1]])
        for _, r in grp[grp.is_user_point | grp.ty.isin([2, 3])].iterrows():
            picks.append(r)
        if len(grp) > 4:
            picks.append(grp.iloc[len(grp)//2])
    return pd.DataFrame(picks).drop_duplicates(["run", "point", "label"]).sort_values(["run", "point"])


def eval_python_diagnostics(points: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    scales = residual_scales(); par0 = task011_parameters(); rows = []; eig_rows = []
    for _, a in points.iterrows():
        par = par0.copy(); par[0] = float(a.z_W0_m)
        v = np.array([float(a.z_m), float(a.u_m_s), math.log(float(a.m_kg))])
        y = np.array([float(a.z_m), float(a.u_m_s), 0.0, float(a.m_kg)])
        raw = restricted_residual_smoothed(v, par)
        scaled = restricted_residual_smoothed(v, par, residual_scale=scales)
        rhs = python_rhs_smoothed(y, par)
        eigs = np.linalg.eigvals(finite_difference_jacobian_smoothed(y, par))
        crit = eigs[np.argmax(eigs.real)]
        rows.append({
            "run": a.run, "point": int(a.point), "label": int(a.label), "type": a.type, "z_W0_m": float(a.z_W0_m),
            "z_m": float(a.z_m), "u_m_s": float(a.u_m_s), "m_kg": float(a.m_kg),
            "raw_restricted_residual_norm": float(np.linalg.norm(raw)), "scaled_restricted_residual_norm": float(np.linalg.norm(scaled)),
            "full_rhs_norm": float(np.linalg.norm(rhs)), "full_stable_eigenvalue_count": int(np.sum(eigs.real < 0)),
            "full_critical_real_s_inv": float(crit.real), "full_critical_imag_s_inv": float(crit.imag),
        })
        for k, ev in enumerate(eigs, start=1):
            eig_rows.append({"run": a.run, "point": int(a.point), "label": int(a.label), "z_W0_m": float(a.z_W0_m), "eigen_index": k, "real_s_inv": ev.real, "imag_s_inv": ev.imag})
    return pd.DataFrame(rows), pd.DataFrame(eig_rows)


def write_note(verdict: dict, branch: pd.DataFrame, notes: pd.DataFrame, seed: pd.DataFrame, diag: pd.DataFrame) -> None:
    plus = branch[branch.run == "z-plus"]; minus = branch[branch.run == "z-minus"]
    note_lines = "\n".join(f"- `{r.run}` line {int(r.line)}: {r.message}" for r in notes.head(10).itertuples()) or "- No convergence diagnostics parsed."
    DOC.write_text(
        "# TASK-023 smoothed restricted z_W0 continuation verdict\n\n"
        "TASK-023 reuses the TASK-019 restricted 3D AUTO formulation: `Z=(z-z_seed)/100`, `U=(u-u_seed)/(1 m/s)`, "
        "`P=M/10`, row-scaled residuals, and `m=m_seed*exp(10P)`. The active control is "
        "`q_z=(z_W0-9000 m)/1000 m`, so physical `z_W0=9000+1000 q_z` metres.\n\n"
        "## Smoothed updraft profile\n\n"
        "The original Berton profile is `W_a(z)=W_a0*clip((z-(z_W0-Delta_z_W))/Delta_z_W,0,1)`. "
        "The smoothed profile used here is `W_a0*eps*[softplus(x/eps)-softplus((x-1)/eps)]`, "
        "where `x=(z-(z_W0-Delta_z_W))/Delta_z_W`, `softplus(y)=log(1+exp(y))`, "
        f"and `eps={SMOOTHING_WIDTH_M:g} m / Delta_z_W = {SMOOTHING_WIDTH_M/DELTA_Z_W:.6g}`. "
        "This is the original ramp/plateau in the zero-width limit but removes the derivative jump at the ramp base and plateau transition.\n\n"
        "## Commands\n\n```bash\n"
        "bash episodes/07-restricted-equilibrium-auto/auto/berton_restricted_task023_zw0_smooth/run_auto.sh\n"
        "uv run python episodes/07-restricted-equilibrium-auto/scripts/berton_restricted_task023_zw0_smooth.py\n"
        "```\n\n"
        "## AUTO result\n\n"
        f"The upward run accepted `{len(plus)}` rows and reached `z_W0={plus.z_W0_m.max() if len(plus) else float('nan'):.1f} m`, approaching the smoothed plateau transition at the seed before DGEBAL/floating-point failure. "
        f"The downward run accepted `{len(minus)}` rows and reached at least the paper oscillatory `z_W0=7000 m` setting; the saved run continues farther to `z_W0={minus.z_W0_m.min() if len(minus) else float('nan'):.1f} m` before MX. "
        "There is no HB label in the accepted branch output. The asymmetric result is physically interpretable: lowering z_W0 leaves the seed on a saturated plateau and barely perturbs the restricted equilibrium, while raising z_W0 moves the seed into the smoothed ramp/transition region.\n\n"
        "## Python checks\n\n"
        f"At the TASK-011 seed the smoothing perturbation in W_a is `{seed.updraft_perturbation_m_s.iloc[0]:.3e} m/s` and the scaled residual norm is `{seed.scaled_residual_norm_at_piecewise_seed.iloc[0]:.3e}`. "
        f"Representative AUTO points have max Python smoothed scaled residual `{diag.scaled_restricted_residual_norm.max() if len(diag) else float('nan'):.3e}`. "
        f"Critical full finite-difference eigenvalue real parts span `{diag.full_critical_real_s_inv.min() if len(diag) else float('nan'):.3e}` to `{diag.full_critical_real_s_inv.max() if len(diag) else float('nan'):.3e}` s^-1.\n\n"
        "## Comparison and verdict\n\n"
        "Compared with TASK-019 W_a0, the same `P=M/10` formulation again gives a meaningful branch in the easy direction. "
        "Compared with TASK-020 H_a3, the z_W0 upward direction still shows numerical fragility near a physically important profile transition, but smoothing makes that failure a branch/ramp-region limitation rather than an artificial derivative kink. "
        "The restricted experiment supports a full-system z_W0 attempt only in a staged way: first use the smoothed profile and scaled z_W0 control, and treat the 9.6--10 km transition region as the main risk rather than claiming an AUTO-supported Hopf.\n\n"
        "## Diagnostics notes\n\n"
        f"{note_lines}\n"
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cfg = config_summary(); cfg.to_csv(OUT_DIR / "config_summary.csv", index=False)
    branch = pd.concat([parse_b(AUTO_DIR / f"b.{m['file']}", r, m) for r, m in RUNS.items()], ignore_index=True)
    branch.to_csv(OUT_DIR / "auto_branch_summary.csv", index=False)
    notes = pd.concat([parse_d(AUTO_DIR / f"d.{m['file']}", r) for r, m in RUNS.items()], ignore_index=True)
    notes.to_csv(OUT_DIR / "auto_convergence_notes.csv", index=False)
    seed = seed_smoothing_crosscheck(); seed.to_csv(OUT_DIR / "seed_smoothing_crosscheck.csv", index=False)
    reps = representative_auto_points(branch); reps.to_csv(OUT_DIR / "representative_auto_points.csv", index=False)
    diag, eig = eval_python_diagnostics(reps); diag.to_csv(OUT_DIR / "python_residual_eigen_diagnostics.csv", index=False); eig.to_csv(OUT_DIR / "python_full_eigenvalues.csv", index=False)
    smooth_samples = pd.DataFrame({
        "z_offset_m": np.linspace(-600, 900, 16),
    })
    smooth_samples["z_m"] = Z_W0_REF + smooth_samples.z_offset_m
    smooth_samples["piecewise_W_a_m_s"] = [piecewise_updraft_value(z, Z_W0_REF) for z in smooth_samples.z_m]
    smooth_samples["smoothed_W_a_m_s"] = [smoothed_updraft_value(z, Z_W0_REF) for z in smooth_samples.z_m]
    smooth_samples["updraft_difference_m_s"] = smooth_samples.smoothed_W_a_m_s - smooth_samples.piecewise_W_a_m_s
    smooth_samples.to_csv(OUT_DIR / "smoothed_updraft_profile_samples.csv", index=False)

    task019 = json.loads((TASK019_OUT / "task019_wa0_gate_verdict.json").read_text())
    task020 = json.loads((TASK020_OUT / "task020_ha3_verdict.json").read_text())
    tangent = pd.read_csv(TASK022_OUT / "seed_implicit_tangent.csv")
    plus = branch[branch.run == "z-plus"]; minus = branch[branch.run == "z-minus"]
    verdict = {
        "uses_task019_scaled_restricted_3d_gate": True,
        "uses_p_mass_coordinate": True,
        "mass_coordinate": "P=M/10 where M=log(m/m_seed)",
        "active_control_mapping": "q_z=(z_W0-9000 m)/1000 m",
        "smoothing_formula": "W_a0*eps*(softplus(x/eps)-softplus((x-1)/eps))",
        "smoothing_width_m": SMOOTHING_WIDTH_M,
        "eps_dimensionless": SMOOTHING_WIDTH_M / DELTA_Z_W,
        "task019_gate_passes": bool(task019["gate_passes_for_task020"]),
        "task020_auto_supported_hopf_candidate": bool(task020["auto_supported_hopf_candidate"]),
        "auto_hb_labels": int((branch.type == "HB").sum()),
        "auto_lp_labels": int((branch.type == "LP").sum()),
        "plus_max_z_W0_m": None if plus.empty else float(plus.z_W0_m.max()),
        "minus_min_z_W0_m": None if minus.empty else float(minus.z_W0_m.min()),
        "minus_relevant_min_z_W0_m": None if minus.empty else float(minus[minus.z_W0_m >= 7000.0].z_W0_m.min()),
        "raw_minus_extends_below_physical_paper_range": bool((minus.z_W0_m < 7000.0).any()),
        "reaches_paper_oscillatory_z_W0_7000m": bool((minus.z_W0_m <= 7000.0 + 1e-6).any()),
        "reaches_paper_steady_z_W0_10000m": bool((plus.z_W0_m >= 10000.0 - 1e-6).any()),
        "seed_smoothing_scaled_residual_norm": float(seed.scaled_residual_norm_at_piecewise_seed.iloc[0]),
        "tangent_rows": int(len(tangent)),
        "verdict": "restricted smoothed z_W0 supports a staged full-system attempt, but upward 10 km transition remains numerically fragile and no HB is AUTO-supported",
    }
    (OUT_DIR / "task023_zw0_verdict.json").write_text(json.dumps(verdict, indent=2, sort_keys=True))
    pd.DataFrame([verdict]).to_csv(OUT_DIR / "zw0_verdict_summary.csv", index=False)
    write_note(verdict, branch, notes, seed, diag)


if __name__ == "__main__":
    main()
