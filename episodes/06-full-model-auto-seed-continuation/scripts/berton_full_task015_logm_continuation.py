"""TASK-015 diagnostics for the log-mass full Berton AUTO formulation.

The AUTO run is launched from the companion notebook or with::

    bash episodes/06-full-model-auto-seed-continuation/auto/berton_full_task015/run_auto.sh

This script parses the saved AUTO files, translates the TASK-011 equilibrium
seed into ``(z, u, w, log(m/kg))`` coordinates, cross-checks transformed RHS
residuals/eigenvalues against the Python physical-state diagnostics, and writes
CSV summaries for the W_a0 first-step retry.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
EPISODE_ROOT = SCRIPT_DIR.parents[0]
REPO_ROOT = SCRIPT_DIR.parents[2]
AUTO_DIR = EPISODE_ROOT / "auto" / "berton_full_task015"
OUT_DIR = EPISODE_ROOT / "outputs" / "task015"
TASK011_OUT = REPO_ROOT / "episodes" / "05-full-model-oscillatory-orbit" / "outputs" / "task011"
TASK012_OUT = EPISODE_ROOT / "outputs" / "task012"
FORTRAN = AUTO_DIR / "bertonfull_logm.f90"

EP04_SCRIPTS = REPO_ROOT / "episodes" / "04-full-model-auto-equilibria" / "scripts"
if str(EP04_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(EP04_SCRIPTS))

from berton_full_auto_task009_validate import default_par, finite_difference_jacobian, python_rhs  # noqa: E402

TYPE_NAMES = {-9: "MX", -4: "UZ-", 0: "regular", 1: "BP", 2: "LP", 3: "HB", 4: "UZ/NPR", 9: "EP"}
RUNS = {
    "logm-wA0-plus": {"control": "W_a0", "file": "task015-logm-wA0-plus"},
    "logm-wA0-minus": {"control": "W_a0", "file": "task015-logm-wA0-minus"},
}


def transformed_rhs(v: np.ndarray, par: np.ndarray) -> np.ndarray:
    z, u, w, log_m = map(float, v)
    m = float(np.exp(log_m))
    f = python_rhs(np.array([z, u, w, m]), par)
    return np.array([f[0], f[1], f[2], f[3] / m])


def transformed_fd_jacobian(v: np.ndarray, par: np.ndarray) -> np.ndarray:
    steps = np.array([1.0, 1e-5, 1e-5, 1e-4])
    j = np.zeros((4, 4))
    for i, h in enumerate(steps):
        vp = v.copy(); vm = v.copy(); vp[i] += h; vm[i] -= h
        j[:, i] = (transformed_rhs(vp, par) - transformed_rhs(vm, par)) / (vp[i] - vm[i])
    return j


def compile_and_run_fortran(samples: list[np.ndarray]) -> np.ndarray:
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        driver = tdp / "logm_rhs_driver.f90"

        def dval(x: float) -> str:
            return f"{x:.17e}".replace("e", "D")

        rows = "\n".join(
            f"  y=(/ &\n    {dval(float(s[0]))}, {dval(float(s[1]))}, {dval(float(s[2]))}, {dval(float(s[3]))} /)\n"
            "  call rhs_full(y,par,f)\n"
            "  write(*,'(4ES25.16)') f"
            for s in samples
        )
        driver.write_text(
            "program logm_rhs_driver\n"
            "  use berton_full_model\n"
            "  implicit none\n"
            "  double precision :: par(95), y(4), f(4)\n"
            "  call init_defaults(par)\n"
            "  par(1)=9000D0; par(2)=0.6D0; par(4)=0.61D0; par(39)=0D0; par(43)=0D0\n"
            f"{rows}\n"
            "end program logm_rhs_driver\n"
        )
        exe = tdp / "logm_rhs_driver"
        subprocess.run(["gfortran", str(FORTRAN), str(driver), "-o", str(exe)], check=True, cwd=tdp)
        out = subprocess.check_output([str(exe)], text=True)
    return np.array([[float(x) for x in line.split()] for line in out.splitlines() if line.strip()])


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
                "H_a3": vals[3],
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
        if "NOTE:" in line or "DGEBAL" in line or "NaN" in line:
            notes.append({"run": run_name, "label": str(current_label or ""), "message": line.strip()})
    return pd.DataFrame(eig_rows), pd.DataFrame(notes)


def main(run_auto: bool = False) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if run_auto:
        subprocess.run(["bash", str(AUTO_DIR / "run_auto.sh")], cwd=REPO_ROOT, check=True)

    seed = pd.read_csv(TASK011_OUT / "continuation_equilibrium_seed.csv")
    seed_row = seed.iloc[0]
    par = default_par()
    par[0] = 9000.0; par[1] = 0.6; par[3] = 0.61; par[38] = 0.0; par[42] = 0.0
    v = np.array([seed_row.z_m, seed_row.u_m_s, seed_row.w_m_s, np.log(seed_row.m_kg)], dtype=float)
    y = np.array([seed_row.z_m, seed_row.u_m_s, seed_row.w_m_s, seed_row.m_kg], dtype=float)

    transformed_residual = transformed_rhs(v, par)
    physical_residual = python_rhs(y, par)
    transformed_eigs = np.linalg.eigvals(transformed_fd_jacobian(v, par))
    physical_eigs = np.linalg.eigvals(finite_difference_jacobian(y, par))
    fortran_rhs = compile_and_run_fortran([v])[0]

    pd.DataFrame(
        [
            {
                "z_m": v[0],
                "u_m_s": v[1],
                "w_m_s": v[2],
                "m_kg": y[3],
                "log_m_kg": v[3],
                "physical_rhs_norm": float(np.linalg.norm(physical_residual)),
                "transformed_rhs_norm": float(np.linalg.norm(transformed_residual)),
                "fortran_python_transformed_rhs_max_abs_diff": float(np.max(np.abs(fortran_rhs - transformed_residual))),
                "physical_eigs_match_transformed": bool(np.allclose(np.sort_complex(physical_eigs), np.sort_complex(transformed_eigs), rtol=5e-5, atol=1e-8)),
            }
        ]
    ).to_csv(OUT_DIR / "seed_logm_crosscheck.csv", index=False)
    pd.DataFrame(
        {
            "real_s_inv": transformed_eigs.real,
            "imag_s_inv": transformed_eigs.imag,
        }
    ).to_csv(OUT_DIR / "seed_logm_python_eigenvalues.csv", index=False)

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

    comparison_rows = []
    task012 = pd.read_csv(TASK012_OUT / "continuation_summary.csv")
    task012_w = task012[task012["control"] == "W_a0"]
    for run_name, group in auto_branch.groupby("run"):
        notes = auto_notes.loc[auto_notes.run == run_name, "message"].tolist()
        accepted = group[group.type != "MX"]
        comparison_rows.append(
            {
                "run": run_name,
                "control": group.control.iloc[0],
                "auto_points": len(group),
                "auto_accepted_non_mx_points": len(accepted),
                "control_min": group.control_value.min(),
                "control_max": group.control_value.max(),
                "types": ",".join(group.type.astype(str).unique()),
                "main_failure_note": next((n for n in notes if "No convergence" in n or "DGEBAL" in n or "Retrying" in n or "NaN" in n), ""),
                "task012_wA0_min_accepted_non_mx_points": int(task012_w["auto_accepted_non_mx_points"].min()),
                "task012_failure_reference": "; ".join(sorted(set(task012_w["main_failure_note"].dropna().astype(str))))[:500],
            }
        )
    pd.DataFrame(comparison_rows).to_csv(OUT_DIR / "continuation_summary.csv", index=False)

    verdict = {
        "coordinate": "log_m_kg = log(m/kg)",
        "seed_log_m_kg": float(v[3]),
        "first_step_control": "W_a0",
        "accepted_nontrivial_branch": bool((auto_branch[auto_branch.type != "MX"].groupby("run").size() > 1).any()),
        "residual_risk": "Log-mass removes the tiny raw mass coordinate, but W_a0 first-step continuation still diverges to NaN/DGEBAL failures before accepting a nontrivial point.",
    }
    (OUT_DIR / "task015_verdict.json").write_text(json.dumps(verdict, indent=2, sort_keys=True))
    print(f"Wrote TASK-015 outputs to {OUT_DIR}")


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run-auto", action="store_true", help="run AUTO before parsing diagnostics")
    args = ap.parse_args()
    main(run_auto=args.run_auto)
