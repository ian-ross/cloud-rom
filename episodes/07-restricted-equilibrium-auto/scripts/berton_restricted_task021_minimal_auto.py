"""TASK-021 minimal AUTO W_a0 diagnostic synthesis.

Run from the repository root after the AUTO notebook/script run::

    uv run python episodes/07-restricted-equilibrium-auto/scripts/berton_restricted_task021_minimal_auto.py

The script parses the stripped restricted/scaled AUTO continuation with only
``W_a0`` in ``ICP`` and an empty ``PVLS`` callback.  It compares the result to
TASK-017 and to the smooth stable TASK-012 Python W_a0 probe.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

EPISODE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = EPISODE_ROOT.parents[1]
AUTO_DIR = EPISODE_ROOT / "auto" / "berton_restricted_task021_minimal"
OUT_DIR = EPISODE_ROOT / "outputs" / "task021"
DOC = EPISODE_ROOT / "docs" / "task021_minimal_wa0_auto_diagnostic.md"
TASK012_OUT = REPO_ROOT / "episodes" / "06-full-model-auto-seed-continuation" / "outputs" / "task012"
TASK017_OUT = EPISODE_ROOT / "outputs" / "task017"

TYPE_NAMES = {-9: "MX", -4: "UZ-", 0: "regular", 1: "BP", 2: "LP", 3: "HB", 4: "UZ/NPR", 9: "EP"}
RUNS = {
    "minimal-wA0-plus": {"file": "task021-minimal-wA0-plus", "direction": "upward", "target": 1.2},
    "minimal-wA0-minus": {"file": "task021-minimal-wA0-minus", "direction": "downward", "target": 0.1},
}
Z_SEED = 9.61802753226093591e3
U_SEED = 1.90986233869532240
M_SEED = 1.08022939205920521e-9


def parse_b(path: Path, run_name: str) -> pd.DataFrame:
    rows: list[dict[str, float | int | str]] = []
    for line in path.read_text().splitlines():
        parts = line.split()
        if len(parts) < 8:
            continue
        try:
            br, pt, ty, lab = map(int, parts[:4])
            vals = list(map(float, parts[4:]))
        except ValueError:
            continue
        if len(vals) < 5:
            continue
        z_scaled, u_scaled, m_log_ratio = vals[2], vals[3], vals[4]
        rows.append({
            "run": run_name,
            "branch": br,
            "point": pt,
            "ty": ty,
            "type": TYPE_NAMES.get(ty, f"TY={ty}"),
            "label": lab,
            "control": "W_a0",
            "control_value": vals[0],
            "scaled_l2_norm": vals[1],
            "Z_scaled": z_scaled,
            "U_scaled": u_scaled,
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
        if not text:
            continue
        if any(token in text for token in ("NOTE:", "DGEBAL", "NaN", "floating-point exceptions", "Iterations", "Retrying step")):
            rows.append({"run": run_name, "line": i, "message": text})
    return pd.DataFrame(rows)


def config_summary() -> pd.DataFrame:
    rows = []
    for run_name, meta in RUNS.items():
        text = (AUTO_DIR / f"c.bertonrestricted-task021-{meta['file'].replace('task021-', '')}").read_text()
        def find(pattern: str) -> str:
            m = re.search(pattern, text)
            return m.group(1).strip() if m else ""
        rows.append({
            "run": run_name,
            "config_file": f"c.bertonrestricted-task021-{meta['file'].replace('task021-', '')}",
            "icp": find(r"ICP\s*=\s*(.+)"),
            "isp": int(find(r"ISP=(\d+)") or -1),
            "jac": int(find(r"JAC=(\d+)") or -1),
            "ilp": int(find(r"ILP=(\d+)") or -1),
            "npar": int(find(r"NPAR=(\d+)") or -1),
            "ds": float(find(r"DS=([-+0-9.eE]+)") or "nan"),
            "has_pvls_diagnostic_icp": any(str(k) in find(r"ICP\s*=\s*(.+)") for k in range(60, 99)),
        })
    return pd.DataFrame(rows)


def python_probe_summary() -> pd.DataFrame:
    probe = pd.read_csv(TASK012_OUT / "python_equilibrium_control_probe.csv")
    w = probe[(probe["control"] == "W_a0") & (probe["success"])]
    return pd.DataFrame([{
        "source": "TASK-012 Python W_a0 probe",
        "control_min": float(w.control_value.min()),
        "control_max": float(w.control_value.max()),
        "successful_points": int(len(w)),
        "altitude_span_m": float(w.z_m.max() - w.z_m.min()),
        "all_stable": bool((w.stable_eigenvalue_count == 4).all() and (w.critical_real_s_inv < 0).all()),
        "critical_real_max_s_inv": float(w.critical_real_s_inv.max()),
    }])


def write_note(summary: pd.DataFrame, cfg: pd.DataFrame, notes: pd.DataFrame, verdict: dict[str, object]) -> None:
    row = summary.iloc[0]
    first_notes = "\n".join(f"- `{r.run}` line {int(r.line)}: {r.message}" for r in notes.head(10).itertuples())
    DOC.write_text(
        "# TASK-021 minimal W_a0 AUTO diagnostic\n\n"
        "This diagnostic strips the TASK-017 restricted/scaled equilibrium continuation to the smallest AUTO setup that still asks for continuation in `W_a0`. "
        "The task021 AUTO directory is separate from TASK-017 artifacts.  The AUTO state remains `Z_scaled`, `U_scaled`, `M_log_ratio` with `w=0`, but the active continuation list is only `ICP=['W_a0']`.\n\n"
        "## Commands and raw artifacts\n\n"
        "```bash\n"
        "bash episodes/07-restricted-equilibrium-auto/auto/berton_restricted_task021_minimal/run_auto.sh\n"
        "uv run python episodes/07-restricted-equilibrium-auto/scripts/berton_restricted_task021_minimal_auto.py\n"
        "```\n\n"
        "Raw AUTO files are in `episodes/07-restricted-equilibrium-auto/auto/berton_restricted_task021_minimal/` as "
        "`b./s./d.task021-minimal-wA0-{plus,minus}`. Curated CSV/JSON outputs are in `episodes/07-restricted-equilibrium-auto/outputs/task021/`.\n\n"
        "## Minimal AUTO constants\n\n"
        f"- `ICP`: `{cfg.icp.iloc[0]}` only; no TASK-017 diagnostic or PVLS parameters are active.\n"
        f"- `ISP={int(cfg.isp.iloc[0])}`, `ILP={int(cfg.ilp.iloc[0])}`, `JAC={int(cfg.jac.iloc[0])}`, `NPAR={int(cfg.npar.iloc[0])}`.\n"
        "- The Fortran `PVLS` callback is deliberately empty and `FUNC` supplies no analytic/user Jacobian, so the first run uses AUTO finite-difference Jacobians.\n\n"
        "## Result\n\n"
        f"The two minimal directions printed `{int(row.auto_total_points)}` total branch rows and `{int(row.auto_nontrivial_points)}` non-seed rows. "
        f"The accepted AUTO `W_a0` range remained `{row.auto_control_min:.3f}`-`{row.auto_control_max:.3f}` m/s; therefore no nontrivial point beyond `W_a0=0.6` was accepted.\n\n"
        "First raw diagnostic lines:\n\n"
        f"{first_notes}\n\n"
        "## Comparison\n\n"
        f"TASK-017 also accepted only the seed (`W_a0={row.task017_control_min:.3f}`-`{row.task017_control_max:.3f}`, nontrivial points `{int(row.task017_nontrivial_points)}`). "
        f"In contrast, the TASK-012 Python W_a0 probe successfully follows stable equilibria from `{row.python_probe_min:.1f}` to `{row.python_probe_max:.1f}` m/s with altitude span `{row.python_probe_altitude_span_m:.3f}` m.\n\n"
        "## Interpretation\n\n"
        f"**Verdict:** {verdict['interpretation']}\n\n"
        "Because the failure persists after removing diagnostic ICP entries, PVLS bookkeeping, and supplied Jacobians, the observed first-step divergence is unlikely to be caused solely by TASK-017 diagnostic metadata/PVLS/Jacobian bookkeeping. "
        "The remaining culprit is more likely the AUTO algebraic continuation formulation/scaling/initial tangent setup for this restricted problem, despite the underlying Python equilibrium branch being smooth and stable.\n"
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cfg = config_summary()
    cfg.to_csv(OUT_DIR / "minimal_config_summary.csv", index=False)
    py = python_probe_summary()
    py.to_csv(OUT_DIR / "python_wa0_probe_summary.csv", index=False)

    branch = pd.concat([parse_b(AUTO_DIR / f"b.{meta['file']}", run) for run, meta in RUNS.items()], ignore_index=True)
    branch.to_csv(OUT_DIR / "auto_branch_summary.csv", index=False)
    notes = pd.concat([parse_d(AUTO_DIR / f"d.{meta['file']}", run) for run, meta in RUNS.items()], ignore_index=True)
    notes.to_csv(OUT_DIR / "auto_convergence_notes.csv", index=False)

    task017 = pd.read_csv(TASK017_OUT / "continuation_conditioning_summary.csv").iloc[0]
    nontrivial = branch[np.abs(branch.control_value - 0.6) > 1e-8]
    failure_note = " | ".join(notes.message.astype(str).head(12)) if not notes.empty else ""
    summary = pd.DataFrame([{
        "auto_total_points": int(len(branch)),
        "auto_nontrivial_points": int(len(nontrivial)),
        "auto_control_min": float(branch.control_value.min()),
        "auto_control_max": float(branch.control_value.max()),
        "accepted_beyond_0p6": bool((branch.control_value > 0.60000001).any()),
        "task017_control_min": float(task017.auto_control_min),
        "task017_control_max": float(task017.auto_control_max),
        "task017_nontrivial_points": int(task017.auto_nontrivial_points),
        "python_probe_min": float(py.control_min.iloc[0]),
        "python_probe_max": float(py.control_max.iloc[0]),
        "python_probe_altitude_span_m": float(py.altitude_span_m.iloc[0]),
        "python_probe_all_stable": bool(py.all_stable.iloc[0]),
        "minimal_failure_mode": failure_note[:800],
        "interpretation": "failure persists in stripped configuration; not solely diagnostic/PVLS/supplied-Jacobian bookkeeping",
    }])
    summary.to_csv(OUT_DIR / "minimal_continuation_summary.csv", index=False)

    verdict = {
        "seed_source": "TASK-011/TASK-012 equilibrium",
        "auto_coordinate": "restricted/scaled 3D: Z, U, M=log(m/m_seed), w=0",
        "minimal_icp": ["W_a0"],
        "isp": int(cfg.isp.iloc[0]),
        "ilp": int(cfg.ilp.iloc[0]),
        "jac": int(cfg.jac.iloc[0]),
        "pvls_callback": "empty",
        "wA0_auto_covered_range_m_s": [float(summary.auto_control_min.iloc[0]), float(summary.auto_control_max.iloc[0])],
        "auto_accepted_nontrivial_branch": bool(summary.auto_nontrivial_points.iloc[0] > 0),
        "accepted_beyond_0p6": bool(summary.accepted_beyond_0p6.iloc[0]),
        "wA0_python_expected_range_m_s": [float(py.control_min.iloc[0]), float(py.control_max.iloc[0])],
        "interpretation": str(summary.interpretation.iloc[0]),
    }
    (OUT_DIR / "task021_minimal_auto_verdict.json").write_text(json.dumps(verdict, indent=2) + "\n")
    write_note(summary, cfg, notes, verdict)


if __name__ == "__main__":
    main()
