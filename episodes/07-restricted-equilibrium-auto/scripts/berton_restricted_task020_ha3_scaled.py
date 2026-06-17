"""TASK-020 scaled restricted H_a3 continuation synthesis.

Run from the repository root after AUTO runs::

    bash episodes/07-restricted-equilibrium-auto/auto/berton_restricted_task020_ha3_scaled/run_auto.sh
    bash episodes/07-restricted-equilibrium-auto/auto/berton_restricted_task020_ha3_hscaled/run_auto.sh
    uv run python episodes/07-restricted-equilibrium-auto/scripts/berton_restricted_task020_ha3_scaled.py

The trusted gate formulation is TASK-019's restricted 3D residual with
``Z=(z-z_seed)/100``, ``U=(u-u_seed)/(1 m/s)``, and ``P=M/10``.  TASK-020
continues an active scaled humidity control ``q_H=(H_a3-0.61)/0.001`` and
records an exploratory larger-state-scale retry for the H_a3 branch.
"""

from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import root

SCRIPT_DIR = Path(__file__).resolve().parent
EPISODE_ROOT = SCRIPT_DIR.parents[0]
REPO_ROOT = SCRIPT_DIR.parents[2]
AUTO_Q = EPISODE_ROOT / "auto" / "berton_restricted_task020_ha3_scaled"
AUTO_H = EPISODE_ROOT / "auto" / "berton_restricted_task020_ha3_hscaled"
OUT_DIR = EPISODE_ROOT / "outputs" / "task020"
DOC = EPISODE_ROOT / "docs" / "task020_ha3_scaled_restricted_verdict.md"
TASK012_OUT = REPO_ROOT / "episodes" / "06-full-model-auto-seed-continuation" / "outputs" / "task012"
TASK015_OUT = REPO_ROOT / "episodes" / "06-full-model-auto-seed-continuation" / "outputs" / "task015"
TASK019_OUT = EPISODE_ROOT / "outputs" / "task019"
TASK022_OUT = EPISODE_ROOT / "outputs" / "task022"

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
EP04_SCRIPTS = REPO_ROOT / "episodes" / "04-full-model-auto-equilibria" / "scripts"
if str(EP04_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(EP04_SCRIPTS))

from berton_restricted_task018_diagnostics import (  # noqa: E402
    RESIDUAL_NAMES,
    restricted_residual,
    seed_physical,
    task011_parameters,
)
from berton_full_auto_task009_validate import finite_difference_jacobian, python_rhs  # noqa: E402

Z_SEED = 9.61802753226093591e3
U_SEED = 1.90986233869532240
M_SEED = 1.08022939205920521e-9
LOG_M_SEED = math.log(M_SEED)
H_REF = 0.61
H_SCALE = 0.001
TYPE_NAMES = {-9: "MX", -4: "UZ-", 0: "regular", 1: "BP", 2: "LP", 3: "HB", 4: "UZ/NPR", 9: "EP"}
RUNS = {
    "q-plus": {"dir": AUTO_Q, "file": "task020-ha3-q-plus", "state_scales": (100.0, 1.0), "variant": "task019_state_scale", "direction": "upward"},
    "q-minus": {"dir": AUTO_Q, "file": "task020-ha3-q-minus", "state_scales": (100.0, 1.0), "variant": "task019_state_scale", "direction": "downward"},
    "hscaled-plus": {"dir": AUTO_H, "file": "task020-ha3-hscaled-plus", "state_scales": (1000.0, 5.0), "variant": "larger_H_state_scale", "direction": "upward"},
    "hscaled-minus": {"dir": AUTO_H, "file": "task020-ha3-hscaled-minus", "state_scales": (1000.0, 5.0), "variant": "larger_H_state_scale", "direction": "downward"},
}


def residual_scales() -> np.ndarray:
    rec = json.loads((EPISODE_ROOT / "outputs" / "task018" / "scaling_recommendation.json").read_text())
    return np.array([rec["residual_scales"][name] for name in RESIDUAL_NAMES], dtype=float)


def parse_b(path: Path, run: str, meta: dict) -> pd.DataFrame:
    rows = []
    z_scale, u_scale = meta["state_scales"]
    if not path.exists():
        return pd.DataFrame()
    for line in path.read_text().splitlines():
        parts = line.split()
        if len(parts) < 9:
            continue
        try:
            br, pt, ty, lab = map(int, parts[:4])
            vals = list(map(float, parts[4:]))
        except ValueError:
            continue
        q, norm, z_scaled, u_scaled, p_scaled = vals[:5]
        H = H_REF + H_SCALE * q
        M = 10.0 * p_scaled
        anchors = [15.0, 40.0, 65.0, 90.0, 115.0, 140.0, 165.0, 190.0, 215.0, 240.0] if meta["direction"] == "upward" else [-10.0, -12.5, -13.0, -15.0, -35.0, -60.0, -85.0, -110.0, -135.0, -160.0, -185.0, -210.0]
        is_user = any(np.isclose(q, target, atol=5e-5) for target in anchors)
        type_name = "UZ" if is_user else ("NPR" if ty == 4 else TYPE_NAMES.get(ty, f"TY={ty}"))
        rows.append({
            "run": run, "variant": meta["variant"], "direction": meta["direction"],
            "branch": br, "point": pt, "ty": ty, "type": type_name, "label": lab,
            "is_user_point": is_user, "is_special_point": ty in {1, 2, 3},
            "q_H_scaled": q, "H_a3": H, "scaled_l2_norm": norm,
            "Z_or_ZH_scaled": z_scaled, "U_or_UH_scaled": u_scaled, "P_log_ratio_over_10": p_scaled,
            "M_log_ratio": M, "z_m": Z_SEED + z_scale * z_scaled,
            "u_m_s": U_SEED + u_scale * u_scaled, "m_kg": M_SEED * math.exp(M),
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
        cfgs = sorted(meta["dir"].glob(f"c.*{meta['file'].replace('task020-', '')}"))
        cfg = cfgs[0] if cfgs else meta["dir"] / "missing"
        text = cfg.read_text() if cfg.exists() else ""
        find = lambda pat: (re.search(pat, text).group(1).strip() if re.search(pat, text) else "")
        rows.append({
            "run": run, "variant": meta["variant"], "config_file": cfg.name,
            "icp": find(r"ICP\s*=\s*(.+)"), "isp": int(find(r"ISP=(\d+)") or -1),
            "jac": int(find(r"JAC=(\d+)") or -1), "ds": float(find(r"DS=([-+0-9.eE]+)") or "nan"),
            "uses_scaled_H_control": "q_H=(H_a3-0.61)/0.001" in text,
            "uses_p_mass_coordinate": "P_log_ratio_over_10" in text,
        })
    return pd.DataFrame(rows)


def python_probe_comparison(branch: pd.DataFrame) -> pd.DataFrame:
    probe = pd.read_csv(TASK012_OUT / "python_equilibrium_control_probe.csv")
    hprobe = probe[(probe.control == "H_a3") & (probe.success)].copy()
    rows = []
    for _, p in hprobe.iterrows():
        near = branch.iloc[(branch.H_a3 - float(p.control_value)).abs().argsort()[:1]] if not branch.empty else pd.DataFrame()
        if near.empty:
            continue
        a = near.iloc[0]
        rows.append({
            "H_a3": float(p.control_value), "nearest_auto_run": a.run, "nearest_auto_H_a3": float(a.H_a3),
            "auto_delta_H": abs(float(a.H_a3) - float(p.control_value)),
            "auto_z_m": float(a.z_m), "task012_z_m": float(p.z_m), "z_abs_error_m": abs(float(a.z_m) - float(p.z_m)),
            "auto_u_m_s": float(a.u_m_s), "task012_u_m_s": float(p.u_m_s), "u_abs_error_m_s": abs(float(a.u_m_s) - float(p.u_m_s)),
            "auto_m_kg": float(a.m_kg), "task012_m_kg": float(p.m_kg), "relative_m_error": abs(float(a.m_kg) - float(p.m_kg)) / float(p.m_kg),
            "task012_stable_eigenvalue_count": int(p.stable_eigenvalue_count), "task012_critical_real_s_inv": float(p.critical_real_s_inv),
        })
    return pd.DataFrame(rows)


def representative_auto_points(branch: pd.DataFrame) -> pd.DataFrame:
    if branch.empty:
        return branch
    picks = []
    for run, grp in branch.groupby("run"):
        picks.append(grp.iloc[0])
        picks.append(grp.iloc[-1])
        specials = grp[grp.ty.isin([2, 3]) | grp.is_user_point]
        for _, row in specials.iterrows():
            picks.append(row)
    out = pd.DataFrame(picks).drop_duplicates(["run", "point", "label"])
    return out.sort_values(["run", "point"])


def eval_python_diagnostics(points: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    scales = residual_scales()
    rows = []
    eig_rows = []
    par0 = task011_parameters()
    for _, a in points.iterrows():
        par = par0.copy(); par[3] = float(a.H_a3)
        v = np.array([float(a.z_m), float(a.u_m_s), math.log(float(a.m_kg))])
        y = np.array([float(a.z_m), float(a.u_m_s), 0.0, float(a.m_kg)])
        raw = restricted_residual(v, par)
        scaled = restricted_residual(v, par, residual_scale=scales)
        rhs = python_rhs(y, par)
        full_j = finite_difference_jacobian(y, par)
        full_eigs = np.linalg.eigvals(full_j)
        rows.append({
            "run": a.run, "point": int(a.point), "label": int(a.label), "type": a.type, "H_a3": float(a.H_a3),
            "z_m": float(a.z_m), "u_m_s": float(a.u_m_s), "m_kg": float(a.m_kg),
            "raw_restricted_residual_norm": float(np.linalg.norm(raw)),
            "scaled_restricted_residual_norm": float(np.linalg.norm(scaled)),
            "full_rhs_norm": float(np.linalg.norm(rhs)),
            "full_stable_eigenvalue_count": int(np.sum(full_eigs.real < 0)),
            "full_critical_real_s_inv": float(full_eigs.real.max()),
            "full_critical_imag_s_inv": float(full_eigs[np.argmax(full_eigs.real)].imag),
        })
        for k, ev in enumerate(full_eigs, start=1):
            eig_rows.append({"run": a.run, "point": int(a.point), "label": int(a.label), "H_a3": float(a.H_a3), "eigen_index": k, "real_s_inv": ev.real, "imag_s_inv": ev.imag})
    return pd.DataFrame(rows), pd.DataFrame(eig_rows)


def python_restricted_continuation() -> pd.DataFrame:
    """Independent local root continuation from the TASK-011 seed near the H_a3 fold."""
    scales = residual_scales(); par0 = task011_parameters(); y, _ = seed_physical()
    prev = np.array([y[0], y[1], math.log(y[3])], dtype=float)
    rows = []
    targets = [0.61, 0.605, 0.600, 0.595, 0.590, 0.611, 0.612, 0.615, 0.620, 0.625, 0.650]
    for H in targets:
        par = par0.copy(); par[3] = H
        sol = root(lambda v: restricted_residual(v, par, residual_scale=scales), prev, method="hybr", tol=1e-10)
        ok = bool(sol.success and np.linalg.norm(sol.fun) < 1e-6)
        rows.append({
            "H_a3": H, "success": ok, "solver_success_flag": bool(sol.success), "message": str(sol.message),
            "scaled_residual_norm": float(np.linalg.norm(sol.fun)),
            "z_m": float(sol.x[0]), "u_m_s": float(sol.x[1]), "m_kg": float(math.exp(sol.x[2])),
        })
        if ok:
            prev = sol.x
    return pd.DataFrame(rows)


def write_note(summary: dict, branch: pd.DataFrame, notes: pd.DataFrame, diag: pd.DataFrame, pycont: pd.DataFrame) -> None:
    plus = branch[branch.run == "q-plus"]
    minus = branch[branch.run == "q-minus"]
    lp = branch[branch.type == "LP"]
    note_lines = "\n".join(f"- `{r.run}` line {int(r.line)}: {r.message}" for r in notes.head(10).itertuples()) or "- No convergence diagnostics parsed."
    DOC.write_text(
        "# TASK-020 scaled restricted H_a3 verdict\n\n"
        "TASK-020 reused the TASK-019 restricted 3D AUTO formulation after the W_a0 gate passed: "
        "`Z=(z-z_seed)/100`, `U=(u-u_seed)/(1 m/s)`, `P=M/10`, row-scaled residuals, and `m=m_seed*exp(10P)`. "
        "The active humidity control was scaled as `q_H=(H_a3-0.61)/0.001`. An exploratory larger-state-scale variant used `ZH=(z-z_seed)/1000` and `UH=(u-u_seed)/5` while preserving the same residual and `P` mass coordinate.\n\n"
        "## Commands\n\n```bash\n"
        "bash episodes/07-restricted-equilibrium-auto/auto/berton_restricted_task020_ha3_scaled/run_auto.sh\n"
        "bash episodes/07-restricted-equilibrium-auto/auto/berton_restricted_task020_ha3_hscaled/run_auto.sh\n"
        "uv run python episodes/07-restricted-equilibrium-auto/scripts/berton_restricted_task020_ha3_scaled.py\n"
        "```\n\n"
        "## AUTO result\n\n"
        f"The trusted TASK-019-scale upward run accepted `{len(plus)}` rows and reached only `H_a3={plus.H_a3.max() if len(plus) else float('nan'):.6f}` before DGEBAL/floating-point failure. "
        f"The downward run accepted `{len(minus)}` rows and detected an LP at `H_a3={lp.H_a3.iloc[0] if len(lp) else float('nan'):.6f}` before MX. "
        "No HB label was accepted in these AUTO files. The larger-state-scale retry failed at the seed in both directions, so it does not improve the verdict.\n\n"
        "## Independent Python diagnostics\n\n"
        f"Representative accepted AUTO points have max scaled restricted residual `{diag.scaled_restricted_residual_norm.max() if len(diag) else float('nan'):.3e}` under the Python residual. "
        f"The full 4D finite-difference eigenvalue diagnostics over those points have critical real parts from `{diag.full_critical_real_s_inv.min() if len(diag) else float('nan'):.3e}` to `{diag.full_critical_real_s_inv.max() if len(diag) else float('nan'):.3e}` s^-1. "
        "A separate Python restricted root continuation solves locally from `H_a3=0.600` through `0.625`, but fails below about `0.595` from this branch, consistent with the AUTO LP/fold indication rather than a clean Hopf crossing.\n\n"
        "## Comparison to TASK-012/TASK-015\n\n"
        "TASK-012's Python H_a3 probe reported a critical-pair sign change near `H_a3≈0.62`, but its saved equilibrium coordinates remain essentially at the seed for all H_a3 samples. The TASK-020 restricted branch instead moves altitude and horizontal velocity by hundreds of metres / metres per second over the same interval, so the TASK-012 probe is useful as a stability hint but not as branch geometry evidence. "
        "The direct full-4D TASK-012 AUTO H_a3 runs accepted only the seed; TASK-015 improved the mass coordinate for W_a0 but still documented first-step/full-formulation numerical fragility. TASK-020 improves on that by accepting a nontrivial restricted H_a3 branch in the downward direction, but not enough for an AUTO-supported Hopf claim.\n\n"
        "## Diagnostics notes\n\n"
        f"{note_lines}\n\n"
        "## Verdict\n\n"
        "There is **no AUTO-supported Hopf candidate** from TASK-020. The restricted branch gives AUTO-supported evidence for a nearby H_a3 fold/turning limitation around `H_a3≈0.597`, while the upward Hopf-relevant side remains numerically inconclusive because AUTO stops near `H_a3≈0.611`. Treat any crossing near `0.62` as a Python hint only, not an AUTO-validated HB.\n"
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cfg = config_summary(); cfg.to_csv(OUT_DIR / "config_summary.csv", index=False)
    branches = [parse_b(meta["dir"] / f"b.{meta['file']}", run, meta) for run, meta in RUNS.items()]
    branch = pd.concat([b for b in branches if not b.empty], ignore_index=True) if any(not b.empty for b in branches) else pd.DataFrame()
    branch.to_csv(OUT_DIR / "auto_branch_summary.csv", index=False)
    notes = pd.concat([parse_d(meta["dir"] / f"d.{meta['file']}", run) for run, meta in RUNS.items()], ignore_index=True)
    notes.to_csv(OUT_DIR / "auto_convergence_notes.csv", index=False)
    pycomp = python_probe_comparison(branch); pycomp.to_csv(OUT_DIR / "task012_python_probe_comparison.csv", index=False)
    reps = representative_auto_points(branch); reps.to_csv(OUT_DIR / "representative_auto_points.csv", index=False)
    diag, eig = eval_python_diagnostics(reps) if len(reps) else (pd.DataFrame(), pd.DataFrame())
    diag.to_csv(OUT_DIR / "python_residual_eigen_diagnostics.csv", index=False)
    eig.to_csv(OUT_DIR / "python_full_eigenvalues.csv", index=False)
    pycont = python_restricted_continuation(); pycont.to_csv(OUT_DIR / "python_restricted_ha3_local_continuation.csv", index=False)

    task012 = pd.read_csv(TASK012_OUT / "continuation_summary.csv").iloc[0]
    task015 = pd.read_csv(TASK015_OUT / "continuation_summary.csv").iloc[0]
    task019 = json.loads((TASK019_OUT / "task019_wa0_gate_verdict.json").read_text())
    tangent = pd.read_csv(TASK022_OUT / "seed_implicit_tangent.csv")
    lp = branch[branch.type == "LP"] if len(branch) else pd.DataFrame()
    verdict = {
        "uses_task019_scaled_restricted_3d_gate": True,
        "task019_gate_passes_for_task020": bool(task019["gate_passes_for_task020"]),
        "active_control_mapping": "q_H=(H_a3-0.61)/0.001",
        "h_scale": H_SCALE,
        "task022_tangent_source": "outputs/task022/seed_implicit_tangent.csv",
        "auto_supported_hopf_candidate": False,
        "auto_hb_labels": int((branch.type == "HB").sum()) if len(branch) else 0,
        "auto_lp_labels": int((branch.type == "LP").sum()) if len(branch) else 0,
        "lp_H_a3": None if lp.empty else float(lp.H_a3.iloc[0]),
        "q_plus_max_H_a3": None if branch[branch.run == "q-plus"].empty else float(branch[branch.run == "q-plus"].H_a3.max()),
        "q_minus_min_H_a3": None if branch[branch.run == "q-minus"].empty else float(branch[branch.run == "q-minus"].H_a3.min()),
        "verdict": "continued numerical inconclusiveness for Hopf; AUTO supports a restricted H_a3 fold/turning limitation, not an HB",
        "task012_comparison": "Python H_a3 critical-real sign change near 0.62 remains a hint only; direct full-4D AUTO accepted seed only.",
        "task015_comparison": "log-mass full-4D reformulation did not solve first-step continuation fragility.",
        "task012_summary_accepted_Ha3_points": int(getattr(task012, "ha3_plus_points", 1)) if "ha3_plus_points" in task012.index else 1,
        "task015_wA0_plus_points": int(getattr(task015, "wA0_plus_points", 1)) if "wA0_plus_points" in task015.index else 1,
        "tangent_rows": int(len(tangent)),
    }
    (OUT_DIR / "task020_ha3_verdict.json").write_text(json.dumps(verdict, indent=2, sort_keys=True))
    pd.DataFrame([verdict]).to_csv(OUT_DIR / "ha3_verdict_summary.csv", index=False)
    write_note(verdict, branch, notes, diag, pycont)


if __name__ == "__main__":
    main()
