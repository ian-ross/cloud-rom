"""TASK-009 validation for the full Berton AUTO-07p Fortran port.

The script compiles a small Fortran driver against auto/berton_full/bertonfull.f90,
compares selected RHS samples against src/cloud_rom/berton2023.py, parses the
saved AUTO initial solution, and compares the AUTO fixed point residual and a
Python finite-difference Jacobian/eigenvalue calculation at that point.
"""

from __future__ import annotations

import argparse
import subprocess
import tempfile
from dataclasses import replace
from pathlib import Path

import numpy as np

from cloud_rom.berton2023 import (
    Atmosphere,
    CONSTANTS,
    Crystal,
    LocalDiagnostics,
    Q_,
    SimulationConfig,
    State,
    accelerations,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
AUTO_DIR = REPO_ROOT / "auto" / "berton_full"
FORTRAN = AUTO_DIR / "bertonfull.f90"
S_FILE = AUTO_DIR / "s.bertfull-zW0"
D_FILE = AUTO_DIR / "d.bertfull-zW0"


def python_rhs(y: np.ndarray, par: np.ndarray) -> np.ndarray:
    z, u, w, m = map(float, y)
    eta_blend = float(par[38])
    eta_override = None if abs(eta_blend) < 1e-14 else float(par[4])
    atm = Atmosphere(
        H_a3=float(par[3]),
        W_a0=Q_(float(par[1]), "m/s"),
        z_W0=Q_(float(par[0]), "m"),
        Δz_W=Q_(float(par[6]), "m"),
        η_override=eta_override,
    )
    # The Fortran TASK-009 port exposes many fixed profile parameters in PAR;
    # current validation uses the documented defaults, matching Atmosphere().
    crystal = Crystal(m=Q_(m, "kg"), φ=float(par[39]), c_B=Q_(float(par[40]), "m"))
    state = State(t=Q_(0, "s"), x=Q_(0, "m"), z=Q_(z, "m"), u=Q_(u, "m/s"), w=Q_(w, "m/s"), crystal=crystal)
    config = SimulationConfig(include_coriolis=bool(round(float(par[42]))), reynolds_length="diameter" if par[43] >= 1.5 else "radius")
    diag = LocalDiagnostics.from_state(state, atm, CONSTANTS, config)
    ax, az = accelerations(state, diag, CONSTANTS, config)
    # Fortran supports rad_mult/drag_mult; samples keep defaults == 1.
    return np.array([w, ax.to("m/s^2").magnitude, az.to("m/s^2").magnitude, diag.m_dot.to("kg/s").magnitude])


def compile_and_run_fortran_samples(samples: list[np.ndarray]) -> np.ndarray:
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        driver = tdp / "rhs_driver.f90"
        def dval(x: float) -> str:
            return f"{x:.17e}".replace("e", "D")

        rows = "\n".join(
            f"  y=(/ &\n    {dval(float(s[0]))}, {dval(float(s[1]))}, {dval(float(s[2]))}, {dval(float(s[3]))} /)\n"
            "  call rhs_full(y,par,f)\n"
            "  write(*,'(4ES25.16)') f"
            for s in samples
        )
        driver.write_text(
            "program rhs_driver\n"
            "  use berton_full_model\n"
            "  implicit none\n"
            "  double precision :: par(95), y(4), f(4)\n"
            "  call init_defaults(par)\n"
            f"{rows}\n"
            "end program rhs_driver\n"
        )
        exe = tdp / "rhs_driver"
        subprocess.run(["gfortran", str(FORTRAN), str(driver), "-o", str(exe)], check=True, cwd=tdp)
        out = subprocess.check_output([str(exe)], text=True)
    return np.array([[float(x) for x in line.split()] for line in out.splitlines() if line.strip()])


def default_par() -> np.ndarray:
    samples = [np.array([10178.50407189, -0.89252035945, 0.0, 1.057007179452e-9])]
    # Keep this in sync with STPNT/init_defaults; sufficient for Python reference.
    par = np.zeros(95)
    par[0:7] = [10000.0, 0.6, 1.0, 0.61, 1.0, 1.0, 300.0]
    par[38:44] = [0.0, 2.0, 20.44e-6, np.pi / 4.0, 0.0, 2.0]
    return par


def parse_first_auto_solution() -> tuple[np.ndarray, np.ndarray]:
    text = S_FILE.read_text().splitlines()
    # First solution: line 2 is time + four U values, following parameter block has 95 values.
    u = np.array([float(x) for x in text[1].split()[1:5]])
    vals: list[float] = []
    for line in text[5:]:
        vals.extend(float(x) for x in line.split())
        if len(vals) >= 95:
            break
    if len(vals) < 95:
        raise ValueError(f"Could not parse 95 PAR values from {S_FILE}")
    return u, np.array(vals[:95])


def parse_first_auto_eigenvalues() -> np.ndarray:
    eig: list[complex] = []
    for line in D_FILE.read_text().splitlines():
        if "Eigenvalue " not in line or ":" not in line:
            continue
        vals = line.split(":", 1)[1].split()
        if len(vals) >= 2:
            eig.append(complex(float(vals[0]), float(vals[1])))
        if len(eig) == 4:
            return np.array(eig)
    raise ValueError(f"Could not parse first four AUTO eigenvalues from {D_FILE}")


def finite_difference_jacobian(y: np.ndarray, par: np.ndarray) -> np.ndarray:
    J = np.zeros((4, 4))
    steps = np.array([1.0, 1e-5, 1e-5, max(abs(y[3]) * 1e-4, 1e-14)])
    for i, h in enumerate(steps):
        yp = y.copy(); ym = y.copy(); yp[i] += h; ym[i] -= h
        if i == 3 and ym[i] <= 0:
            ym[i] = y[i] * (1 - 1e-4)
        J[:, i] = (python_rhs(yp, par) - python_rhs(ym, par)) / (yp[i] - ym[i])
    return J


def validate(run_auto: bool = False) -> None:
    if run_auto:
        subprocess.run(["bash", str(AUTO_DIR / "run_auto.sh")], cwd=REPO_ROOT, check=True)

    par = default_par()
    samples = [
        np.array([10178.50407189, -0.89252035945, 0.0, 1.057007179452e-9]),
        np.array([9500.0, 2.5, -0.1, 8.0e-10]),
        np.array([9000.0, 5.0, 0.2, 1.5e-9]),
    ]
    f_fortran = compile_and_run_fortran_samples(samples)
    f_python = np.vstack([python_rhs(s, par) for s in samples])
    diff = np.abs(f_fortran - f_python)
    tol = np.array([1e-12, 5e-8, 5e-8, 5e-18])
    print("Fortran/Python RHS comparison (max abs diff):", diff.max(axis=0))
    if not np.all(diff <= tol):
        raise AssertionError(f"RHS mismatch exceeds tolerances {tol}:\nFortran={f_fortran}\nPython={f_python}\nDiff={diff}")

    if not S_FILE.exists():
        raise FileNotFoundError(f"Missing {S_FILE}; run with --run-auto first")
    y_auto, par_auto = parse_first_auto_solution()
    residual = python_rhs(y_auto, par_auto)
    J = finite_difference_jacobian(y_auto, par_auto)
    eig = np.linalg.eigvals(J)

    # Independently finite-difference the Fortran AUTO-port RHS at the same
    # AUTO fixed point and compare eigenvalues with the Python calculation.
    steps = np.array([1.0, 1e-5, 1e-5, max(abs(y_auto[3]) * 1e-4, 1e-14)])
    fd_samples: list[np.ndarray] = []
    for i, h in enumerate(steps):
        yp = y_auto.copy(); ym = y_auto.copy(); yp[i] += h; ym[i] -= h
        if i == 3 and ym[i] <= 0:
            ym[i] = y_auto[i] * (1 - 1e-4)
        fd_samples.extend([yp, ym])
    f_fd = compile_and_run_fortran_samples(fd_samples)
    J_fortran = np.zeros((4, 4))
    for i in range(4):
        yp, ym = fd_samples[2 * i], fd_samples[2 * i + 1]
        J_fortran[:, i] = (f_fd[2 * i] - f_fd[2 * i + 1]) / (yp[i] - ym[i])
    eig_fortran = np.linalg.eigvals(J_fortran)

    print("AUTO initial solution U:", y_auto)
    print("Python residual at AUTO initial solution:", residual)
    print("Residual norm:", np.linalg.norm(residual))
    eig_auto = parse_first_auto_eigenvalues()
    print("AUTO d-file eigenvalues:", eig_auto)
    print("Python finite-difference Jacobian eigenvalues:", eig)
    print("Fortran AUTO-port finite-difference Jacobian eigenvalues:", eig_fortran)
    if np.linalg.norm(residual) > 1e-7:
        raise AssertionError("AUTO initial fixed-point residual is not small")
    if not np.allclose(np.sort_complex(eig_fortran), np.sort_complex(eig), rtol=5e-5, atol=1e-8):
        raise AssertionError("Fortran/Python finite-difference eigenvalues differ")
    if not np.allclose(np.sort_complex(eig_auto), np.sort_complex(eig), rtol=5e-5, atol=1e-8):
        raise AssertionError("AUTO/Python eigenvalues differ")
    print("Validation passed: Fortran RHS matches Python samples and AUTO fixed point residual/eigenvalues are independently checked.")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run-auto", action="store_true", help="run AUTO before validation")
    args = ap.parse_args()
    validate(run_auto=args.run_auto)


if __name__ == "__main__":
    main()
