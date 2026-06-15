"""TASK-012 analysis for full Berton continuation from the TASK-011 seed.

The AUTO run itself is launched from the accompanying notebook (or with
``bash episodes/06-full-model-auto-seed-continuation/auto/berton_full_task012/run_auto.sh``).
This script parses the saved AUTO diagnostics and adds an independent Python
root-continuation sensitivity probe for the same equilibrium controls.

Usage from repository root::

    uv run python episodes/06-full-model-auto-seed-continuation/scripts/berton_full_task012_seed_continuation.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import root

SCRIPT_DIR = Path(__file__).resolve().parent
EPISODE_ROOT = SCRIPT_DIR.parents[0]
REPO_ROOT = SCRIPT_DIR.parents[2]
AUTO_DIR = EPISODE_ROOT / "auto" / "berton_full_task012"
OUT_DIR = EPISODE_ROOT / "outputs" / "task012"
TASK011_OUT = REPO_ROOT / "episodes" / "05-full-model-oscillatory-orbit" / "outputs" / "task011"

EP04_SCRIPTS = REPO_ROOT / "episodes" / "04-full-model-auto-equilibria" / "scripts"
if str(EP04_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(EP04_SCRIPTS))

from berton_full_auto_task009_validate import default_par, finite_difference_jacobian, python_rhs  # noqa: E402

TYPE_NAMES = {-9: "MX", -4: "UZ-", 0: "regular", 1: "BP", 2: "LP", 3: "HB", 4: "UZ/NPR", 9: "EP"}
RUNS = {
    "wA0-plus": {"control": "W_a0", "file": "task012-wA0-plus", "control_index": 1},
    "wA0-minus": {"control": "W_a0", "file": "task012-wA0-minus", "control_index": 1},
    "Ha3-plus": {"control": "H_a3", "file": "task012-Ha3-plus", "control_index": 3},
    "Ha3-minus": {"control": "H_a3", "file": "task012-Ha3-minus", "control_index": 3},
}


def read_task011_seed() -> tuple[pd.DataFrame, dict]:
    seed = pd.read_csv(TASK011_OUT / "continuation_equilibrium_seed.csv")
    verdict = json.loads((TASK011_OUT / "classification_verdict.json").read_text())
    return seed, verdict


def parse_b(path: Path, run_name: str, control: str) -> pd.DataFrame:
    rows: list[dict[str, float | int | str]] = []
    for line in path.read_text().splitlines():
        parts = line.split()
        if len(parts) < 12:
            continue
        try:
            br, pt, ty, lab = map(int, parts[:4])
            vals = list(map(float, parts[4:]))
        except ValueError:
            continue
        rows.append(
            {
                "run": run_name,
                "branch": br,
                "point": pt,
                "ty": ty,
                "type": TYPE_NAMES.get(ty, f"TY={ty}"),
                "label": lab,
                "control": control,
                "control_value": vals[0],
                "l2_norm": vals[1],
                "z_W0": vals[2],
                "other_control": vals[3],
                "sigma_S": vals[4],
                "R_zeta": vals[5],
                "sigma_plus_Rzeta": vals[6],
                "R": vals[7],
            }
        )
    return pd.DataFrame(rows)


def parse_diagnostics(path: Path, run_name: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    eig_rows: list[dict[str, float | int | str]] = []
    notes: list[dict[str, str]] = []
    current_label: int | None = None
    for line in path.read_text().splitlines():
        m = re.match(r"\s*\d+\s+(\d+)\s+Eigenvalues\s+:\s+Stable:\s+(\d+)", line)
        if m:
            current_label = int(m.group(1))
            notes.append({"run": run_name, "label": str(current_label), "message": f"Stable eigenvalues: {m.group(2)}"})
            continue
        m = re.search(r"Eigenvalue\s+(\d+):\s+([+-]?\d*\.\d+E[+-]?\d+)\s+([+-]?\d*\.\d+E[+-]?\d+)", line)
        if m and current_label is not None:
            eig_rows.append(
                {
                    "run": run_name,
                    "label": current_label,
                    "eigenvalue_index": int(m.group(1)),
                    "real_s_inv": float(m.group(2)),
                    "imag_s_inv": float(m.group(3)),
                }
            )
            continue
        if "NOTE:" in line:
            notes.append({"run": run_name, "label": str(current_label or ""), "message": line.strip()})
    return pd.DataFrame(eig_rows), pd.DataFrame(notes)


def equilibrium_residual(vars3: np.ndarray, par: np.ndarray) -> np.ndarray:
    z, u, log_m = vars3
    m = float(np.exp(log_m))
    f = python_rhs(np.array([z, u, 0.0, m]), par)
    return np.array([f[1], f[2], f[3]])


def branch_probe(control: str, values: np.ndarray, seed_row: pd.Series) -> pd.DataFrame:
    par = default_par()
    par[0] = 9000.0
    par[1] = 0.6
    par[3] = 0.61
    x = np.array([seed_row.z_m, seed_row.u_m_s, np.log(seed_row.m_kg)], dtype=float)
    rows: list[dict[str, float | str | bool]] = []
    for val in values:
        if control == "W_a0":
            par[1] = float(val)
        elif control == "H_a3":
            par[3] = float(val)
        else:
            raise ValueError(control)
        sol = root(lambda v: equilibrium_residual(v, par), x, method="hybr", tol=1e-11)
        candidate = sol.x if (sol.success or np.linalg.norm(equilibrium_residual(sol.x, par)) < 1e-10) else x
        if sol.success or np.linalg.norm(equilibrium_residual(sol.x, par)) < 1e-10:
            x = sol.x
        z, u, log_m = candidate
        m = float(np.exp(log_m))
        y = np.array([z, u, 0.0, m])
        rhs = python_rhs(y, par)
        accepted = bool(sol.success or np.linalg.norm(rhs) < 1e-10)
        eig = np.linalg.eigvals(finite_difference_jacobian(y, par))
        crit = eig[np.argmax(eig.real)]
        rows.append(
            {
                "control": control,
                "control_value": float(val),
                "success": accepted,
                "message": sol.message,
                "z_m": z,
                "u_m_s": u,
                "w_m_s": 0.0,
                "m_kg": m,
                "rhs_norm": float(np.linalg.norm(rhs)),
                "critical_real_s_inv": float(crit.real),
                "critical_imag_s_inv": float(crit.imag),
                "stable_eigenvalue_count": int(np.sum(eig.real < 0.0)),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    seed, verdict = read_task011_seed()
    seed.to_csv(OUT_DIR / "task011_seed_review.csv", index=False)
    (OUT_DIR / "task011_verdict_review.json").write_text(json.dumps(verdict, indent=2, sort_keys=True))

    branch_frames = []
    eig_frames = []
    note_frames = []
    for run_name, meta in RUNS.items():
        branch_frames.append(parse_b(AUTO_DIR / f"b.{meta['file']}", run_name, meta["control"]))
        eig, notes = parse_diagnostics(AUTO_DIR / f"d.{meta['file']}", run_name)
        eig_frames.append(eig)
        note_frames.append(notes)
    auto_branch = pd.concat(branch_frames, ignore_index=True)
    auto_eigs = pd.concat(eig_frames, ignore_index=True)
    auto_notes = pd.concat(note_frames, ignore_index=True)
    auto_branch.to_csv(OUT_DIR / "auto_branch_summary.csv", index=False)
    auto_eigs.to_csv(OUT_DIR / "auto_eigenvalue_diagnostics.csv", index=False)
    auto_notes.to_csv(OUT_DIR / "auto_convergence_notes.csv", index=False)

    seed_row = seed.iloc[0]
    w_vals = np.r_[np.linspace(0.1, 0.6, 11), np.linspace(0.65, 1.2, 12)]
    h_vals = np.r_[np.linspace(0.4, 0.6, 9), np.linspace(0.625, 0.85, 10)]
    probe = pd.concat(
        [branch_probe("W_a0", w_vals, seed_row), branch_probe("H_a3", h_vals, seed_row)],
        ignore_index=True,
    )
    probe.to_csv(OUT_DIR / "python_equilibrium_control_probe.csv", index=False)

    summary = []
    for run_name, group in auto_branch.groupby("run"):
        notes = auto_notes.loc[auto_notes.run == run_name, "message"].tolist()
        accepted = group[group.type != "MX"]
        summary.append(
            {
                "run": run_name,
                "control": group.control.iloc[0],
                "auto_points": len(group),
                "auto_accepted_non_mx_points": len(accepted),
                "control_min": group.control_value.min(),
                "control_max": group.control_value.max(),
                "types": ",".join(group.type.astype(str).unique()),
                "main_failure_note": next((n for n in notes if "No convergence" in n or "DGEBAL" in n or "Retrying" in n), ""),
            }
        )
    pd.DataFrame(summary).to_csv(OUT_DIR / "continuation_summary.csv", index=False)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4), constrained_layout=True)
    for control, ax in zip(["W_a0", "H_a3"], axes):
        g = probe[probe.control == control]
        ax.plot(g.control_value, g.z_m, marker="o", label="equilibrium z")
        ax.set_xlabel(control)
        ax.set_ylabel("z_eq [m]")
        ax.grid(True, alpha=0.3)
        ax2 = ax.twinx()
        ax2.plot(g.control_value, g.critical_real_s_inv, color="tab:red", marker="x", label="critical Re(lambda)")
        ax2.axhline(0.0, color="tab:red", lw=0.8, alpha=0.5)
        ax2.set_ylabel("critical Re(lambda) [s$^{-1}$]", color="tab:red")
    fig.savefig(OUT_DIR / "python_equilibrium_control_probe.png", dpi=180)
    plt.close(fig)

    print(f"Wrote TASK-012 outputs to {OUT_DIR}")


if __name__ == "__main__":
    main()
