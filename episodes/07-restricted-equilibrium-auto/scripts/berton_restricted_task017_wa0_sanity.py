"""TASK-017 W_a0 conditioning sanity-check synthesis.

Run from the repository root::

    uv run python episodes/07-restricted-equilibrium-auto/scripts/berton_restricted_task017_wa0_sanity.py

The script parses the restricted/scaled TASK-017 AUTO attempt, cross-checks the
TASK-011 seed in the TASK-018 coordinates, compares against the TASK-012 Python
W_a0 probe and TASK-015 full-4D log-mass retry, and writes a conditioning-gate
verdict.  The negative AUTO result is intentionally preserved: the restricted
problem still accepts only the seed in this AUTO configuration, so H_a3 failures
cannot yet be treated as control-specific.
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
AUTO_DIR = EPISODE_ROOT / "auto" / "berton_restricted_task017"
OUT_DIR = EPISODE_ROOT / "outputs" / "task017"
TASK012_OUT = REPO_ROOT / "episodes" / "06-full-model-auto-seed-continuation" / "outputs" / "task012"
TASK015_OUT = REPO_ROOT / "episodes" / "06-full-model-auto-seed-continuation" / "outputs" / "task015"
TASK018_OUT = EPISODE_ROOT / "outputs" / "task018"
DOC = EPISODE_ROOT / "docs" / "task017_wa0_conditioning_sanity_check.md"

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from berton_restricted_task018_diagnostics import (  # noqa: E402
    RESIDUAL_NAMES,
    restricted_residual,
    seed_physical,
    task011_parameters,
)

TYPE_NAMES = {-9: "MX", -4: "UZ-", 0: "regular", 1: "BP", 2: "LP", 3: "HB", 4: "UZ/NPR", 9: "EP"}
RUNS = {
    "restricted-wA0-plus": {"file": "task017-restricted-wA0-plus", "direction": "upward", "target": 1.2},
    "restricted-wA0-minus": {"file": "task017-restricted-wA0-minus", "direction": "downward", "target": 0.1},
}


def parse_b(path: Path, run_name: str) -> pd.DataFrame:
    rows: list[dict[str, float | int | str]] = []
    for line in path.read_text().splitlines():
        parts = line.split()
        if len(parts) < 10:
            continue
        try:
            br, pt, ty, lab = map(int, parts[:4])
            vals = list(map(float, parts[4:]))
        except ValueError:
            continue
        row = {
            "run": run_name,
            "branch": br,
            "point": pt,
            "ty": ty,
            "type": TYPE_NAMES.get(ty, f"TY={ty}"),
            "label": lab,
            "control": "W_a0",
            "control_value": vals[0],
            "scaled_l2_norm": vals[1],
            "z_W0": vals[2],
            "H_a3": vals[3],
            "z_m": vals[4] if len(vals) > 4 else np.nan,
            "u_m_s": vals[5] if len(vals) > 5 else np.nan,
            "m_kg": vals[6] if len(vals) > 6 else np.nan,
            "sigma_S": vals[7] if len(vals) > 7 else np.nan,
        }
        rows.append(row)
    return pd.DataFrame(rows)


def parse_d(path: Path, run_name: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    eig_rows: list[dict[str, float | int | str]] = []
    notes: list[dict[str, str | int]] = []
    current_label: int | None = None
    for line in path.read_text().splitlines():
        m = re.match(r"\s*\d+\s+(\d+)\s+Eigenvalues\s+:\s+Stable:\s+(\d+)", line)
        if m:
            current_label = int(m.group(1))
            notes.append({"run": run_name, "label": current_label, "message": f"Stable eigenvalues: {m.group(2)}"})
            continue
        m = re.search(r"Eigenvalue\s+(\d+):\s+([+-]?\d*\.\d+E[+-]?\d+)\s+([+-]?\d*\.\d+E[+-]?\d+)", line)
        if m and current_label is not None:
            eig_rows.append({"run": run_name, "label": current_label, "eigenvalue_index": int(m.group(1)), "real_s_inv": float(m.group(2)), "imag_s_inv": float(m.group(3))})
            continue
        if any(token in line for token in ("NOTE:", "DGEBAL", "NaN", "No convergence", "floating-point exceptions")):
            notes.append({"run": run_name, "label": current_label or 0, "message": line.strip()})
    return pd.DataFrame(eig_rows), pd.DataFrame(notes)


def seed_crosscheck() -> pd.DataFrame:
    y_seed, _ = seed_physical()
    par = task011_parameters()
    v = np.array([y_seed[0], y_seed[1], np.log(y_seed[3])], dtype=float)
    raw = restricted_residual(v, par)
    rec = json.loads((TASK018_OUT / "scaling_recommendation.json").read_text())
    scales = np.array([rec["residual_scales"][name] for name in RESIDUAL_NAMES], dtype=float)
    scaled = raw / scales
    return pd.DataFrame([{
        "z_m": y_seed[0],
        "u_m_s": y_seed[1],
        "w_m_s": y_seed[2],
        "m_kg": y_seed[3],
        "Z_scaled": 0.0,
        "U_scaled": 0.0,
        "M_log_ratio": 0.0,
        "raw_restricted_residual_norm": float(np.linalg.norm(raw)),
        "scaled_restricted_residual_norm": float(np.linalg.norm(scaled)),
        "residual_scale_du_dt": scales[0],
        "residual_scale_dw_dt": scales[1],
        "residual_scale_dlogm_dt": scales[2],
    }])


def python_probe_summary() -> pd.DataFrame:
    probe = pd.read_csv(TASK012_OUT / "python_equilibrium_control_probe.csv")
    w = probe[(probe["control"] == "W_a0") & (probe["success"])]
    return pd.DataFrame([{
        "source": "TASK-012 Python W_a0 probe",
        "control_min": float(w.control_value.min()),
        "control_max": float(w.control_value.max()),
        "successful_points": int(len(w)),
        "z_min_m": float(w.z_m.min()),
        "z_max_m": float(w.z_m.max()),
        "altitude_span_m": float(w.z_m.max() - w.z_m.min()),
        "all_stable": bool((w.stable_eigenvalue_count == 4).all() and (w.critical_real_s_inv < 0).all()),
        "critical_real_max_s_inv": float(w.critical_real_s_inv.max()),
    }])


def write_note(summary: pd.DataFrame, verdict: dict[str, object]) -> None:
    row = summary.iloc[0]
    DOC.write_text(
        "# TASK-017 W_a0 conditioning sanity check\n\n"
        "This note uses `W_a0` as a non-Hopf conditioning control for the Berton equilibrium seed. "
        "The seed is the TASK-011/TASK-012 stable equilibrium translated into the TASK-018 restricted/scaled coordinates "
        "`Z=(z-z_seed)/100 m`, `U=(u-u_seed)/(1 m/s)`, `M=log(m/m_seed)`, with `w=0`.\n\n"
        "## Commands and artifacts\n\n"
        "```bash\n"
        "bash episodes/07-restricted-equilibrium-auto/auto/berton_restricted_task017/run_auto.sh\n"
        "uv run python episodes/07-restricted-equilibrium-auto/scripts/berton_restricted_task017_wa0_sanity.py\n"
        "```\n\n"
        "Curated outputs are in `episodes/07-restricted-equilibrium-auto/outputs/task017/`. Raw AUTO files are saved as "
        "`b./s./d.task017-restricted-wA0-{plus,minus}` under `episodes/07-restricted-equilibrium-auto/auto/berton_restricted_task017/`.\n\n"
        "## Python expectation\n\n"
        f"The TASK-012 Python probe follows stable W_a0 equilibria over `{row.python_probe_min:.2f}`-`{row.python_probe_max:.2f}` m/s, "
        f"with altitude moving by `{row.python_probe_altitude_span_m:.3f}` m and all saved critical real parts negative.\n\n"
        "## AUTO result\n\n"
        f"The restricted/scaled AUTO retry accepted `{int(row.auto_total_points)}` total printed branch points and "
        f"`{int(row.auto_nontrivial_points)}` non-seed/nontrivial points. The covered AUTO W_a0 range is "
        f"`{row.auto_control_min:.3f}`-`{row.auto_control_max:.3f}` m/s, i.e. only the seed value. "
        "The diagnostic logs retain DGEBAL/NaN/floating-point failure messages before any user anchor is reached.\n\n"
        "## Conditioning verdict\n\n"
        f"**Verdict:** {verdict['conditioning_verdict']}\n\n"
        "Because the easy W_a0 gate still fails before a nontrivial branch point, current H_a3 failures should **not** be interpreted as control-specific Hopf evidence. "
        "They remain evidence of broader AUTO formulation/conditioning or problem-setup fragility despite the Python equilibrium branch being smooth and stable.\n\n"
        "Residual risk: the restricted/scaled residual is much better conditioned locally per TASK-018, but the AUTO equilibrium setup still encounters first-step linear-algebra divergence; further work should isolate AUTO arclength/Jacobian scaling details before H_a3 Hopf work.\n"
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    seed_crosscheck().to_csv(OUT_DIR / "seed_restricted_crosscheck.csv", index=False)
    py_summary = python_probe_summary()
    py_summary.to_csv(OUT_DIR / "python_wa0_probe_summary.csv", index=False)

    branches = []
    eigs = []
    notes = []
    for run_name, meta in RUNS.items():
        branches.append(parse_b(AUTO_DIR / f"b.{meta['file']}", run_name))
        e, n = parse_d(AUTO_DIR / f"d.{meta['file']}", run_name)
        eigs.append(e)
        notes.append(n)
    branch = pd.concat(branches, ignore_index=True)
    auto_eigs = pd.concat(eigs, ignore_index=True) if eigs else pd.DataFrame()
    auto_notes = pd.concat(notes, ignore_index=True) if notes else pd.DataFrame()
    branch.to_csv(OUT_DIR / "auto_branch_summary.csv", index=False)
    auto_eigs.to_csv(OUT_DIR / "auto_eigenvalue_diagnostics.csv", index=False)
    auto_notes.to_csv(OUT_DIR / "auto_convergence_notes.csv", index=False)

    seed_w = 0.6
    nontrivial = branch[np.abs(branch.control_value - seed_w) > 1e-8]
    seed_state = seed_crosscheck().iloc[0]
    task015 = pd.read_csv(TASK015_OUT / "continuation_summary.csv")
    failure_note = " | ".join(auto_notes.message.astype(str).head(8)) if not auto_notes.empty else ""
    summary = pd.DataFrame([{
        "auto_total_points": int(len(branch)),
        "auto_nontrivial_points": int(len(nontrivial)),
        "auto_control_min": float(branch.control_value.min()),
        "auto_control_max": float(branch.control_value.max()),
        "auto_altitude_span_m": float(branch.z_m.max() - branch.z_m.min()),
        "seed_scaled_residual_norm": float(seed_state.scaled_restricted_residual_norm),
        "python_probe_min": float(py_summary.control_min.iloc[0]),
        "python_probe_max": float(py_summary.control_max.iloc[0]),
        "python_probe_altitude_span_m": float(py_summary.altitude_span_m.iloc[0]),
        "python_probe_all_stable": bool(py_summary.all_stable.iloc[0]),
        "task015_full4d_nontrivial_points": int(pd.read_csv(TASK015_OUT / "auto_branch_summary.csv").query("abs(control_value - 0.6) > 1e-8").shape[0]),
        "task015_failure_mode": "; ".join(task015.main_failure_note.dropna().astype(str).unique())[:500],
        "restricted_failure_mode": failure_note[:500],
        "conditioning_interpretation": "broader formulation/conditioning problem; not H_a3-specific",
    }])
    summary.to_csv(OUT_DIR / "continuation_conditioning_summary.csv", index=False)

    verdict = {
        "seed_source": "TASK-011/TASK-012 equilibrium",
        "auto_coordinate": "restricted/scaled 3D: Z, U, M=log(m/m_seed), w=0",
        "wA0_python_expected_range_m_s": [float(py_summary.control_min.iloc[0]), float(py_summary.control_max.iloc[0])],
        "wA0_auto_covered_range_m_s": [float(branch.control_value.min()), float(branch.control_value.max())],
        "auto_accepted_nontrivial_branch": bool(len(nontrivial) > 0),
        "conditioning_verdict": "W_a0 restricted/scaled AUTO still accepts only the seed; H_a3 failures remain broader formulation/conditioning concerns rather than control-specific evidence.",
    }
    (OUT_DIR / "task017_conditioning_verdict.json").write_text(json.dumps(verdict, indent=2, sort_keys=True))
    write_note(summary, verdict)
    print(f"Wrote TASK-017 outputs to {OUT_DIR}")


if __name__ == "__main__":
    main()
