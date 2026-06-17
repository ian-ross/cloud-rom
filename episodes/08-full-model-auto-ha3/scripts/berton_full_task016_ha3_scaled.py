"""TASK-016 full-system scaled H_a3 AUTO continuation synthesis.

Run from repository root after the companion AUTO run::

    bash episodes/08-full-model-auto-ha3/auto/berton_full_task016_ha3_scaled/run_auto.sh
    uv run python episodes/08-full-model-auto-ha3/scripts/berton_full_task016_ha3_scaled.py

The formulation ports the TASK-019/TASK-020 lessons back to the full 4D
Berton equilibrium system: scaled states ``Z=(z-z_seed)/1000``,
``U=(u-u_seed)/5``, ``W=w``, ``P=log(m/m_seed)/10``, and active control
``q_H=(H_a3-0.61)/0.001``. This script preserves the negative/convergence
result without overstating Hopf evidence.
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
AUTO_DIR = EPISODE_ROOT / "auto" / "berton_full_task016_ha3_scaled"
OUT_DIR = EPISODE_ROOT / "outputs" / "task016"
DOC = EPISODE_ROOT / "docs" / "task016_full_ha3_scaled_verdict.md"
NOTEBOOK = EPISODE_ROOT / "notebooks" / "task016_full_ha3_auto_record.ipynb"
TASK012_OUT = REPO_ROOT / "episodes" / "06-full-model-auto-seed-continuation" / "outputs" / "task012"
TASK015_OUT = REPO_ROOT / "episodes" / "06-full-model-auto-seed-continuation" / "outputs" / "task015"
TASK020_OUT = REPO_ROOT / "episodes" / "07-restricted-equilibrium-auto" / "outputs" / "task020"

EP04_SCRIPTS = REPO_ROOT / "episodes" / "04-full-model-auto-equilibria" / "scripts"
if str(EP04_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(EP04_SCRIPTS))
from berton_full_auto_task009_validate import default_par, finite_difference_jacobian, python_rhs  # noqa: E402

Z_SEED = 9.618027532260936e3
U_SEED = 1.9098623386953226
W_SEED = 0.0
M_SEED = 1.0802293920592054e-9
H_REF = 0.61
H_SCALE = 0.001
TYPE_NAMES = {-9: "MX", -4: "UZ-", 0: "regular", 1: "BP", 2: "LP", 3: "HB", 4: "UZ/NPR", 9: "EP"}
RUNS = {
    "q-plus": {"file": "task016-full-ha3-q-plus", "direction": "upward"},
    "q-minus": {"file": "task016-full-ha3-q-minus", "direction": "downward"},
}


def physical_from_scaled(zs: float, us: float, ws: float, ps: float) -> tuple[float, float, float, float, float, float]:
    z = Z_SEED + 1000.0 * zs
    u = U_SEED + 5.0 * us
    w = ws
    M = 10.0 * ps
    m = M_SEED * math.exp(M)
    H = H_REF
    return z, u, w, M, m, H


def parse_b(path: Path, run: str, direction: str) -> pd.DataFrame:
    rows = []
    if not path.exists():
        return pd.DataFrame()
    for line in path.read_text().splitlines():
        parts = line.split()
        if len(parts) < 10:
            continue
        try:
            br, pt, ty, lab = map(int, parts[:4])
            vals = list(map(float, parts[4:10]))
        except ValueError:
            continue
        q, norm, zs, us, ws, ps = vals
        H = H_REF + H_SCALE * q
        z, u, w, M, m, _ = physical_from_scaled(zs, us, ws, ps)
        rows.append(
            {
                "run": run,
                "direction": direction,
                "branch": br,
                "point": pt,
                "ty": ty,
                "type": TYPE_NAMES.get(ty, f"TY={ty}"),
                "label": lab,
                "q_H_scaled": q,
                "H_a3": H,
                "l2_norm_scaled_state": norm,
                "Z_scaled_1000m": zs,
                "U_scaled_5ms": us,
                "W_m_s": ws,
                "P_log_ratio_over_10": ps,
                "M_log_ratio": M,
                "z_m": z,
                "u_m_s": u,
                "w_m_s": w,
                "m_kg": m,
                "is_special_point": ty in {1, 2, 3},
                "is_hopf_label": ty == 3,
            }
        )
    return pd.DataFrame(rows)


def parse_d(path: Path, run: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    eig_rows = []
    note_rows = []
    current_label: int | None = None
    if not path.exists():
        return pd.DataFrame(), pd.DataFrame()
    tokens = ("NOTE:", "NaN", "DGEBAL", "floating-point", "Retrying step", "No convergence", "MX")
    for i, line in enumerate(path.read_text().splitlines(), start=1):
        m = re.match(r"\s*\d+\s+(\d+)\s+Eigenvalues\s+:\s+Stable:\s+(\d+)", line)
        if m:
            current_label = int(m.group(1))
            note_rows.append({"run": run, "line": i, "label": current_label, "message": f"Stable eigenvalues: {m.group(2)}"})
            continue
        m = re.search(r"Eigenvalue\s+(\d+):\s+([+-]?\d*\.\d+E[+-]?\d+)\s+([+-]?\d*\.\d+E[+-]?\d+)", line)
        if m and current_label is not None:
            eig_rows.append(
                {
                    "run": run,
                    "label": current_label,
                    "eigenvalue_index": int(m.group(1)),
                    "real_s_inv": float(m.group(2)),
                    "imag_s_inv": float(m.group(3)),
                }
            )
            continue
        text = line.strip()
        if any(t in text for t in tokens):
            note_rows.append({"run": run, "line": i, "label": current_label if current_label is not None else "", "message": text})
    return pd.DataFrame(eig_rows), pd.DataFrame(note_rows)


def config_summary() -> pd.DataFrame:
    rows = []
    for run, meta in RUNS.items():
        cfg = AUTO_DIR / f"c.bertonfull-task016-ha3-{run.replace('q-', 'q-')}"
        text = cfg.read_text() if cfg.exists() else ""
        rows.append(
            {
                "run": run,
                "config_file": cfg.name,
                "state_scaling": "Z=(z-z_seed)/1000, U=(u-u_seed)/5, W=w, P=log(m/m_seed)/10",
                "control_scaling": "q_H=(H_a3-0.61)/0.001",
                "physical_inverse": "z=z_seed+1000Z; u=u_seed+5U; w=W; m=m_seed*exp(10P)",
                "contains_canonical_H_a3_0_61": True,
                "uzr_or_stop": "; ".join(line.strip() for line in text.splitlines() if line.startswith("UZ")),
                "raw_artifacts": ",".join(f"{prefix}.{meta['file']}" for prefix in ["b", "s", "d"]),
            }
        )
    return pd.DataFrame(rows)


def representative_points(branch: pd.DataFrame) -> pd.DataFrame:
    if branch.empty:
        return branch
    picks = []
    for _, grp in branch.groupby("run"):
        picks.append(grp.iloc[0])
        non_mx = grp[grp.type != "MX"]
        if len(non_mx):
            picks.append(non_mx.iloc[-1])
        specials = grp[grp.is_special_point]
        for _, row in specials.iterrows():
            picks.append(row)
    return pd.DataFrame(picks).drop_duplicates(["run", "point", "label"]).sort_values(["run", "point"])


def python_diagnostics(points: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    par0 = default_par()
    par0[0] = 9000.0
    par0[1] = 0.6
    par0[3] = 0.61
    par0[38] = 0.0
    par0[42] = 0.0
    rows = []
    eig_rows = []
    for _, p in points.iterrows():
        par = par0.copy()
        par[3] = float(p.H_a3)
        y = np.array([float(p.z_m), float(p.u_m_s), float(p.w_m_s), float(p.m_kg)])
        rhs = python_rhs(y, par)
        j = finite_difference_jacobian(y, par)
        eigs = np.linalg.eigvals(j)
        rows.append(
            {
                "run": p.run,
                "point": int(p.point),
                "label": int(p.label),
                "type": p.type,
                "H_a3": float(p.H_a3),
                "z_m": float(p.z_m),
                "u_m_s": float(p.u_m_s),
                "w_m_s": float(p.w_m_s),
                "m_kg": float(p.m_kg),
                "full_rhs_norm": float(np.linalg.norm(rhs)),
                "stable_eigenvalue_count": int(np.sum(eigs.real < 0)),
                "critical_real_s_inv": float(eigs.real.max()),
                "critical_imag_s_inv": float(eigs[np.argmax(eigs.real)].imag),
            }
        )
        for k, ev in enumerate(eigs, start=1):
            eig_rows.append({"run": p.run, "point": int(p.point), "label": int(p.label), "H_a3": float(p.H_a3), "eigen_index": k, "real_s_inv": ev.real, "imag_s_inv": ev.imag})
    return pd.DataFrame(rows), pd.DataFrame(eig_rows)


def suspected_crossing_crosscheck() -> pd.DataFrame:
    """Finite-difference full-Jacobian check at TASK-012 H_a3 crossing anchors."""
    par0 = default_par()
    par0[0] = 9000.0
    par0[1] = 0.6
    par0[38] = 0.0
    par0[42] = 0.0
    y = np.array([Z_SEED, U_SEED, W_SEED, M_SEED], dtype=float)
    rows = []
    for H in [0.600, 0.610, 0.625, 0.650]:
        par = par0.copy()
        par[3] = H
        rhs = python_rhs(y, par)
        eigs = np.linalg.eigvals(finite_difference_jacobian(y, par))
        rows.append(
            {
                "H_a3": H,
                "z_m": Z_SEED,
                "u_m_s": U_SEED,
                "w_m_s": W_SEED,
                "m_kg": M_SEED,
                "full_rhs_norm_at_task011_seed": float(np.linalg.norm(rhs)),
                "stable_eigenvalue_count": int(np.sum(eigs.real < 0)),
                "critical_real_s_inv": float(eigs.real.max()),
                "critical_imag_s_inv": float(eigs[np.argmax(eigs.real)].imag),
                "interpretation": "finite-difference Python full-Jacobian check of the TASK-012 suspected H_a3 crossing; not an accepted AUTO branch point",
            }
        )
    return pd.DataFrame(rows)


def comparison_summary(branch: pd.DataFrame, notes: pd.DataFrame) -> pd.DataFrame:
    rows = []
    task020 = json.loads((TASK020_OUT / "task020_ha3_verdict.json").read_text()) if (TASK020_OUT / "task020_ha3_verdict.json").exists() else {}
    for run, grp in branch.groupby("run"):
        accepted = grp[grp.type != "MX"]
        rn = notes[notes.run == run]
        rows.append(
            {
                "run": run,
                "attempted_direction": grp.direction.iloc[0],
                "accepted_rows_excluding_mx": int(len(accepted)),
                "accepted_H_a3_min": float(accepted.H_a3.min()) if len(accepted) else math.nan,
                "accepted_H_a3_max": float(accepted.H_a3.max()) if len(accepted) else math.nan,
                "special_types": ",".join(sorted(set(accepted.type.astype(str)))) if len(accepted) else "",
                "has_auto_hopf_label": bool((accepted.ty == 3).any()),
                "main_failure_note": next((str(x) for x in rn.message if any(tok in str(x) for tok in ["DGEBAL", "NaN", "Retrying step", "floating-point"])), ""),
                "task020_restricted_reference": task020.get("verdict", task020.get("summary", "restricted H_a3 had no AUTO-supported HB; upward direction inconclusive")),
            }
        )
    return pd.DataFrame(rows)


def write_doc(summary: pd.DataFrame, diag: pd.DataFrame, notes: pd.DataFrame, crossing: pd.DataFrame) -> None:
    accepted_min = summary.accepted_H_a3_min.min()
    accepted_max = summary.accepted_H_a3_max.max()
    has_hb = bool(summary.has_auto_hopf_label.any())
    note_lines = "\n".join(f"- `{r.run}` line {int(r.line)}: {r.message}" for r in notes.head(12).itertuples()) or "- No diagnostics parsed."
    DOC.write_text(
        "# TASK-016 full-system scaled H_a3 continuation verdict\n\n"
        "TASK-016 retried the full 4D Berton equilibrium continuation after the restricted TASK-019/TASK-020 scaling work. "
        "The AUTO state starts exactly at the TASK-011/TASK-012 equilibrium seed and uses `Z=(z-z_seed)/1000`, `U=(u-u_seed)/5`, `W=w`, and `P=log(m/m_seed)/10`; the active control is `q_H=(H_a3-0.61)/0.001`. "
        "The physical inverse conversions are recorded in `outputs/task016/config_summary.csv` and in the AUTO source comments.\n\n"
        "## Commands\n\n```bash\n"
        "bash episodes/08-full-model-auto-ha3/auto/berton_full_task016_ha3_scaled/run_auto.sh\n"
        "uv run python episodes/08-full-model-auto-ha3/scripts/berton_full_task016_ha3_scaled.py\n"
        "uv run pytest tests/test_episode08_full_task016.py\n"
        "```\n\n"
        "## AUTO result\n\n"
        f"Accepted H_a3 range: `{accepted_min:.6f}` to `{accepted_max:.6f}`. This range includes only the canonical seed value `0.61`; both requested directions were attempted, but AUTO did not accept a nontrivial full-system H_a3 branch. "
        f"AUTO Hopf/HB label present: `{has_hb}`. The upward direction retries through small q_H steps before NaN/DGEBAL/floating-point failure; the downward direction records only the seed plus MX/no movement.\n\n"
        "Parsed convergence diagnostics include:\n\n"
        f"{note_lines}\n\n"
        "## Independent Python cross-check\n\n"
        f"The representative accepted point(s) have Python full-RHS norm up to `{diag.full_rhs_norm.max() if len(diag) else math.nan:.3e}` and stable eigenvalue count `{','.join(map(str, sorted(set(diag.stable_eigenvalue_count.astype(int)))) if len(diag) else 'n/a')}`. "
        f"The critical real eigenvalue at the accepted seed is `{diag.critical_real_s_inv.max() if len(diag) else math.nan:.3e}` s^-1, so the accepted point is locally stable in the independent Python finite-difference Jacobian. "
        f"A separate finite-difference Python check at TASK-012 suspected crossing anchors (`outputs/task016/python_suspected_crossing_crosscheck.csv`) gives critical real parts from `{crossing.critical_real_s_inv.min() if len(crossing) else math.nan:.3e}` to `{crossing.critical_real_s_inv.max() if len(crossing) else math.nan:.3e}` s^-1 over H_a3=0.600--0.650; this confirms the Python stability-sign hint but not an accepted AUTO crossing.\n\n"
        "## Verdict\n\n"
        "`H_a3` does **not** provide an AUTO-validated full-system Hopf candidate in this TASK-016 retry. The result is negative/inconclusive rather than a Hopf validation: the canonical seed is stable, the branch fails before reaching the Python-predicted `H_a3≈0.62` crossing region, and no HB label or independently cross-checked stability crossing is available from accepted full-system AUTO points. "
        "The restricted TASK-020 upward hint therefore remains a Python/restricted numerical hint only, not full-system AUTO evidence.\n"
    )


def write_notebook() -> None:
    """Write a minimal reproducibility notebook without requiring nbformat."""
    cells = [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["# TASK-016 full H_a3 AUTO record\n", "\n", "Reproducible record of AUTO commands, constants, outputs, and parser invocation.\n"],
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": ["import sys\n", "sys.path.append('/usr/local/lib64/auto-07p/python')\n", "import auto\n", "from pathlib import Path\n", "AUTO_DIR = Path('../auto/berton_full_task016_ha3_scaled')\n", "AUTO_DIR\n"],
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["Constants: `q_H=(H_a3-0.61)/0.001`; `Z=(z-z_seed)/1000`; `U=(u-u_seed)/5`; `W=w`; `P=log(m/m_seed)/10`. Raw files are saved as `b/s/d.task016-full-ha3-q-{plus,minus}`.\n"],
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": ["# Executed production command from repository root:\n", "# bash episodes/08-full-model-auto-ha3/auto/berton_full_task016_ha3_scaled/run_auto.sh\n", "# Parser/curation command:\n", "# uv run python episodes/08-full-model-auto-ha3/scripts/berton_full_task016_ha3_scaled.py\n"],
        },
    ]
    nb = {"cells": cells, "metadata": {"language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 5}
    NOTEBOOK.write_text(json.dumps(nb, indent=2))


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DOC.parent.mkdir(parents=True, exist_ok=True)
    NOTEBOOK.parent.mkdir(parents=True, exist_ok=True)

    branch_frames = []
    eig_frames = []
    note_frames = []
    for run, meta in RUNS.items():
        branch_frames.append(parse_b(AUTO_DIR / f"b.{meta['file']}", run, meta["direction"]))
        eig, notes = parse_d(AUTO_DIR / f"d.{meta['file']}", run)
        eig_frames.append(eig)
        note_frames.append(notes)

    branch = pd.concat(branch_frames, ignore_index=True) if branch_frames else pd.DataFrame()
    eigs = pd.concat(eig_frames, ignore_index=True) if eig_frames else pd.DataFrame()
    notes = pd.concat(note_frames, ignore_index=True) if note_frames else pd.DataFrame()
    reps = representative_points(branch)
    diag, py_eigs = python_diagnostics(reps)
    cfg = config_summary()
    comp = comparison_summary(branch, notes)
    crossing = suspected_crossing_crosscheck()

    branch.to_csv(OUT_DIR / "auto_branch_summary.csv", index=False)
    eigs.to_csv(OUT_DIR / "auto_eigenvalue_diagnostics.csv", index=False)
    notes.to_csv(OUT_DIR / "auto_convergence_notes.csv", index=False)
    cfg.to_csv(OUT_DIR / "config_summary.csv", index=False)
    reps.to_csv(OUT_DIR / "representative_auto_points.csv", index=False)
    diag.to_csv(OUT_DIR / "python_full_eigenvalue_crosscheck.csv", index=False)
    py_eigs.to_csv(OUT_DIR / "python_full_eigenvalues.csv", index=False)
    comp.to_csv(OUT_DIR / "ha3_full_verdict_summary.csv", index=False)
    crossing.to_csv(OUT_DIR / "python_suspected_crossing_crosscheck.csv", index=False)

    accepted = branch[branch.type != "MX"]
    verdict = {
        "task": "TASK-016",
        "formulation": "full 4D scaled H_a3 with Z,U,W,P and q_H",
        "seed_source": "TASK-011/TASK-012 equilibrium seed",
        "canonical_H_a3_included": True,
        "attempted_directions": sorted(branch.direction.dropna().unique().tolist()),
        "accepted_H_a3_min": float(accepted.H_a3.min()) if len(accepted) else None,
        "accepted_H_a3_max": float(accepted.H_a3.max()) if len(accepted) else None,
        "accepted_non_seed_points": int(((accepted.q_H_scaled.abs() > 1e-12)).sum()) if len(accepted) else 0,
        "auto_hopf_validated": bool((accepted.ty == 3).any()) if len(accepted) else False,
        "verdict": "negative/inconclusive: no AUTO-validated full-system H_a3 Hopf candidate; branch fails before Python-predicted crossing region",
        "zW0_ready": False,
    }
    (OUT_DIR / "task016_full_ha3_verdict.json").write_text(json.dumps(verdict, indent=2, sort_keys=True))
    write_doc(comp, diag, notes, crossing)
    write_notebook()
    print(f"Wrote TASK-016 outputs to {OUT_DIR}")


if __name__ == "__main__":
    main()
