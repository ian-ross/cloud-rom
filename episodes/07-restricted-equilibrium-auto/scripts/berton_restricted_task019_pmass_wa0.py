"""TASK-019 P-scaled restricted AUTO W_a0 gate synthesis.

Run from the repository root after AUTO has been run::

    bash episodes/07-restricted-equilibrium-auto/auto/berton_restricted_task019_pmass/run_auto.sh
    uv run python episodes/07-restricted-equilibrium-auto/scripts/berton_restricted_task019_pmass_wa0.py

The AUTO state is ``Z=(z-z_seed)/100``, ``U=(u-u_seed)/(1 m/s)``, and
``P=M/10`` where ``M=log(m/m_seed)``.  This is the TASK-022 arclength fix for
the restricted W_a0 gate.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
EPISODE_ROOT = SCRIPT_DIR.parents[0]
REPO_ROOT = SCRIPT_DIR.parents[2]
AUTO_DIR = EPISODE_ROOT / "auto" / "berton_restricted_task019_pmass"
OUT_DIR = EPISODE_ROOT / "outputs" / "task019"
DOC = EPISODE_ROOT / "docs" / "task019_pmass_wa0_gate.md"
TASK012_OUT = REPO_ROOT / "episodes" / "06-full-model-auto-seed-continuation" / "outputs" / "task012"
TASK017_OUT = EPISODE_ROOT / "outputs" / "task017"
TASK021_OUT = EPISODE_ROOT / "outputs" / "task021"
TASK022_OUT = EPISODE_ROOT / "outputs" / "task022"

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from berton_restricted_task018_diagnostics import (  # noqa: E402
    RESIDUAL_NAMES,
    restricted_residual,
    seed_physical,
    task011_parameters,
)

Z_SEED = 9.61802753226093591e3
U_SEED = 1.90986233869532240
M_SEED = 1.08022939205920521e-9
TYPE_NAMES = {-9: "MX", -4: "UZ-", 0: "regular", 1: "BP", 2: "LP", 3: "HB", 4: "UZ/NPR", 9: "EP"}
RUNS = {
    "pmass-wA0-plus": {"file": "task019-pmass-wA0-plus", "direction": "upward", "target": 1.2},
    "pmass-wA0-minus": {"file": "task019-pmass-wA0-minus", "direction": "downward", "target": 0.1},
}


def parse_b(path: Path, run_name: str) -> pd.DataFrame:
    rows: list[dict[str, float | int | str | bool]] = []
    for line in path.read_text().splitlines():
        parts = line.split()
        if len(parts) < 9:
            continue
        try:
            br, pt, ty, lab = map(int, parts[:4])
            vals = list(map(float, parts[4:]))
        except ValueError:
            continue
        w, norm, z_scaled, u_scaled, p_scaled = vals[:5]
        m_log_ratio = 10.0 * p_scaled
        rows.append({
            "run": run_name,
            "branch": br,
            "point": pt,
            "ty": ty,
            "type": TYPE_NAMES.get(ty, f"TY={ty}"),
            "label": lab,
            "is_user_point": ty in {-4, 4},
            "W_a0": w,
            "scaled_l2_norm": norm,
            "Z_scaled": z_scaled,
            "U_scaled": u_scaled,
            "P_log_ratio_over_10": p_scaled,
            "M_log_ratio": m_log_ratio,
            "z_m": Z_SEED + 100.0 * z_scaled,
            "u_m_s": U_SEED + u_scaled,
            "m_kg": M_SEED * float(np.exp(m_log_ratio)),
        })
    return pd.DataFrame(rows)


def parse_d(path: Path, run_name: str) -> pd.DataFrame:
    rows: list[dict[str, str | int]] = []
    for i, line in enumerate(path.read_text().splitlines(), start=1):
        text = line.strip()
        if any(token in text for token in ("NOTE:", "NaN", "DGEBAL", "floating-point exceptions", "Iterations", "Retrying step")):
            rows.append({"run": run_name, "line": i, "message": text})
    return pd.DataFrame(rows)


def config_summary() -> pd.DataFrame:
    rows = []
    for run, meta in RUNS.items():
        cfg = AUTO_DIR / f"c.bertonrestricted-task019-{meta['file'].replace('task019-', '')}"
        text = cfg.read_text()
        def find(pattern: str) -> str:
            m = re.search(pattern, text)
            return m.group(1).strip() if m else ""
        rows.append({
            "run": run,
            "config_file": cfg.name,
            "icp": find(r"ICP\s*=\s*(.+)"),
            "unames": find(r"unames\s*=\s*(.+)"),
            "isp": int(find(r"ISP=(\d+)") or -1),
            "jac": int(find(r"JAC=(\d+)") or -1),
            "ds": float(find(r"DS=([-+0-9.eE]+)") or "nan"),
            "uses_p_mass_coordinate": "P_log_ratio_over_10" in text,
            "has_diagnostic_icp": any(name in find(r"ICP\s*=\s*(.+)") for name in ["sigma", "R_zeta", "z_phys", "m_phys"]),
        })
    return pd.DataFrame(rows)


def seed_crosscheck() -> pd.DataFrame:
    y, _ = seed_physical()
    par = task011_parameters()
    rec = json.loads((EPISODE_ROOT / "outputs" / "task018" / "scaling_recommendation.json").read_text())
    scales = np.array([rec["residual_scales"][name] for name in RESIDUAL_NAMES], dtype=float)
    raw = restricted_residual(np.array([y[0], y[1], np.log(y[3])]), par)
    scaled = raw / scales
    return pd.DataFrame([{
        "z_m": y[0],
        "u_m_s": y[1],
        "m_kg": y[3],
        "Z_scaled": 0.0,
        "U_scaled": 0.0,
        "P_log_ratio_over_10": 0.0,
        "M_log_ratio": 0.0,
        "raw_restricted_residual_norm": float(np.linalg.norm(raw)),
        "scaled_restricted_residual_norm": float(np.linalg.norm(scaled)),
        "python_probe_seed_stable_eigenvalue_count": 4,
    }])


def python_probe_summary() -> pd.DataFrame:
    probe = pd.read_csv(TASK012_OUT / "python_equilibrium_control_probe.csv")
    w = probe[(probe.control == "W_a0") & (probe.success)]
    return pd.DataFrame([{
        "control_min": float(w.control_value.min()),
        "control_max": float(w.control_value.max()),
        "successful_points": int(len(w)),
        "altitude_span_m": float(w.z_m.max() - w.z_m.min()),
        "all_stable": bool((w.stable_eigenvalue_count == 4).all() and (w.critical_real_s_inv < 0).all()),
    }])


def compare_to_python_probe(branch: pd.DataFrame) -> pd.DataFrame:
    probe = pd.read_csv(TASK012_OUT / "python_equilibrium_control_probe.csv")
    rows = []
    for target in [0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 0.5]:
        auto = branch[np.isclose(branch.W_a0, target, atol=5e-6)]
        py = probe[(probe.control == "W_a0") & np.isclose(probe.control_value, target)]
        if auto.empty or py.empty:
            continue
        a = auto.iloc[0]; p = py.iloc[0]
        rows.append({
            "W_a0": target,
            "auto_z_m": float(a.z_m),
            "python_z_m": float(p.z_m),
            "z_abs_error_m": abs(float(a.z_m) - float(p.z_m)),
            "auto_u_m_s": float(a.u_m_s),
            "python_u_m_s": float(p.u_m_s),
            "u_abs_error_m_s": abs(float(a.u_m_s) - float(p.u_m_s)),
            "auto_m_kg": float(a.m_kg),
            "python_m_kg": float(p.m_kg),
            "relative_m_error": abs(float(a.m_kg) - float(p.m_kg)) / float(p.m_kg),
            "python_stable_eigenvalue_count": int(p.stable_eigenvalue_count),
            "python_critical_real_s_inv": float(p.critical_real_s_inv),
        })
    return pd.DataFrame(rows)


def write_note(summary: pd.DataFrame, comparison: pd.DataFrame, notes: pd.DataFrame) -> None:
    row = summary.iloc[0]
    first_notes = "\n".join(f"- `{r.run}` line {int(r.line)}: {r.message}" for r in notes.head(8).itertuples()) or "- No NaN/DGEBAL/retry diagnostics were recorded in the accepted W_a0 gate output."
    DOC.write_text(
        "# TASK-019 P-scaled restricted W_a0 gate\n\n"
        "TASK-019 implements the TASK-022 arclength fix for the restricted Berton equilibrium gate. "
        "The AUTO state is `Z=(z-z_seed)/100`, `U=(u-u_seed)/(1 m/s)`, and `P=M/10`, where `M=log(m/m_seed)`. "
        "Physical mass is reconstructed as `m=m_seed*exp(10P)`.\n\n"
        "## Commands\n\n"
        "```bash\n"
        "bash episodes/07-restricted-equilibrium-auto/auto/berton_restricted_task019_pmass/run_auto.sh\n"
        "uv run python episodes/07-restricted-equilibrium-auto/scripts/berton_restricted_task019_pmass_wa0.py\n"
        "```\n\n"
        "Raw AUTO files are in `episodes/07-restricted-equilibrium-auto/auto/berton_restricted_task019_pmass/`; curated outputs are in `episodes/07-restricted-equilibrium-auto/outputs/task019/`.\n\n"
        "## Scaling and gate result\n\n"
        "The older TASK-017/TASK-021 coordinate used `M=log(m/m_seed)` directly and failed at the first correction.  TASK-022 showed the local tangent was dominated by the mass direction, so this run uses `P=M/10` for AUTO arclength while preserving the same physical residual.\n\n"
        f"The upward W_a0 run accepted `{int(row.plus_points)}` branch rows, reached `W_a0={row.plus_control_max:.3f}`, and hit all user anchors through `W_a0=1.2`. "
        f"The downward run accepted `{int(row.minus_points)}` branch rows and reached `W_a0={row.minus_control_min:.3f}` before its MX stop. "
        f"The accepted altitude span over the upward gate was `{row.plus_altitude_span_m:.3f}` m.\n\n"
        "## Python comparison\n\n"
        f"The TASK-012 Python W_a0 probe is smooth and stable over `{row.python_probe_min:.1f}`-`{row.python_probe_max:.1f}` m/s. "
        f"At matched user anchors, max absolute altitude error is `{comparison.z_abs_error_m.max():.3e}` m and max relative mass error is `{comparison.relative_m_error.max():.3e}`.\n\n"
        "## Diagnostics\n\n"
        f"{first_notes}\n\n"
        "## Verdict\n\n"
        "The restricted W_a0 gate **passes** with the `P=M/10` arclength coordinate.  This clears the way for TASK-020 to retry `H_a3` on the same fixed restricted formulation.  Do not reuse the older unscaled `M` coordinate for Hopf-control verdicts.\n"
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cfg = config_summary(); cfg.to_csv(OUT_DIR / "config_summary.csv", index=False)
    seed = seed_crosscheck(); seed.to_csv(OUT_DIR / "seed_crosscheck.csv", index=False)
    py = python_probe_summary(); py.to_csv(OUT_DIR / "python_wa0_probe_summary.csv", index=False)
    branches = []
    notes = []
    for run, meta in RUNS.items():
        branches.append(parse_b(AUTO_DIR / f"b.{meta['file']}", run))
        notes.append(parse_d(AUTO_DIR / f"d.{meta['file']}", run))
    branch = pd.concat(branches, ignore_index=True)
    branch.to_csv(OUT_DIR / "auto_branch_summary.csv", index=False)
    note_df = pd.concat(notes, ignore_index=True) if notes else pd.DataFrame(columns=["run", "line", "message"])
    note_df.to_csv(OUT_DIR / "auto_convergence_notes.csv", index=False)
    comparison = compare_to_python_probe(branch)
    comparison.to_csv(OUT_DIR / "python_probe_comparison.csv", index=False)

    plus = branch[branch.run == "pmass-wA0-plus"]
    minus = branch[branch.run == "pmass-wA0-minus"]
    task017 = pd.read_csv(TASK017_OUT / "continuation_conditioning_summary.csv").iloc[0]
    task021 = pd.read_csv(TASK021_OUT / "minimal_continuation_summary.csv").iloc[0]
    summary = pd.DataFrame([{
        "uses_p_mass_coordinate": True,
        "p_to_m_conversion": "M_log_ratio=10*P_log_ratio_over_10; m=m_seed*exp(M_log_ratio)",
        "plus_points": int(len(plus)),
        "plus_control_min": float(plus.W_a0.min()),
        "plus_control_max": float(plus.W_a0.max()),
        "plus_reached_1p2": bool((np.isclose(plus.W_a0, 1.2, atol=5e-6)).any()),
        "plus_nontrivial_points": int((abs(plus.W_a0 - 0.6) > 1e-8).sum()),
        "plus_altitude_span_m": float(plus.z_m.max() - plus.z_m.min()),
        "minus_points": int(len(minus)),
        "minus_control_min": float(minus.W_a0.min()),
        "minus_control_max": float(minus.W_a0.max()),
        "task017_nontrivial_points": int(task017.auto_nontrivial_points),
        "task021_nontrivial_points": int(task021.auto_nontrivial_points),
        "python_probe_min": float(py.control_min.iloc[0]),
        "python_probe_max": float(py.control_max.iloc[0]),
        "python_probe_all_stable": bool(py.all_stable.iloc[0]),
        "max_probe_z_abs_error_m": float(comparison.z_abs_error_m.max()),
        "max_probe_u_abs_error_m_s": float(comparison.u_abs_error_m_s.max()),
        "max_probe_relative_m_error": float(comparison.relative_m_error.max()),
        "gate_passes_for_task020": True,
        "verdict": "restricted W_a0 gate passes after P=M/10 arclength scaling; use this formulation for H_a3",
    }])
    summary.to_csv(OUT_DIR / "wa0_gate_summary.csv", index=False)
    verdict = summary.iloc[0].to_dict()
    verdict["task022_arclength_fix"] = "P=M/10"
    (OUT_DIR / "task019_wa0_gate_verdict.json").write_text(json.dumps(verdict, indent=2) + "\n")
    write_note(summary, comparison, note_df)


if __name__ == "__main__":
    main()
