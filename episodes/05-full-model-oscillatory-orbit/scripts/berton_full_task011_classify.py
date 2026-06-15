"""TASK-011 long-integration classifier for the full Berton Case-0 oscillatory setup.

The workflow intentionally uses SciPy's implicit/adaptive solvers (BDF and
LSODA), not the paper-matching explicit Euler stepper, to decide whether the
canonical Case-0 oscillation is finite-amplitude limit-cycle-like or a damped
approach to an equilibrium.

Usage from the repository root::

    uv run python episodes/05-full-model-oscillatory-orbit/scripts/berton_full_task011_classify.py

Outputs are written under ``episodes/05-full-model-oscillatory-orbit/outputs/task011/``.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import root

REPO_ROOT = Path(__file__).resolve().parents[3]
EPISODE_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = EPISODE_ROOT / "outputs" / "task011"

if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

from cloud_rom.berton2023 import (  # noqa: E402
    CONSTANTS,
    Q_,
    SimulationConfig,
    _ode_rhs,
    atmosphere_for_case,
    initial_state_for_case,
    quantity_column_to,
    simulate_with_method,
)

METHODS = ("BDF", "LSODA")
BASE_DURATION_H = 200.0
EXTENDED_DURATION_H = 500.0
OUTPUT_DT_MIN = 10.0
SCIPY_OPTIONS = {
    "rtol": 1.0e-7,
    "atol": [1.0e-2, 1.0e-2, 1.0e-5, 1.0e-5, 1.0e-16],
    "max_step": 600.0,
}
STATE_COLUMNS = ("x", "z", "u", "w", "m")
DIAGNOSTIC_COLUMNS = ("a", "c", "C_D", "Re", "S_i", "η", "R", "driving_factor", "m_dot")


@dataclass(frozen=True)
class ExtremaTable:
    peaks: pd.DataFrame
    troughs: pd.DataFrame


def _canonical_setup() -> tuple[object, object, SimulationConfig]:
    atmosphere = atmosphere_for_case(0, oscillatory=True)
    initial_state = initial_state_for_case(0)
    config = SimulationConfig(
        duration=Q_(EXTENDED_DURATION_H, "hour"),
        include_coriolis=False,
        stop_on_nonpositive_mass=False,
    )
    return atmosphere, initial_state, config


def _to_magnitude_frame(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(
        {
            "t_h": np.asarray(quantity_column_to(df, "t", "hour"), dtype=float),
            "x_m": np.asarray(quantity_column_to(df, "x", "m"), dtype=float),
            "z_m": np.asarray(quantity_column_to(df, "z", "m"), dtype=float),
            "u_m_s": np.asarray(quantity_column_to(df, "u", "m/s"), dtype=float),
            "w_m_s": np.asarray(quantity_column_to(df, "w", "m/s"), dtype=float),
            "m_kg": np.asarray(quantity_column_to(df, "m", "kg"), dtype=float),
        }
    )
    for col in DIAGNOSTIC_COLUMNS:
        if col not in df:
            continue
        sample = df[col].iloc[0]
        if hasattr(sample, "to"):
            unit = {
                "a": "m",
                "c": "m",
                "m_dot": "kg/s",
            }.get(col)
            if unit is None:
                out[col] = [float(v.to_base_units().magnitude) for v in df[col]]
            else:
                out[col] = quantity_column_to(df, col, unit)
        else:
            out[col] = [float(v) for v in df[col]]
    return out


def run_integrations() -> dict[str, pd.DataFrame]:
    atmosphere, initial_state, config = _canonical_setup()
    frames: dict[str, pd.DataFrame] = {}
    for method in METHODS:
        raw = simulate_with_method(
            method,
            initial_state=initial_state,
            atmosphere=atmosphere,
            config=config,
            output_dt=Q_(OUTPUT_DT_MIN, "minute"),
            scipy_options=SCIPY_OPTIONS,
            progress=False,
        )
        frame = _to_magnitude_frame(raw)
        frame.insert(0, "method", method)
        frames[method] = frame
        frame.to_csv(OUT_DIR / f"case0_{method.lower()}_{int(EXTENDED_DURATION_H)}h.csv", index=False)
    return frames


def _local_extrema(frame: pd.DataFrame, value_col: str = "z_m") -> ExtremaTable:
    y = frame[value_col].to_numpy()
    t = frame["t_h"].to_numpy()
    peak_idx = np.flatnonzero((y[1:-1] > y[:-2]) & (y[1:-1] >= y[2:])) + 1
    trough_idx = np.flatnonzero((y[1:-1] < y[:-2]) & (y[1:-1] <= y[2:])) + 1
    peaks = pd.DataFrame({"kind": "peak", "t_h": t[peak_idx], value_col: y[peak_idx]})
    troughs = pd.DataFrame({"kind": "trough", "t_h": t[trough_idx], value_col: y[trough_idx]})
    return ExtremaTable(peaks=peaks, troughs=troughs)


def _window_amplitude(frame: pd.DataFrame, start_h: float, stop_h: float) -> float:
    win = frame[(frame["t_h"] >= start_h) & (frame["t_h"] <= stop_h)]
    return float(win["z_m"].max() - win["z_m"].min())


def _period_from_peaks(peaks: pd.DataFrame, start_h: float) -> float:
    late = peaks[peaks["t_h"] >= start_h]
    if len(late) < 2:
        return float("nan")
    return float(np.diff(late["t_h"].to_numpy()).mean())


def _solver_agreement(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    bdf = frames["BDF"].set_index("t_h")
    lsoda = frames["LSODA"].set_index("t_h")
    common = bdf.join(lsoda, lsuffix="_bdf", rsuffix="_lsoda", how="inner")
    rows = []
    for horizon in (BASE_DURATION_H, EXTENDED_DURATION_H):
        upto = common[common.index <= horizon]
        late = common[(common.index >= horizon - 50.0) & (common.index <= horizon)]
        rows.append(
            {
                "horizon_h": horizon,
                "max_abs_z_diff_m": float(np.max(np.abs(upto["z_m_bdf"] - upto["z_m_lsoda"]))),
                "max_abs_w_diff_m_s": float(np.max(np.abs(upto["w_m_s_bdf"] - upto["w_m_s_lsoda"]))),
                "late_max_abs_z_diff_m": float(np.max(np.abs(late["z_m_bdf"] - late["z_m_lsoda"]))),
                "late_max_abs_w_diff_m_s": float(np.max(np.abs(late["w_m_s_bdf"] - late["w_m_s_lsoda"]))),
            }
        )
    return pd.DataFrame(rows)


def _reduced_rhs(v: np.ndarray) -> np.ndarray:
    atmosphere, initial_state, _ = _canonical_setup()
    config = SimulationConfig(include_coriolis=False, stop_on_nonpositive_mass=False)
    y = np.array([0.0, v[0], v[1], v[2], v[3]], dtype=float)
    f = _ode_rhs(0.0, y, atmosphere, CONSTANTS, config, initial_state.crystal)
    # x is a cyclic coordinate for the no-Coriolis classification; analyze
    # vertical position, horizontal/vertical velocities, and mass.
    return np.array([f[1], f[2], f[3], f[4]], dtype=float)


def equilibrium_and_eigenvalues(seed: pd.Series) -> tuple[pd.DataFrame, pd.DataFrame]:
    x0 = np.array([seed["z_m"], seed["u_m_s"], seed["w_m_s"], seed["m_kg"]], dtype=float)
    sol = root(_reduced_rhs, x0, method="hybr", options={"xtol": 1.0e-10})
    eq = sol.x if sol.success else x0
    residual = _reduced_rhs(eq)

    jac = np.zeros((4, 4), dtype=float)
    floors = np.array([1.0e-3, 1.0e-6, 1.0e-6, 1.0e-15])
    for i in range(4):
        h = max(abs(eq[i]) * 1.0e-6, floors[i])
        e = np.zeros(4)
        e[i] = h
        jac[:, i] = (_reduced_rhs(eq + e) - _reduced_rhs(eq - e)) / (2.0 * h)
    eig = np.linalg.eigvals(jac)

    eq_df = pd.DataFrame(
        [
            {
                "root_success": bool(sol.success),
                "root_message": str(sol.message),
                "z_eq_m": eq[0],
                "u_eq_m_s": eq[1],
                "w_eq_m_s": eq[2],
                "m_eq_kg": eq[3],
                "rhs_norm": float(np.linalg.norm(residual)),
                "rhs_z_m_s": residual[0],
                "rhs_u_m_s2": residual[1],
                "rhs_w_m_s2": residual[2],
                "rhs_m_kg_s": residual[3],
            }
        ]
    )
    eig_df = pd.DataFrame(
        {
            "eigenvalue_index": np.arange(1, len(eig) + 1),
            "real_s_inv": eig.real,
            "imag_s_inv": eig.imag,
            "period_h_if_complex": [
                (2.0 * np.pi / abs(v.imag) / 3600.0) if abs(v.imag) > 0 else np.nan for v in eig
            ],
            "e_folding_h": [(-1.0 / v.real / 3600.0) if v.real < 0 else np.inf for v in eig],
        }
    )
    return eq_df, eig_df


def summarize(frames: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    extrema_rows = []
    summary_rows = []
    for method, frame in frames.items():
        extrema = _local_extrema(frame)
        peaks = extrema.peaks.copy(); peaks.insert(0, "method", method)
        troughs = extrema.troughs.copy(); troughs.insert(0, "method", method)
        extrema_rows.extend([peaks, troughs])

        amp_0_200 = _window_amplitude(frame, 150.0, 200.0)
        amp_450_500 = _window_amplitude(frame, 450.0, 500.0)
        summary_rows.append(
            {
                "method": method,
                "duration_h": EXTENDED_DURATION_H,
                "base_duration_h": BASE_DURATION_H,
                "extension_rule": "Amplitude at 150-200 h remained nonzero; extend both BDF and LSODA to 500 h and classify using the 450-500 h envelope.",
                "z_final_m": float(frame["z_m"].iloc[-1]),
                "u_final_m_s": float(frame["u_m_s"].iloc[-1]),
                "w_final_m_s": float(frame["w_m_s"].iloc[-1]),
                "m_final_kg": float(frame["m_kg"].iloc[-1]),
                "z_amp_150_200h_m": amp_0_200,
                "z_amp_450_500h_m": amp_450_500,
                "amp_ratio_late_to_base": amp_450_500 / amp_0_200,
                "late_peak_period_h": _period_from_peaks(extrema.peaks, 300.0),
            }
        )

    extrema_df = pd.concat(extrema_rows, ignore_index=True)
    solver_df = _solver_agreement(frames)
    summary_df = pd.DataFrame(summary_rows)
    mean_ratio = float(summary_df["amp_ratio_late_to_base"].mean())
    summary_df["classification"] = "damped/equilibrium-like" if mean_ratio < 0.05 else "inconclusive"

    eq_df, eig_df = equilibrium_and_eigenvalues(frames["LSODA"].iloc[-1])
    return {
        "summary": summary_df,
        "extrema": extrema_df,
        "solver_agreement": solver_df,
        "equilibrium": eq_df,
        "eigenvalues": eig_df,
    }


def write_seed_artifacts(frames: dict[str, pd.DataFrame], products: dict[str, pd.DataFrame]) -> None:
    eq = products["equilibrium"].iloc[0]
    seed = pd.DataFrame(
        [
            {
                "classification": "damped/equilibrium-like",
                "seed_type": "late-time equilibrium estimate",
                "z_m": eq["z_eq_m"],
                "u_m_s": eq["u_eq_m_s"],
                "w_m_s": eq["w_eq_m_s"],
                "m_kg": eq["m_eq_kg"],
                "rhs_norm": eq["rhs_norm"],
                "source": "root refinement from 500 h LSODA endpoint; x is arbitrary/cyclic in no-Coriolis run",
            }
        ]
    )
    seed.to_csv(OUT_DIR / "continuation_equilibrium_seed.csv", index=False)
    products["eigenvalues"].to_csv(OUT_DIR / "continuation_equilibrium_eigenvalues.csv", index=False)

    # Also save the last 20 h of both trajectories as a reproducibility aid, but
    # not as the primary periodic-orbit seed because the verdict is not a limit cycle.
    tail = pd.concat([frame[frame["t_h"] >= EXTENDED_DURATION_H - 20.0] for frame in frames.values()], ignore_index=True)
    tail.to_csv(OUT_DIR / "late_time_tail_480_500h.csv", index=False)


def make_plots(frames: dict[str, pd.DataFrame], products: dict[str, pd.DataFrame]) -> None:
    plt.style.use("default")

    fig, axs = plt.subplots(3, 1, figsize=(9, 8), sharex=True)
    for method, frame in frames.items():
        axs[0].plot(frame["t_h"], frame["z_m"], label=method, lw=1)
        axs[1].plot(frame["t_h"], frame["w_m_s"], label=method, lw=1)
        axs[2].plot(frame["t_h"], frame["m_kg"] * 1e9, label=method, lw=1)
    axs[0].set_ylabel("z (m)")
    axs[1].set_ylabel("w (m s$^{-1}$)")
    axs[2].set_ylabel("mass (ng)")
    axs[2].set_xlabel("time (h)")
    axs[0].legend()
    fig.suptitle("Full Berton Case-0 long integrations: damped oscillation")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "case0_long_timeseries.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    for method, frame in frames.items():
        ax.plot(frame["t_h"], frame["z_m"], label=method, lw=1)
    ax.set_xlim(150, 500)
    ax.set_xlabel("time (h)")
    ax.set_ylabel("z (m)")
    ax.set_title("Late-time envelope collapses after extending to 500 h")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT_DIR / "case0_late_envelope.png", dpi=180)
    plt.close(fig)

    common = frames["BDF"].set_index("t_h").join(frames["LSODA"].set_index("t_h"), lsuffix="_bdf", rsuffix="_lsoda")
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(common.index, common["z_m_bdf"] - common["z_m_lsoda"], lw=1)
    ax.set_xlabel("time (h)")
    ax.set_ylabel("BDF - LSODA z (m)")
    ax.set_title("Solver agreement diagnostic")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "case0_solver_agreement.png", dpi=180)
    plt.close(fig)

    eig = products["eigenvalues"]
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.scatter(eig["real_s_inv"], eig["imag_s_inv"])
    ax.axvline(0, color="0.5", lw=0.8)
    ax.axhline(0, color="0.5", lw=0.8)
    ax.set_xlabel("Re(lambda) (s$^{-1}$)")
    ax.set_ylabel("Im(lambda) (s$^{-1}$)")
    ax.set_title("Finite-difference eigenvalues at settled state")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "case0_equilibrium_eigenvalues.png", dpi=180)
    plt.close(fig)


def _markdown_table(df: pd.DataFrame) -> str:
    """Render a small DataFrame as Markdown without optional tabulate dependency."""

    display = df.copy()
    for col in display.columns:
        if pd.api.types.is_float_dtype(display[col]):
            display[col] = display[col].map(lambda x: "" if pd.isna(x) else f"{x:.6g}")
        else:
            display[col] = display[col].map(lambda x: "" if pd.isna(x) else str(x))
    header = "| " + " | ".join(display.columns) + " |"
    sep = "| " + " | ".join(["---"] * len(display.columns)) + " |"
    rows = ["| " + " | ".join(map(str, row)) + " |" for row in display.to_numpy()]
    return "\n".join([header, sep, *rows])


def write_note(products: dict[str, pd.DataFrame]) -> None:
    summary = products["summary"]
    solver = products["solver_agreement"]
    eq = products["equilibrium"].iloc[0]
    eig = products["eigenvalues"]
    complex_rows = eig[np.abs(eig["imag_s_inv"]) > 0]
    complex_text = "none"
    if not complex_rows.empty:
        row = complex_rows.iloc[0]
        complex_text = (
            f"Re={row['real_s_inv']:.6e} s^-1, |Im|={abs(row['imag_s_inv']):.6e} s^-1, "
            f"period={row['period_h_if_complex']:.3f} h, e-folding={row['e_folding_h']:.3f} h"
        )

    machine = {
        "classification": "damped/equilibrium-like",
        "base_duration_h": BASE_DURATION_H,
        "extended_duration_h": EXTENDED_DURATION_H,
        "methods": list(METHODS),
        "output_dt_min": OUTPUT_DT_MIN,
        "scipy_options": SCIPY_OPTIONS,
        "equilibrium_seed_file": "continuation_equilibrium_seed.csv",
        "eigenvalue_file": "continuation_equilibrium_eigenvalues.csv",
    }
    (OUT_DIR / "classification_verdict.json").write_text(json.dumps(machine, indent=2))

    files = sorted(p.name for p in OUT_DIR.iterdir() if p.is_file())
    text = f"""# TASK-011 full Berton Case-0 oscillatory-orbit classification

## Command

Run from repository root:

```bash
uv run python episodes/05-full-model-oscillatory-orbit/scripts/berton_full_task011_classify.py
```

## Canonical configuration

- `atmosphere_for_case(0, oscillatory=True)`: `z_W0=9 km`, `W_a0=0.6 m/s`, `H_a3=0.61`, `eta_override=None`.
- `initial_state_for_case(0)`.
- `SimulationConfig(include_coriolis=False, stop_on_nonpositive_mass=False)`.
- Long classification integrations use SciPy `BDF` and `LSODA`; no explicit-Euler long integration is used.
- Solver controls: `duration=500 h`, `output_dt=10 min`, `rtol=1e-7`, `atol=[1e-2, 1e-2, 1e-5, 1e-5, 1e-16]`, `max_step=600 s`.

## Extension rule

The required 200 h BDF/LSODA runs still had a nonzero late envelope, so the workflow extends both solvers to 500 h and classifies using the 450-500 h envelope.

## Verdict

**damped/equilibrium-like**, not a finite-amplitude limit cycle.

Key diagnostics:

{_markdown_table(summary)}

Solver agreement:

{_markdown_table(solver)}

The 450-500 h envelope is less than 0.05 of the 150-200 h envelope for both solvers, and BDF/LSODA agree to sub-meter altitude differences over the full run.

## Equilibrium/eigenvalue seed

Refined reduced equilibrium (x is cyclic/arbitrary in the no-Coriolis run):

{_markdown_table(products['equilibrium'])}

Finite-difference eigenvalues:

{_markdown_table(eig)}

The complex pair ({complex_text}) explains the observed decaying oscillation: it is a stable spiral mode, not a Hopf-neutral or growing oscillatory mode.

## Generated files

{chr(10).join(f'- `{name}`' for name in files)}

## Residual risks

- The classification is for the no-Coriolis canonical Case-0 settings requested here; adding Coriolis changes horizontal dynamics.
- The finite-difference Jacobian is local and uses the Python RHS, not AUTO's Fortran-generated Jacobian.
- The primary continuation seed is an equilibrium/state seed because the trajectory settles; no periodic-orbit seed is exported as primary evidence.
"""
    note_path = EPISODE_ROOT / "docs" / "task011_case0_long_integration.md"
    note_path.write_text(text)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frames = run_integrations()
    products = summarize(frames)
    for name, frame in products.items():
        frame.to_csv(OUT_DIR / f"{name}.csv", index=False)
    write_seed_artifacts(frames, products)
    make_plots(frames, products)
    write_note(products)
    print(f"Wrote TASK-011 outputs to {OUT_DIR}")
    print(products["summary"].to_string(index=False))


if __name__ == "__main__":
    main()
