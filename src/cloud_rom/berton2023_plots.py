"""Plotting and notebook helpers for Berton (2023) Section 3 reproductions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from cloud_rom import berton2023 as b


def qcol(df: pd.DataFrame, column: str, unit: str) -> np.ndarray:
    """Convert a Pint-valued DataFrame column to a NumPy array of magnitudes."""

    return np.asarray(b.quantity_column_to(df, column, unit), dtype=float)


def run_case0(
    *,
    oscillatory: bool,
    duration_h: float,
    dt_s: float,
    samples: int,
    include_coriolis: bool = False,
    progress: bool = True,
    progress_desc: str | None = None,
) -> pd.DataFrame:
    """Run Berton (2023) Case 0 and return sampled Pint-valued diagnostics."""

    cfg = b.SimulationConfig(
        duration=b.Q_(duration_h, "hour"),
        dt=b.Q_(dt_s, "s"),
        include_coriolis=include_coriolis,
        stop_on_nonpositive_mass=True,
    )
    steps = int(cfg.duration.to("s").magnitude / cfg.dt.to("s").magnitude)
    sample_every = max(1, steps // samples)
    if progress_desc is None:
        mode = "oscillatory" if oscillatory else "steady"
        progress_desc = f"{mode} Case 0"
    return b.simulate(
        b.initial_state_for_case(0),
        b.atmosphere_for_case(0, oscillatory=oscillatory),
        config=cfg,
        sample_every=sample_every,
        progress=progress,
        progress_desc=progress_desc,
    )


def magnitude_frame(df: pd.DataFrame, atmosphere: b.Atmosphere) -> pd.DataFrame:
    """Numeric, consistently unit-converted columns used by the plots."""

    out = pd.DataFrame(
        {
            "t_h": qcol(df, "t", "hour"),
            "x_km": qcol(df, "x", "km"),
            "z_km": qcol(df, "z", "km"),
            "u_m_s": qcol(df, "u", "m/s"),
            "w_m_s": qcol(df, "w", "m/s"),
            "m_ug": qcol(df, "m", "microgram"),
            "a_um": qcol(df, "a", "micrometer"),
            "c_um": qcol(df, "c", "micrometer"),
            "cB_um": qcol(df, "c_B", "micrometer"),
            "Di_um": qcol(df, "D_i", "micrometer"),
            "mu_uPa_s": qcol(df, "μ_a", "micropascal * second"),
            "rho_ie_kg_m3": qcol(df, "ρ_ie", "kg/m^3"),
            "k_s_inv": qcol(df, "k", "1/s"),
            "dT_mK": qcol(df, "T_s_minus_T_a", "millikelvin"),
            "Siminus1_pct": 100 * (np.asarray(df["S_i"], dtype=float) - 1),
            "R_pct": 100 * np.asarray(df["R"], dtype=float),
            "drive_pct": 100 * np.asarray(df["driving_factor"], dtype=float),
            "psi": np.asarray(df["ψ"], dtype=float),
            "CD": np.asarray(df["C_D"], dtype=float),
            "Re": np.asarray(df["Re"], dtype=float),
        }
    )
    out["x_minus_x0_km"] = out["x_km"] - out["x_km"].iloc[0]
    out["z_minus_z0_km"] = out["z_km"] - out["z_km"].iloc[0]
    out["Wf_m_s"] = np.asarray(
        [
            row.w.to("m/s").magnitude - atmosphere.updraft(row.z).to("m/s").magnitude
            for row in df.itertuples(index=False)
        ]
    )
    return out


def summarize_run(df: pd.DataFrame, *, requested_duration_h: float) -> None:
    """Print concise run diagnostics for a sampled simulation."""

    last_t_h = df.iloc[-1]["t"].to("hour").magnitude
    last_mass = df.iloc[-1]["m"].to("microgram").magnitude
    print(f"Rows: {len(df)}")
    print(f"Last sampled time: {last_t_h:.3f} h (requested {requested_duration_h:.3f} h)")
    print(f"Last sampled mass: {last_mass:.4f} µg")
    if last_t_h < 0.99 * requested_duration_h:
        print("Stopped early: the crystal mass likely became non-positive between sampled outputs.")


def add_zero(ax: Any) -> None:
    """Add horizontal and vertical zero reference lines to an axis."""

    ax.axhline(0, color="0.4", lw=0.8)
    ax.axvline(0, color="0.4", lw=0.8)


def plot_trajectory_hodograph(data: pd.DataFrame, title: str, *, early_hours: float | None = None) -> Any:
    """Plot Section 3 trajectory and hodograph panels."""

    if early_hours is None:
        fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    else:
        fig, axes = plt.subplots(1, 3, figsize=(15, 4))

    axes[0].plot(data["x_minus_x0_km"], data["z_minus_z0_km"])
    axes[0].set_xlabel(r"$x-x_0$ (km)")
    axes[0].set_ylabel(r"$z-z_0$ (km)")
    axes[0].set_title("trajectory")
    add_zero(axes[0])

    hodograph_ax = axes[-1]
    if early_hours is not None:
        early = data[data["t_h"] <= min(early_hours, data["t_h"].max())]
        axes[1].plot(early["x_minus_x0_km"], early["z_minus_z0_km"])
        axes[1].set_xlabel(r"$x-x_0$ (km)")
        axes[1].set_ylabel(r"$z-z_0$ (km)")
        axes[1].set_title(f"trajectory, first {early_hours:g} h")
        add_zero(axes[1])

    hodograph_ax.plot(data["u_m_s"], data["w_m_s"])
    hodograph_ax.set_xlabel(r"$u$ (m s$^{-1}$)")
    hodograph_ax.set_ylabel(r"$w$ (m s$^{-1}$)")
    hodograph_ax.set_title("hodograph")
    add_zero(hodograph_ax)

    fig.suptitle(title)
    fig.tight_layout()
    return fig


def plot_x_z(data: pd.DataFrame, title: str) -> Any:
    """Plot Section 3 abscissa and altitude time profiles."""

    fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(11, 4), sharex=True)
    ax0.plot(data["t_h"], data["x_minus_x0_km"])
    ax0.set_xlabel("time (h)")
    ax0.set_ylabel(r"$x-x_0$ (km)")
    ax1.plot(data["t_h"], data["z_minus_z0_km"])
    ax1.set_xlabel("time (h)")
    ax1.set_ylabel(r"$z-z_0$ (km)")
    ax1.axhline(0, color="0.4", lw=0.8)
    fig.suptitle(title)
    fig.tight_layout()
    return fig


def plot_microphysics_drivers(data: pd.DataFrame, title: str) -> Any:
    """Plot fall speed, supersaturation, radiation, and driving factor."""

    fig, axes = plt.subplots(2, 2, figsize=(11, 7), sharex=True)
    axes[0, 0].plot(data["t_h"], data["Wf_m_s"])
    axes[0, 0].set_ylabel(r"$W_f=w-W_a$ (m s$^{-1}$)")
    axes[0, 1].plot(data["t_h"], data["drive_pct"])
    axes[0, 1].set_ylabel(r"$S_i-1-R$ (%)")
    axes[1, 0].plot(data["t_h"], data["Siminus1_pct"], label=r"$S_i-1$")
    axes[1, 0].plot(data["t_h"], data["R_pct"], label=r"$R$")
    axes[1, 0].set_ylabel("percent")
    axes[1, 0].legend()
    axes[1, 1].plot(data["t_h"], data["Siminus1_pct"], label=r"$S_i-1$")
    axes[1, 1].plot(data["t_h"], data["R_pct"], label=r"$R$")
    axes[1, 1].plot(data["t_h"], data["drive_pct"], label=r"$S_i-1-R$")
    axes[1, 1].set_ylabel("percent")
    axes[1, 1].legend()
    for ax in axes.ravel():
        ax.set_xlabel("time (h)")
        ax.axhline(0, color="0.4", lw=0.8)
    fig.suptitle(title)
    fig.tight_layout()
    return fig


def plot_size_state(data: pd.DataFrame, title: str) -> Any:
    """Plot mass, dimensions, equivalent diameter, and viscosity."""

    fig, axes = plt.subplots(2, 2, figsize=(11, 7), sharex=True)
    axes[0, 0].plot(data["t_h"], data["m_ug"])
    axes[0, 0].set_ylabel(r"$m$ ($\mu$g)")
    axes[0, 1].plot(data["t_h"], data["a_um"], label=r"$a$")
    axes[0, 1].plot(data["t_h"], data["c_um"], label=r"$c$")
    axes[0, 1].plot(data["t_h"], data["cB_um"], label=r"$c_B$")
    axes[0, 1].set_ylabel(r"dimensions ($\mu$m)")
    axes[0, 1].legend()
    axes[1, 0].plot(data["t_h"], data["Di_um"])
    axes[1, 0].set_ylabel(r"$D_i$ ($\mu$m)")
    axes[1, 1].plot(data["t_h"], data["mu_uPa_s"])
    axes[1, 1].set_ylabel(r"$\mu_a$ ($\mu$Pa s)")
    for ax in axes.ravel():
        ax.set_xlabel("time (h)")
    fig.suptitle(title)
    fig.tight_layout()
    return fig


def plot_drag_state(data: pd.DataFrame, title: str) -> Any:
    """Plot shape, drag, damping, and temperature-difference diagnostics."""

    fig, axes = plt.subplots(3, 2, figsize=(11, 10), sharex=True)
    axes[0, 0].plot(data["t_h"], data["psi"])
    axes[0, 0].set_ylabel(r"$\psi$")
    axes[0, 1].plot(data["t_h"], data["rho_ie_kg_m3"])
    axes[0, 1].set_ylabel(r"$\rho_{ie}$ (kg m$^{-3}$)")
    axes[1, 0].plot(data["t_h"], data["CD"])
    axes[1, 0].set_ylabel(r"$C_D$")
    axes[1, 1].plot(data["t_h"], data["Re"])
    axes[1, 1].set_ylabel(r"$Re$")
    axes[2, 0].plot(data["t_h"], data["k_s_inv"])
    axes[2, 0].set_ylabel(r"$k$ (s$^{-1}$)")
    axes[2, 1].plot(data["t_h"], data["dT_mK"])
    axes[2, 1].set_ylabel(r"$T_s-T_a$ (mK)")
    axes[2, 1].axhline(0, color="0.4", lw=0.8)
    for ax in axes.ravel():
        ax.set_xlabel("time (h)")
    fig.suptitle(title)
    fig.tight_layout()
    return fig


def export_magnitudes(data: pd.DataFrame, path: str | Path) -> Path:
    """Write a numeric magnitude DataFrame to CSV and return the path."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(path, index=False)
    return path
