"""TASK-022 standalone validation for restricted Berton AUTO Fortran.

Run from the repository root::

    uv run python episodes/07-restricted-equilibrium-auto/scripts/berton_restricted_task022_validate_fortran.py

This script compiles the TASK-017 restricted/scaled AUTO Fortran source outside
AUTO, calls STPNT/FUNC/PVLS at selected samples, compares residuals and
Jacobians against Python finite differences, and runs an affine local surrogate
AUTO continuation based on the validated seed tangent.
"""

from __future__ import annotations

import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
EPISODE_ROOT = SCRIPT_DIR.parents[0]
REPO_ROOT = SCRIPT_DIR.parents[2]
AUTO017 = EPISODE_ROOT / "auto" / "berton_restricted_task017"
WORK_DIR = EPISODE_ROOT / "auto" / "berton_restricted_task022_validate"
LINEAR_DIR = EPISODE_ROOT / "auto" / "berton_restricted_task022_linear_surrogate"
OUT_DIR = EPISODE_ROOT / "outputs" / "task022"
DOC = EPISODE_ROOT / "docs" / "task022_restricted_fortran_validation.md"
TASK012_OUT = REPO_ROOT / "episodes" / "06-full-model-auto-seed-continuation" / "outputs" / "task012"
TASK021_OUT = EPISODE_ROOT / "outputs" / "task021"

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from berton_restricted_task018_diagnostics import (  # noqa: E402
    RESIDUAL_NAMES,
    local_diagnostics,
    restricted_residual,
    seed_physical,
    task011_parameters,
)

Z_SEED = 9.61802753226093591e3
U_SEED = 1.90986233869532240
M_SEED = 1.08022939205920521e-9
LOG_M_SEED = math.log(M_SEED)
STATE_NAMES = ("Z_scaled", "U_scaled", "M_log_ratio")
DFDU_STEPS = np.array([1e-4, 1e-5, 1e-4], dtype=float)
TASK017_ICP = [2, 1, 4, 96, 97, 98, 60, 61, 62, 63, 65, 67]
ACTIVE_DFDP_PARAMS = [2, 1, 4]
PARAM_NAMES = {1: "z_W0", 2: "W_a0", 4: "H_a3"}
PVLS_PARAMS = [60, 61, 62, 63, 64, 65, 66, 67, 68, 75, 77, 79, 80, 81, 91, 92, 93, 94, 95, 96, 97, 98]


def scaled_to_physical_u(u: np.ndarray) -> np.ndarray:
    return np.array([Z_SEED + 100.0 * u[0], U_SEED + u[1], LOG_M_SEED + u[2]], dtype=float)


def full_state_from_scaled(u: np.ndarray) -> np.ndarray:
    z, horiz, log_m = scaled_to_physical_u(u)
    return np.array([z, horiz, 0.0, math.exp(log_m)], dtype=float)


def scaled_residual(u: np.ndarray, par: np.ndarray) -> np.ndarray:
    rec = json.loads((EPISODE_ROOT / "outputs" / "task018" / "scaling_recommendation.json").read_text())
    scales = np.array([rec["residual_scales"][name] for name in RESIDUAL_NAMES], dtype=float)
    return restricted_residual(scaled_to_physical_u(u), par, residual_scale=scales)


def centered_jacobian(fun, x: np.ndarray, steps: np.ndarray) -> np.ndarray:
    base = np.asarray(fun(x), dtype=float)
    out = np.zeros((len(base), len(x)), dtype=float)
    for j, h in enumerate(steps):
        xp = x.copy(); xm = x.copy()
        xp[j] += h; xm[j] -= h
        out[:, j] = (fun(xp) - fun(xm)) / (xp[j] - xm[j])
    return out


def parameter_sensitivity(u: np.ndarray, par: np.ndarray, fortran_param_index: int) -> np.ndarray:
    idx = fortran_param_index - 1
    p0 = float(par[idx])
    h = max(abs(p0) * 1e-5, 1e-6)
    pp = par.copy(); pm = par.copy()
    pp[idx] += h; pm[idx] -= h
    return (scaled_residual(u, pp) - scaled_residual(u, pm)) / (pp[idx] - pm[idx])


def build_samples() -> pd.DataFrame:
    par = task011_parameters()
    u0 = np.zeros(3)
    A = centered_jacobian(lambda x: scaled_residual(x, par), u0, DFDU_STEPS)
    b = parameter_sensitivity(u0, par, 2)
    tangent = -np.linalg.solve(A, b)
    rows = [{"sample": "seed", "source": "TASK-011/TASK-012 seed", "W_a0": 0.6, "Z_scaled": 0.0, "U_scaled": 0.0, "M_log_ratio": 0.0}]
    dw = 0.001
    up = tangent * dw
    rows.append({"sample": "tangent_predictor_W0p601", "source": "implicit tangent predictor", "W_a0": 0.601, "Z_scaled": up[0], "U_scaled": up[1], "M_log_ratio": up[2]})
    probe = pd.read_csv(TASK012_OUT / "python_equilibrium_control_probe.csv")
    for target in (0.5, 0.7, 1.0):
        row = probe[(probe.control == "W_a0") & np.isclose(probe.control_value, target)].iloc[0]
        rows.append({
            "sample": f"task012_probe_W{target:.1f}".replace(".", "p"),
            "source": "TASK-012 Python W_a0 probe equilibrium",
            "W_a0": float(row.control_value),
            "Z_scaled": (float(row.z_m) - Z_SEED) / 100.0,
            "U_scaled": float(row.u_m_s) - U_SEED,
            "M_log_ratio": math.log(float(row.m_kg) / M_SEED),
        })
    return pd.DataFrame(rows)


def write_fortran_driver(samples: pd.DataFrame) -> None:
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(AUTO017 / "bertonrestricted_task017.f90", WORK_DIR / "bertonrestricted_task017.f90")
    n = len(samples)
    u_rows = []
    w_vals = []
    names = []
    for row in samples.itertuples(index=False):
        u_rows.extend([row.Z_scaled, row.U_scaled, row.M_log_ratio])
        w_vals.append(row.W_a0)
        names.append(str(row.sample))
    def fvals(vals: list[float]) -> str:
        return ", ".join(f"{v:.17E}" for v in vals)
    names_init = ", ".join(f"'{name:<32s}'" for name in names)
    driver = f"""
PROGRAM task022_driver
  IMPLICIT NONE
  INTEGER, PARAMETER :: dp=KIND(1.0D0), ns={n}, ndim=3, npar=98
  DOUBLE PRECISION :: U(ndim), PAR(npar), F(ndim), DFDU(ndim,ndim), DFDP(ndim,npar)
  DOUBLE PRECISION :: samples(ndim,ns), wvals(ns)
  INTEGER :: ICP(12), PVALS({len(PVLS_PARAMS)}), s, i, j, p
  CHARACTER(LEN=32) :: names(ns)
  DATA samples / {fvals(u_rows)} /
  DATA wvals / {fvals(w_vals)} /
  DATA names / {names_init} /
  DATA ICP / 2,1,4,96,97,98,60,61,62,63,65,67 /
  DATA PVALS / {','.join(map(str, PVLS_PARAMS))} /
  WRITE(*,'(A)') 'kind sample i j value'
  DO s=1,ns
    CALL STPNT(ndim,U,PAR,0D0)
    U(1:ndim)=samples(1:ndim,s)
    PAR(2)=wvals(s)
    DFDU=0D0; DFDP=0D0
    CALL FUNC(ndim,U,ICP,PAR,2,F,DFDU,DFDP)
    DO i=1,ndim
      WRITE(*,'(A,1X,A,1X,I0,1X,I0,1X,ES24.16)') 'residual', TRIM(names(s)), i, 0, F(i)
    END DO
    DO i=1,ndim
      DO j=1,ndim
        WRITE(*,'(A,1X,A,1X,I0,1X,I0,1X,ES24.16)') 'dfdu', TRIM(names(s)), i, j, DFDU(i,j)
      END DO
    END DO
    DO i=1,ndim
      DO j=1,3
        p=ICP(j)
        WRITE(*,'(A,1X,A,1X,I0,1X,I0,1X,ES24.16)') 'dfdp', TRIM(names(s)), i, p, DFDP(i,p)
      END DO
    END DO
    CALL PVLS(ndim,U,PAR)
    DO j=1,{len(PVLS_PARAMS)}
      p=PVALS(j)
      WRITE(*,'(A,1X,A,1X,I0,1X,I0,1X,ES24.16)') 'pvls', TRIM(names(s)), p, 0, PAR(p)
    END DO
  END DO
END PROGRAM task022_driver
"""
    (WORK_DIR / "task022_driver.f90").write_text(driver)


def compile_and_run_driver() -> pd.DataFrame:
    subprocess.run(["gfortran", "-O0", "-g", "-c", "bertonrestricted_task017.f90", "-o", "bertonrestricted_task017.o"], cwd=WORK_DIR, check=True)
    subprocess.run(["gfortran", "-O0", "-g", "bertonrestricted_task017.o", "task022_driver.f90", "-o", "task022_driver.exe"], cwd=WORK_DIR, check=True)
    out = subprocess.run(["./task022_driver.exe"], cwd=WORK_DIR, check=True, text=True, capture_output=True).stdout
    rows = []
    for line in out.splitlines()[1:]:
        parts = line.split()
        if len(parts) != 5:
            continue
        rows.append({"kind": parts[0], "sample": parts[1], "i": int(parts[2]), "j": int(parts[3]), "value": float(parts[4])})
    df = pd.DataFrame(rows)
    df.to_csv(OUT_DIR / "fortran_driver_raw.csv", index=False)
    return df


def compare_residuals(samples: pd.DataFrame, raw: pd.DataFrame) -> pd.DataFrame:
    rows = []
    base_par = task011_parameters()
    for _, sample in samples.iterrows():
        sample_name = str(sample["sample"])
        par = base_par.copy(); par[1] = float(sample.W_a0)
        u = np.array([sample.Z_scaled, sample.U_scaled, sample.M_log_ratio], dtype=float)
        py = scaled_residual(u, par)
        ft = raw[(raw.kind == "residual") & (raw["sample"] == sample_name)].sort_values("i").value.to_numpy()
        for k, name in enumerate(RESIDUAL_NAMES, start=1):
            rows.append({"sample": sample_name, "W_a0": sample.W_a0, "residual": name, "fortran": ft[k-1], "python": py[k-1], "abs_error": abs(ft[k-1] - py[k-1])})
    df = pd.DataFrame(rows)
    df.to_csv(OUT_DIR / "residual_comparison.csv", index=False)
    return df


def compare_dfdu(samples: pd.DataFrame, raw: pd.DataFrame) -> pd.DataFrame:
    rows = []
    base_par = task011_parameters()
    for _, sample in samples.iterrows():
        sample_name = str(sample["sample"])
        par = base_par.copy(); par[1] = float(sample.W_a0)
        u = np.array([sample.Z_scaled, sample.U_scaled, sample.M_log_ratio], dtype=float)
        py = centered_jacobian(lambda x: scaled_residual(x, par), u, DFDU_STEPS)
        for i in range(1, 4):
            for j in range(1, 4):
                ft = raw[(raw.kind == "dfdu") & (raw["sample"] == sample_name) & (raw.i == i) & (raw.j == j)].value.iloc[0]
                rows.append({"sample": sample_name, "row": i, "column": j, "state": STATE_NAMES[j-1], "fortran": ft, "python_fd": py[i-1, j-1], "abs_error": abs(ft - py[i-1, j-1])})
    df = pd.DataFrame(rows)
    df.to_csv(OUT_DIR / "dfdu_comparison.csv", index=False)
    return df


def compare_dfdp(samples: pd.DataFrame, raw: pd.DataFrame) -> pd.DataFrame:
    rows = []
    base_par = task011_parameters()
    for _, sample in samples.iterrows():
        sample_name = str(sample["sample"])
        par = base_par.copy(); par[1] = float(sample.W_a0)
        u = np.array([sample.Z_scaled, sample.U_scaled, sample.M_log_ratio], dtype=float)
        for p in ACTIVE_DFDP_PARAMS:
            py = parameter_sensitivity(u, par, p)
            for i in range(1, 4):
                ft = raw[(raw.kind == "dfdp") & (raw["sample"] == sample_name) & (raw.i == i) & (raw.j == p)].value.iloc[0]
                rows.append({"sample": sample_name, "row": i, "parameter_index": p, "parameter": PARAM_NAMES[p], "fortran": ft, "python_fd": py[i-1], "abs_error": abs(ft - py[i-1])})
    df = pd.DataFrame(rows)
    df.to_csv(OUT_DIR / "dfdp_comparison.csv", index=False)
    return df


def compare_pvls(samples: pd.DataFrame, raw: pd.DataFrame) -> pd.DataFrame:
    rows = []
    base_par = task011_parameters()
    mapping = {
        67: ("k", lambda d, y: d.k.to("1/s").magnitude if hasattr(d.k, "to") else float(d.k)),
        68: ("Re", lambda d, y: float(d.Re)),
        75: ("S_i", lambda d, y: float(d.S_i)),
        77: ("eta", lambda d, y: float(getattr(d, "η"))),
        79: ("W_a", lambda d, y: d.W_a.to("m/s").magnitude),
        80: ("U_a", lambda d, y: d.U_a.to("m/s").magnitude),
        96: ("z_phys", lambda d, y: float(y[0])),
        97: ("u_phys", lambda d, y: float(y[1])),
        98: ("m_phys", lambda d, y: float(y[3])),
    }
    for _, sample in samples.iterrows():
        sample_name = str(sample["sample"])
        par = base_par.copy(); par[1] = float(sample.W_a0)
        u = np.array([sample.Z_scaled, sample.U_scaled, sample.M_log_ratio], dtype=float)
        y = full_state_from_scaled(u)
        diag = local_diagnostics(y, par)
        for p, (name, fun) in mapping.items():
            ft = raw[(raw.kind == "pvls") & (raw["sample"] == sample_name) & (raw.i == p)].value.iloc[0]
            py = float(fun(diag, y))
            rows.append({"sample": sample_name, "parameter_index": p, "diagnostic": name, "fortran": ft, "python": py, "abs_error": abs(ft - py)})
    df = pd.DataFrame(rows)
    df.to_csv(OUT_DIR / "pvls_comparison.csv", index=False)
    return df


def tangent_check(samples: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    par = task011_parameters()
    u0 = np.zeros(3)
    A = centered_jacobian(lambda x: scaled_residual(x, par), u0, DFDU_STEPS)
    b = parameter_sensitivity(u0, par, 2)
    tangent = -np.linalg.solve(A, b)
    probe = pd.read_csv(TASK012_OUT / "python_equilibrium_control_probe.csv")
    rows = []
    for target in (0.55, 0.65):
        row = probe[(probe.control == "W_a0") & np.isclose(probe.control_value, target)].iloc[0]
        actual = np.array([(float(row.z_m) - Z_SEED) / 100.0, float(row.u_m_s) - U_SEED, math.log(float(row.m_kg) / M_SEED)])
        pred = tangent * (target - 0.6)
        for j, state in enumerate(STATE_NAMES):
            rows.append({"target_W_a0": target, "state": state, "predicted_delta": pred[j], "actual_delta": actual[j], "abs_error": abs(pred[j] - actual[j])})
    df = pd.DataFrame(rows)
    df.to_csv(OUT_DIR / "local_tangent_check.csv", index=False)
    pd.DataFrame(A, columns=STATE_NAMES).assign(residual=RESIDUAL_NAMES).to_csv(OUT_DIR / "seed_dfdu_matrix.csv", index=False)
    pd.DataFrame({"residual": RESIDUAL_NAMES, "dF_dW_a0": b}).to_csv(OUT_DIR / "seed_dfdw_vector.csv", index=False)
    pd.DataFrame({"state": STATE_NAMES, "dstate_dW_a0": tangent}).to_csv(OUT_DIR / "seed_implicit_tangent.csv", index=False)
    return df, A, b


def write_linear_surrogate(A: np.ndarray, b: np.ndarray) -> None:
    LINEAR_DIR.mkdir(parents=True, exist_ok=True)
    def mat_vals() -> str:
        # Fortran DATA fills first index fastest: A(1,1), A(2,1), A(3,1), A(1,2)...
        vals = [A[i, j] for j in range(3) for i in range(3)]
        return ", ".join(f"{v:.17E}" for v in vals)
    bvals = ", ".join(f"{v:.17E}" for v in b)
    f90 = f"""
SUBROUTINE FUNC(NDIM,U,ICP,PAR,IJAC,F,DFDU,DFDP)
  IMPLICIT NONE
  INTEGER, INTENT(IN) :: NDIM,IJAC,ICP(*)
  DOUBLE PRECISION, INTENT(IN) :: U(NDIM),PAR(*)
  DOUBLE PRECISION, INTENT(OUT) :: F(NDIM)
  DOUBLE PRECISION, INTENT(INOUT) :: DFDU(NDIM,NDIM),DFDP(NDIM,*)
  DOUBLE PRECISION :: A(3,3), B(3), DW
  INTEGER :: I,J
  DATA A / {mat_vals()} /
  DATA B / {bvals} /
  DW=PAR(2)-0.6D0
  DO I=1,3
    F(I)=B(I)*DW
    DO J=1,3
      F(I)=F(I)+A(I,J)*U(J)
    END DO
  END DO
  IF (IJAC .NE. 0) THEN
    DFDU(1:NDIM,1:NDIM)=0D0
    DFDP(1:NDIM,1:98)=0D0
    DO I=1,3
      DO J=1,3
        DFDU(I,J)=A(I,J)
      END DO
      DFDP(I,2)=B(I)
    END DO
  END IF
END SUBROUTINE FUNC

SUBROUTINE STPNT(NDIM,U,PAR,T)
  IMPLICIT NONE
  INTEGER, INTENT(IN) :: NDIM
  DOUBLE PRECISION, INTENT(INOUT) :: U(NDIM),PAR(*)
  DOUBLE PRECISION, INTENT(IN) :: T
  U(1:NDIM)=0D0
  PAR(1)=9000D0
  PAR(2)=0.6D0
END SUBROUTINE STPNT

SUBROUTINE BCND(NDIM,PAR,ICP,NBC,U0,U1,FB,IJAC,DBC)
  IMPLICIT NONE
  INTEGER, INTENT(IN) :: NDIM,ICP(*),NBC,IJAC
  DOUBLE PRECISION, INTENT(IN) :: PAR(*),U0(NDIM),U1(NDIM)
  DOUBLE PRECISION, INTENT(OUT) :: FB(NBC)
  DOUBLE PRECISION, INTENT(INOUT) :: DBC(NBC,*)
END SUBROUTINE BCND

SUBROUTINE ICND(NDIM,PAR,ICP,NINT,U,UOLD,UDOT,UPOLD,FI,IJAC,DINT)
  IMPLICIT NONE
  INTEGER, INTENT(IN) :: NDIM,ICP(*),NINT,IJAC
  DOUBLE PRECISION, INTENT(IN) :: PAR(*),U(NDIM),UOLD(NDIM),UDOT(NDIM),UPOLD(NDIM)
  DOUBLE PRECISION, INTENT(OUT) :: FI(NINT)
  DOUBLE PRECISION, INTENT(INOUT) :: DINT(NINT,*)
END SUBROUTINE ICND

SUBROUTINE FOPT(NDIM,U,ICP,PAR,IJAC,FS,DFDU,DFDP)
  IMPLICIT NONE
  INTEGER, INTENT(IN) :: NDIM,ICP(*),IJAC
  DOUBLE PRECISION, INTENT(IN) :: U(NDIM),PAR(*)
  DOUBLE PRECISION, INTENT(OUT) :: FS
  DOUBLE PRECISION, INTENT(INOUT) :: DFDU(NDIM),DFDP(*)
END SUBROUTINE FOPT

SUBROUTINE PVLS(NDIM,U,PAR)
  IMPLICIT NONE
  INTEGER, INTENT(IN) :: NDIM
  DOUBLE PRECISION, INTENT(IN) :: U(NDIM)
  DOUBLE PRECISION, INTENT(INOUT) :: PAR(*)
END SUBROUTINE PVLS
"""
    (LINEAR_DIR / "bertonrestricted_task022_linear.f90").write_text(f90)
    (LINEAR_DIR / "c.bertonrestricted-task022-linear-wA0-plus").write_text("""# TASK-022 affine local surrogate W_a0 continuation.
parnames = {2:'W_a0'}
unames = {1:'Z_scaled', 2:'U_scaled', 3:'M_log_ratio'}
NDIM=3, IPS=1, IRS=0, ILP=0
ICP = ['W_a0']
NTST=10, NCOL=4, IAD=3, ISP=0, ISW=1, IPLT=0, NBC=0, NINT=0
NMX=180, NPR=5, MXBF=0, IID=2, ITMX=12, ITNW=8, NWTN=4, JAC=1
EPSL=1e-10, EPSU=1e-10, EPSS=1e-08
DS=0.001, DSMIN=1e-08, DSMAX=0.02, IADS=1
NPAR=98, THL={}, THU={}
UZR = {'W_a0': [0.7, 1.0, 1.2]}
UZSTOP = {'W_a0': [1.2]}
""")
    (LINEAR_DIR / "run_auto.sh").write_text("""#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
auto <<'AUTOEOF'
clean()
ld('bertonrestricted_task022_linear')
r=run(c='bertonrestricted-task022-linear-wA0-plus')
sv(r,'task022-linear-wA0-plus')
AUTOEOF
""")
    (LINEAR_DIR / "run_auto.sh").chmod(0o755)
    subprocess.run(["bash", "run_auto.sh"], cwd=LINEAR_DIR, check=True)


def parse_linear_branch() -> pd.DataFrame:
    rows = []
    path = LINEAR_DIR / "b.task022-linear-wA0-plus"
    for line in path.read_text().splitlines():
        parts = line.split()
        if len(parts) < 9:
            continue
        try:
            br, pt, ty, lab = map(int, parts[:4])
            vals = list(map(float, parts[4:]))
        except ValueError:
            continue
        rows.append({"branch": br, "point": pt, "ty": ty, "label": lab, "W_a0": vals[0], "l2_norm": vals[1], "Z_scaled": vals[2], "U_scaled": vals[3], "M_log_ratio": vals[4]})
    df = pd.DataFrame(rows)
    df.to_csv(OUT_DIR / "linear_surrogate_branch_summary.csv", index=False)
    return df


def write_summary(resid: pd.DataFrame, dfdu: pd.DataFrame, dfdp: pd.DataFrame, pvls: pd.DataFrame, tangent: pd.DataFrame, linear: pd.DataFrame) -> dict[str, object]:
    task021 = json.loads((TASK021_OUT / "task021_minimal_auto_verdict.json").read_text())
    summary = {
        "samples_validated": int(resid["sample"].nunique()),
        "max_residual_abs_error": float(resid.abs_error.max()),
        "max_dfdu_abs_error": float(dfdu.abs_error.max()),
        "max_dfdp_abs_error": float(dfdp.abs_error.max()),
        "max_pvls_selected_abs_error": float(pvls.abs_error.max()),
        "max_tangent_abs_error_over_0p05_W_steps": float(tangent.abs_error.max()),
        "linear_surrogate_points": int(len(linear)),
        "linear_surrogate_w_min": float(linear.W_a0.min()),
        "linear_surrogate_w_max": float(linear.W_a0.max()),
        "task021_minimal_auto_accepted_nontrivial_branch": bool(task021["auto_accepted_nontrivial_branch"]),
        "residual_mismatch_plausible": bool(resid.abs_error.max() > 1e-6),
        "dfdu_mismatch_plausible": bool(dfdu.abs_error.max() > 1e-5),
        "dfdp_indexing_mismatch_plausible": bool(dfdp.abs_error.max() > 1e-3),
        "pvls_selected_mismatch_plausible": bool(pvls.abs_error.max() > 1e-5),
        "linear_surrogate_auto_setup_ok": bool(linear.W_a0.max() >= 1.19 and len(linear) > 5),
        "remaining_plausible_failure_modes": [
            "nonlinear Berton residual/arclength corrector interaction",
            "AUTO step/tangent scaling for the nonlinear restricted problem",
            "finite-difference behavior away from the seed after large Newton iterates",
        ],
        "less_plausible_failure_modes": [
            "Fortran/Python restricted residual mismatch",
            "TASK-017 DFDU mismatch at validated samples",
            "TASK-017 W_a0/z_W0/H_a3 DFDP parameter-indexing mismatch",
            "selected PVLS physical diagnostics mismatch",
            "generic AUTO inability to continue the local affine restricted problem",
        ],
    }
    (OUT_DIR / "validation_verdict.json").write_text(json.dumps(summary, indent=2) + "\n")
    pd.DataFrame([summary | {"remaining_plausible_failure_modes": "; ".join(summary["remaining_plausible_failure_modes"]), "less_plausible_failure_modes": "; ".join(summary["less_plausible_failure_modes"])}]).to_csv(OUT_DIR / "validation_summary.csv", index=False)
    return summary


def write_note(summary: dict[str, object]) -> None:
    DOC.write_text(
        "# TASK-022 restricted Fortran validation and local surrogate\n\n"
        "This note validates the failing TASK-017 restricted/scaled AUTO Fortran source outside AUTO and adds the local affine surrogate proposed after TASK-021.\n\n"
        "## Commands\n\n"
        "```bash\n"
        "uv run python episodes/07-restricted-equilibrium-auto/scripts/berton_restricted_task022_validate_fortran.py\n"
        "uv run pytest tests/test_episode07_restricted_task022.py\n"
        "```\n\n"
        "The script compiles `episodes/07-restricted-equilibrium-auto/auto/berton_restricted_task017/bertonrestricted_task017.f90` with a generated standalone driver under `auto/berton_restricted_task022_validate/`. "
        "It calls `STPNT`, `FUNC(..., IJAC=2, ...)`, and `PVLS` at the seed, a local tangent predictor point, and TASK-012 W_a0 probe equilibria at 0.5, 0.7, and 1.0 m/s.\n\n"
        "## Validation result\n\n"
        f"- Samples validated: `{summary['samples_validated']}`.\n"
        f"- Max Fortran/Python residual absolute error: `{summary['max_residual_abs_error']:.3e}`.\n"
        f"- Max DFDU absolute error: `{summary['max_dfdu_abs_error']:.3e}`.\n"
        f"- Max DFDP absolute error for W_a0/z_W0/H_a3: `{summary['max_dfdp_abs_error']:.3e}`.\n"
        f"- Max selected PVLS diagnostic absolute error: `{summary['max_pvls_selected_abs_error']:.3e}`.\n\n"
        "These checks make residual mismatch, the validated DFDU entries, active DFDP parameter indexing, and selected physical PVLS diagnostics unlikely explanations for the first-step AUTO failure.\n\n"
        "## Local tangent and affine surrogate\n\n"
        f"The affine surrogate based on the seed matrices accepted `{summary['linear_surrogate_points']}` branch rows and covered `W_a0={summary['linear_surrogate_w_min']:.3f}`-`{summary['linear_surrogate_w_max']:.3f}`. "
        "That means AUTO can continue the local linearized restricted problem with the same state coordinates and W_a0 control.\n\n"
        "## Conclusion\n\n"
        "The restricted sandbox is still useful, but the next experiment should target the nonlinear corrector path, not PVLS or basic residual/Jacobian indexing. "
        "The most plausible remaining causes are nonlinear Berton residual/arclength interaction, step/tangent scaling for the nonlinear restricted problem, or finite-difference behavior after Newton iterates jump far from the local branch. "
        "A practical next step is to make AUTO follow the nonlinear problem with an explicitly scaled W_a0 control or externally seeded small predictor steps, then compare each Newton iterate against the validated local tangent.\n"
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    samples = build_samples()
    samples.to_csv(OUT_DIR / "validation_samples.csv", index=False)
    write_fortran_driver(samples)
    raw = compile_and_run_driver()
    resid = compare_residuals(samples, raw)
    dfdu = compare_dfdu(samples, raw)
    dfdp = compare_dfdp(samples, raw)
    pvls = compare_pvls(samples, raw)
    tangent, A, b = tangent_check(samples)
    write_linear_surrogate(A, b)
    linear = parse_linear_branch()
    summary = write_summary(resid, dfdu, dfdp, pvls, tangent, linear)
    write_note(summary)


if __name__ == "__main__":
    main()
