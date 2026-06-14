"""TASK-005: classify the corrected Berton reduced 3D baseline fixed point.

This script intentionally does not introduce new dynamics.  It consolidates the
audited evidence from TASK-001 through TASK-004:

* corrected Jacobian and cubic coefficients,
* derived signs of the radiative/supersaturation-gradient combination,
* numerical root tracking across drag rate,
* k -> infinity slow-pair reduction.

The output is a plain-language classification of the baseline reduced fixed
point as either a corrected-Jacobian saddle or Hopf-capable stable spiral.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import sympy as sp

from berton_3d_hopf_task003_root_tracking import K_SWEEP, RootRow, SlowParameters, derive_slow_parameters, track_roots


@dataclass(frozen=True)
class Classification:
    verdict: str
    sigma_plus_Rzeta: float
    d: float
    determinant_2d: float
    a0_at_model_k: float
    rh_residual_at_model_k: float
    max_root_real_by_k: tuple[tuple[float, float], ...]
    all_swept_roots_stable: bool
    corrected_det_expr: sp.Expr
    briefing_det_expr: sp.Expr
    briefing_det_residual: sp.Expr
    hopf_locus_residual_expr: sp.Expr
    omega0_squared_expr: sp.Expr
    eq119_like_expr: sp.Expr


def banner(title: str) -> None:
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)


def show(label: str, expr: sp.Expr) -> None:
    print(f"\n{label}:")
    sp.pprint(expr, use_unicode=True)


def symbolic_relations() -> dict[str, sp.Expr]:
    """Return the corrected symbolic relations used for classification."""

    k, beta, G, r_star, w, R_r, sigma_S, R_zeta, c, d = sp.symbols(
        "k beta G r_star w R_r sigma_S R_zeta c d", positive=True
    )
    # R_zeta and d may have either sign; re-declare them as real and rebuild.
    R_zeta = sp.symbols("R_zeta", real=True)
    d = sp.symbols("d", real=True)
    B = sp.symbols("B", positive=True)

    a = k * w
    bcoef = k * B
    a2 = k + c
    a1 = k * c + a
    a0 = a * c - bcoef * d
    det_2d = sp.factor(a0 / k)
    rh_residual = sp.factor(a2 * a1 - a0)
    hopf_locus_residual = sp.factor(k * (k * c + a + c**2) + bcoef * d)

    primitive_subs = {B: 2 * beta * r_star, c: G * R_r / r_star, d: G * (sigma_S + R_zeta) / r_star}
    corrected_det_primitive = sp.factor(det_2d.subs(primitive_subs))
    briefing_det_candidate = sp.factor((G / r_star) * (w * R_r - 2 * beta * r_star**2 * (sigma_S + R_zeta)))
    briefing_det_residual = sp.factor(corrected_det_primitive - briefing_det_candidate)

    omega0_squared = sp.factor(det_2d - (w + c) ** 2 / 4)
    eq119_like = sp.factor((-B * d).subs(primitive_subs))

    return {
        "a": a,
        "b": bcoef,
        "a2": a2,
        "a1": a1,
        "a0": a0,
        "det_2d": det_2d,
        "rh_residual": rh_residual,
        "hopf_locus_residual": hopf_locus_residual,
        "corrected_det_primitive": corrected_det_primitive,
        "briefing_det_candidate": briefing_det_candidate,
        "briefing_det_residual": briefing_det_residual,
        "omega0_squared": omega0_squared,
        "eq119_like": eq119_like,
    }


def coefficients_at(k_per_s: float, params: SlowParameters) -> tuple[float, float, float, float]:
    """Return a0, 2D determinant a0/k, and Routh-Hurwitz residual at k."""

    a = k_per_s * params.w_prime_per_s
    bcoef = 2.0 * k_per_s * params.beta_per_m_s * params.r_star_m
    c = params.c_per_s
    d = params.d_per_s_per_m
    a2 = k_per_s + c
    a1 = k_per_s * c + a
    a0 = a * c - bcoef * d
    rh_residual = a2 * a1 - a0
    return a0, a0 / k_per_s, rh_residual, a1


def classify(params: SlowParameters | None = None, rows: list[RootRow] | None = None) -> Classification:
    """Classify the baseline using derived signs and corrected root evidence."""

    if params is None:
        params = derive_slow_parameters()
    if rows is None:
        rows = track_roots(params)

    relations = symbolic_relations()
    sigma_plus = params.sigma_S_per_m + params.R_zeta_per_m
    a0_model, det_2d, rh_model, _a1_model = coefficients_at(params.model_k_per_s, params)
    max_root_real_by_k = tuple((row.k_per_s, float(max(root.real for root in row.roots))) for row in rows)
    all_swept_roots_stable = all(row.a0 > 0.0 and max(root.real for root in row.roots) < 0.0 for row in rows)

    if a0_model < 0.0:
        verdict = "SADDLE: corrected a0<0 implies one positive real eigenvalue."
    elif all_swept_roots_stable:
        verdict = "HOPF-CAPABLE STABLE SPIRAL: corrected a0>0 and swept roots are stable complex slow pairs."
    else:
        verdict = "AMBIGUOUS/UNSTABLE: a0>=0 but root evidence is not uniformly stable."

    return Classification(
        verdict=verdict,
        sigma_plus_Rzeta=sigma_plus,
        d=params.d_per_s_per_m,
        determinant_2d=det_2d,
        a0_at_model_k=a0_model,
        rh_residual_at_model_k=rh_model,
        max_root_real_by_k=max_root_real_by_k,
        all_swept_roots_stable=all_swept_roots_stable,
        corrected_det_expr=relations["corrected_det_primitive"],
        briefing_det_expr=relations["briefing_det_candidate"],
        briefing_det_residual=relations["briefing_det_residual"],
        hopf_locus_residual_expr=relations["hopf_locus_residual"],
        omega0_squared_expr=relations["omega0_squared"],
        eq119_like_expr=relations["eq119_like"],
    )


def print_classification(classification: Classification, params: SlowParameters, rows: list[RootRow]) -> None:
    banner("TASK-005 corrected baseline classification")
    print(classification.verdict)

    banner("Corrected polynomial, determinant, and Hopf locus")
    print("Corrected cubic: lambda^3 + a2 lambda^2 + a1 lambda + a0")
    print("with a=k*w, b=k*B=2*k*beta*r*, c=(G/r*)R_r, d=(G/r*)(sigma_S+R_zeta)")
    print("a2 = k + c")
    print("a1 = k*c + a")
    print("a0 = a*c - b*d")
    print("Corrected Routh-Hurwitz Hopf locus: a2*a1 = a0")
    show("Equivalent residual, zero on Hopf locus: k*(k*c + a + c^2) + b*d", classification.hopf_locus_residual_expr)
    show("Corrected primitive 2D determinant a0/k", classification.corrected_det_expr)
    show("Briefing expanded determinant candidate", classification.briefing_det_expr)
    show("Residual: corrected determinant - briefing candidate", classification.briefing_det_residual)
    if classification.briefing_det_residual != 0:
        print("DISCREPANCY SURFACED: SymPy/TASK-001 give one fewer power of r_star than the briefing's expanded determinant candidate.")

    banner("Baseline signs and numerical classification")
    print(f"z*                         = {params.z_star_m:.12f} m")
    print(f"r*                         = {params.r_star_m:.12e} m")
    print(f"sigma_S                    = {params.sigma_S_per_m:.12e} m^-1")
    print(f"R_zeta                     = {params.R_zeta_per_m:.12e} m^-1")
    print(f"sigma_S + R_zeta           = {classification.sigma_plus_Rzeta:.12e} m^-1")
    print(f"d                          = {classification.d:.12e} s^-1 m^-1")
    print(f"2D determinant a0/k         = {classification.determinant_2d:.12e}")
    print(f"a0 at model k={params.model_k_per_s:.6g} = {classification.a0_at_model_k:.12e}")
    print(f"RH residual a2*a1-a0        = {classification.rh_residual_at_model_k:.12e}")
    print("Root-tracking max real parts:")
    for k_per_s, max_real in classification.max_root_real_by_k:
        print(f"- k={k_per_s:10.3g} s^-1: max Re(lambda) = {max_real:+.12e}")

    if classification.a0_at_model_k > 0.0 and classification.all_swept_roots_stable:
        print("\nInterpretation: the derived negative sigma_S+R_zeta makes d<0.  Because b>0, the corrected -b*d term raises a0 above zero instead of forcing a saddle.")
        print("The fixed slow parameters are stable over the swept k values, so this is Hopf-capable sign structure rather than a saddle.")
    elif classification.a0_at_model_k < 0.0:
        print("\nInterpretation: a0<0 would force a real positive eigenvalue, giving a saddle and excluding Hopf at this fixed point.")

    banner("Oscillatory direction and Eq. (119)-style frequency")
    show("Slow-pair omega0^2 = det - trace^2/4", classification.omega0_squared_expr)
    show("Dominant Eq. (119)-like term -B*d", classification.eq119_like_expr)
    print("For this Hopf-capable baseline, destabilisation toward the Hopf locus means reducing the positive RH residual a2*a1-a0 to zero.")
    print("In the corrected formulas this is driven by making b*d more negative in k*(k*c+a+c^2)+b*d, i.e. stronger negative d=(G/r*)(sigma_S+R_zeta), larger fall-speed slope B, or other feedbacks that reduce damping.")
    print("Qualitatively, the Berton 10 km -> 9 km updraft-base transition would need to move the operating point toward this zero-residual surface; in this frozen-k reduced model that means strengthening the negative radiative/supersaturation-gradient feedback enough for the slow complex pair to cross.")
    print("If instead sigma_S+R_zeta became positive, d would become positive, -b*d would lower a0, and the corrected system could become a saddle.  Omitted feedbacks such as Reynolds-dependent drag-rate variation, nonlocal trajectory effects, or changes in crystal habit/geometry could alter this reduced verdict.")


def run_task005() -> tuple[SlowParameters, list[RootRow], Classification]:
    params = derive_slow_parameters()
    rows = track_roots(params, K_SWEEP)
    classification = classify(params, rows)
    print_classification(classification, params, rows)
    return params, rows, classification


if __name__ == "__main__":
    run_task005()
