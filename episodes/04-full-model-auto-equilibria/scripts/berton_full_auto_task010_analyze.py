"""TASK-010 analysis for full Berton AUTO equilibrium continuation.

This script parses the saved AUTO-07p output from this episode's ``auto/berton_full``,
catalogues detected special points, cross-checks branch eigenvalues with the
independent Python finite-difference Jacobian from the TASK-009 validation
harness, and writes a compact table/plot for the Berton z_W0 continuation.

Usage from repository root::

    uv run python episodes/04-full-model-auto-equilibria/scripts/berton_full_auto_task010_analyze.py --run-auto

Outputs are written under ``episodes/04-full-model-auto-equilibria/outputs/task010/``.
"""

from __future__ import annotations

import argparse
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import sys

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from berton_full_auto_task009_validate import AUTO_DIR, EPISODE_ROOT, REPO_ROOT, finite_difference_jacobian, python_rhs

B_FILE = AUTO_DIR / "b.bertfull-zW0"
S_FILE = AUTO_DIR / "s.bertfull-zW0"
D_FILE = AUTO_DIR / "d.bertfull-zW0"
OUT_DIR = EPISODE_ROOT / "outputs" / "task010"

PAR_NAMES = {
    1: "z_W0",
    2: "W_a0",
    3: "rad_mult",
    4: "H_a3",
    5: "eta_override",
    6: "drag_mult",
    7: "Delta_z_W",
    39: "eta_blend",
    40: "phi",
    41: "c_B",
    43: "include_coriolis",
    44: "reynolds_length_mode",
    60: "sigma_S",
    61: "R_zeta",
    62: "sigma_plus_Rzeta",
    63: "R",
    64: "rad_R",
    65: "driving_factor",
    66: "m_dot",
    67: "k",
    68: "Re",
    75: "S_i",
    77: "eta",
    79: "W_a",
    80: "U_a",
    81: "rho_a",
    91: "vertical_force_residual",
    92: "growth_balance_residual",
    93: "fall_speed_slope_proxy",
    94: "growth_mass_slope",
    95: "reduced_det_proxy",
}

TYPE_NAMES = {
    -4: "UZ-",
    0: "regular",
    1: "BP",
    2: "LP",
    3: "HB",
    4: "UZ/NPR",
    9: "EP",
}


@dataclass(frozen=True)
class AutoSolution:
    branch: int
    point: int
    ty: int
    label: int
    state: np.ndarray
    par: np.ndarray


def run_auto() -> None:
    subprocess.run(["bash", str(AUTO_DIR / "run_auto.sh")], cwd=REPO_ROOT, check=True)


def parse_b_file(path: Path = B_FILE) -> pd.DataFrame:
    rows: list[dict[str, float | int | str]] = []
    for line in path.read_text().splitlines():
        parts = line.split()
        if len(parts) != 12:
            continue
        try:
            br, pt, ty, lab = map(int, parts[:4])
            vals = list(map(float, parts[4:]))
        except ValueError:
            continue
        rows.append(
            {
                "branch": br,
                "point": pt,
                "ty": ty,
                "label": lab,
                "type": TYPE_NAMES.get(ty, f"TY={ty}"),
                "z_W0": vals[0],
                "l2_norm": vals[1],
                "sigma_S": vals[2],
                "R_zeta": vals[3],
                "sigma_plus_Rzeta": vals[4],
                "R": vals[5],
                "driving_factor": vals[6],
                "k": vals[7],
            }
        )
    if not rows:
        raise ValueError(f"No branch rows parsed from {path}")
    return pd.DataFrame(rows)


def parse_s_file(path: Path = S_FILE, npar: int = 95) -> dict[int, AutoSolution]:
    lines = path.read_text().splitlines()
    i = 0
    out: dict[int, AutoSolution] = {}
    while i < len(lines):
        parts = lines[i].split()
        if len(parts) < 4:
            i += 1
            continue
        try:
            ints = [int(x) for x in parts]
        except ValueError:
            i += 1
            continue
        # AUTO solution headers have many integer fields; first four are BR, PT, TY, LAB.
        if len(ints) < 12 or i + 5 >= len(lines):
            i += 1
            continue
        branch, point, ty, label = ints[:4]
        try:
            state = np.array([float(x) for x in lines[i + 1].split()[1:5]], dtype=float)
        except ValueError:
            i += 1
            continue
        vals: list[float] = []
        j = i + 5
        while j < len(lines) and len(vals) < npar:
            try:
                vals.extend(float(x) for x in lines[j].split())
            except ValueError:
                break
            j += 1
        if len(vals) >= npar and label > 0:
            out[label] = AutoSolution(branch, point, ty, label, state, np.array(vals[:npar], dtype=float))
            i = j
        else:
            i += 1
    if not out:
        raise ValueError(f"No labeled solutions parsed from {path}")
    return out


def parse_d_file(path: Path = D_FILE) -> dict[int, dict[str, object]]:
    out: dict[int, dict[str, object]] = {}
    current: int | None = None
    for line in path.read_text().splitlines():
        m = re.match(r"\s*\d+\s+(\d+)\s+Eigenvalues\s+:\s+Stable:\s+(\d+)", line)
        if m:
            current = int(m.group(1))
            out.setdefault(current, {"stable": int(m.group(2)), "eigenvalues": [], "messages": []})
            out[current]["stable"] = int(m.group(2))
            continue
        m = re.search(r"Eigenvalue\s+\d+:\s+([+-]?\d*\.\d+E[+-]?\d+)\s+([+-]?\d*\.\d+E[+-]?\d+)", line)
        if m and current is not None:
            eigs = out[current].setdefault("eigenvalues", [])
            if len(eigs) < 4:
                eigs.append(complex(float(m.group(1)), float(m.group(2))))
            continue
        if current is not None and any(token in line for token in ["BP", "LP", "HB"]):
            out[current].setdefault("messages", []).append(line.strip())
    return out


def critical_eigenvalue(eig: np.ndarray) -> complex:
    return eig[np.argmax(eig.real)]


def branch_rows_with_cross_checks() -> tuple[pd.DataFrame, pd.DataFrame]:
    bdf = parse_b_file()
    solutions = parse_s_file()
    ddata = parse_d_file()
    rows: list[dict[str, object]] = []
    for label, sol in sorted(solutions.items()):
        par = sol.par.copy()
        auto_eigs = np.array(ddata.get(label, {}).get("eigenvalues", []), dtype=complex)
        stable = ddata.get(label, {}).get("stable", np.nan)
        J = finite_difference_jacobian(sol.state, par)
        py_eigs = np.linalg.eigvals(J)
        ce_auto = critical_eigenvalue(auto_eigs) if auto_eigs.size else np.nan + 0j
        ce_py = critical_eigenvalue(py_eigs)
        residual = python_rhs(sol.state, par)
        row: dict[str, object] = {
            "label": label,
            "point": sol.point,
            "ty": sol.ty,
            "type": TYPE_NAMES.get(sol.ty, f"TY={sol.ty}"),
            "z_W0": par[0],
            "z": sol.state[0],
            "u": sol.state[1],
            "w": sol.state[2],
            "m": sol.state[3],
            "stable_count_auto": stable,
            "critical_real_auto": float(np.real(ce_auto)),
            "critical_imag_auto": float(np.imag(ce_auto)),
            "critical_real_python": float(np.real(ce_py)),
            "critical_imag_python": float(np.imag(ce_py)),
            "max_abs_eig_diff_sorted": float(np.max(np.abs(np.sort_complex(auto_eigs) - np.sort_complex(py_eigs)))) if auto_eigs.size == py_eigs.size else np.nan,
            "residual_norm_python": float(np.linalg.norm(residual)),
        }
        for idx, name in PAR_NAMES.items():
            row[name] = float(par[idx - 1])
        rows.append(row)
    sdf = pd.DataFrame(rows)
    return bdf, sdf


def dataframe_to_markdown(df: pd.DataFrame, floatfmt: str = ".6g") -> str:
    headers = [str(c) for c in df.columns]
    rows: list[list[str]] = []
    for _, row in df.iterrows():
        vals: list[str] = []
        for value in row:
            if isinstance(value, (float, np.floating)):
                vals.append(format(float(value), floatfmt))
            else:
                vals.append(str(value))
        rows.append(vals)
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    lines.extend("| " + " | ".join(vals) + " |" for vals in rows)
    return "\n".join(lines) + "\n"


def catalogue_special_points(bdf: pd.DataFrame, sdf: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for code, name in [(2, "LP"), (3, "HB"), (1, "BP")]:
        hits = bdf[bdf["ty"] == code]
        if hits.empty:
            rows.append({"kind": name, "status": "not detected", "count": 0, "labels": "", "z_W0_values": ""})
        else:
            rows.append(
                {
                    "kind": name,
                    "status": "detected",
                    "count": len(hits),
                    "labels": ",".join(str(int(x)) for x in hits["label"] if int(x) > 0),
                    "z_W0_values": ",".join(f"{x:.6g}" for x in hits["z_W0"]),
                }
            )
    # User and endpoint labels are not bifurcations, but are useful anchors.
    anchors = sdf[sdf["type"].isin(["UZ-", "UZ/NPR", "EP"])]
    rows.append(
        {
            "kind": "UZ/EP anchors",
            "status": "catalogued",
            "count": len(anchors),
            "labels": ",".join(str(int(x)) for x in anchors["label"]),
            "z_W0_values": ",".join(f"{x:.6g}" for x in anchors["z_W0"]),
        }
    )
    return pd.DataFrame(rows)


def write_outputs(run: bool = False) -> None:
    if run:
        run_auto()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    bdf, sdf = branch_rows_with_cross_checks()
    specials = catalogue_special_points(bdf, sdf)

    # A compact subset that directly addresses the TASK-010 summary criterion.
    interesting = sdf[(sdf["z_W0"].between(8499.0, 10001.0)) | (sdf["type"] == "EP")].copy()
    cols = [
        "label", "type", "z_W0", "z", "u", "w", "m", "stable_count_auto",
        "critical_real_auto", "critical_imag_auto", "critical_real_python", "critical_imag_python",
        "sigma_S", "R_zeta", "sigma_plus_Rzeta", "R", "driving_factor", "k",
        "max_abs_eig_diff_sorted", "residual_norm_python",
    ]
    bdf.to_csv(OUT_DIR / "branch_points.csv", index=False)
    sdf.to_csv(OUT_DIR / "labeled_solution_cross_checks.csv", index=False)
    specials.to_csv(OUT_DIR / "special_points.csv", index=False)
    interesting[cols].to_csv(OUT_DIR / "summary_table.csv", index=False)
    (OUT_DIR / "summary_table.md").write_text(dataframe_to_markdown(interesting[cols], floatfmt=".6g"))
    (OUT_DIR / "special_points.md").write_text(dataframe_to_markdown(specials))

    fig, axes = plt.subplots(3, 1, figsize=(7.5, 8.5), sharex=True)
    axes[0].plot(bdf["z_W0"] / 1000.0, bdf["l2_norm"] / 1000.0, "k.-", ms=3)
    axes[0].set_ylabel("AUTO L2 norm / km")
    axes[0].set_title("Full Berton equilibrium continuation in z_W0")
    axes[1].plot(sdf["z_W0"] / 1000.0, sdf["critical_real_auto"], "o-", label="AUTO")
    axes[1].plot(sdf["z_W0"] / 1000.0, sdf["critical_real_python"], "x", label="Python FD")
    axes[1].axhline(0.0, color="0.6", lw=0.8)
    axes[1].set_ylabel("max Re(eigenvalue) [s$^{-1}$]")
    axes[1].legend()
    axes[2].plot(bdf["z_W0"] / 1000.0, bdf["sigma_plus_Rzeta"], ".-", label="sigma_S + R_zeta")
    axes[2].plot(bdf["z_W0"] / 1000.0, bdf["driving_factor"], ".-", label="growth balance")
    axes[2].axhline(0.0, color="0.6", lw=0.8)
    axes[2].set_xlabel("z_W0 [km]")
    axes[2].set_ylabel("mechanism diagnostics")
    axes[2].legend()
    for ax in axes:
        ax.grid(True, alpha=0.25)
        ax.invert_xaxis()
    fig.tight_layout()
    fig.savefig(OUT_DIR / "branch_summary.png", dpi=180)
    plt.close(fig)

    print(f"Wrote {OUT_DIR}")
    print(specials.to_string(index=False))
    print(interesting[cols].to_string(index=False))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run-auto", action="store_true", help="rerun AUTO before parsing outputs")
    args = ap.parse_args()
    write_outputs(run=args.run_auto)


if __name__ == "__main__":
    main()
