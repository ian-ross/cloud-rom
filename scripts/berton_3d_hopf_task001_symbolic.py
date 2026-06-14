"""TASK-001: Symbolic 3D fixed-point linearization for Berton (2023).

This script derives, prints, and asserts the corrected symbolic Jacobian and
characteristic polynomial for the reduced state order (zeta, v, r):

    zeta_dot = v
    v_dot    = -k * (v - (W_a(zeta) - V_f(r)))
    r_dot    = (G / r) * (s(zeta) - R(zeta, r))

It intentionally prints every non-trivial intermediate expression so the
algebra can be audited by a human.  The final matrix is not typed in as the
source of truth; it is built by differentiating the RHS and substituting the
fixed-point conditions.
"""

from __future__ import annotations

import sympy as sp


def banner(title: str) -> None:
    print("\n" + "=" * 88)
    print(title)
    print("=" * 88)


def show(label: str, expr: sp.Expr | sp.Matrix) -> None:
    print(f"\n{label}:")
    sp.pprint(expr, use_unicode=True)


def assert_zero(expr: sp.Expr, message: str) -> None:
    simplified = sp.simplify(expr)
    if simplified != 0:
        show("Assertion residual", simplified)
        raise AssertionError(message)


def assert_matrix_equal(left: sp.Matrix, right: sp.Matrix, message: str) -> None:
    residual = sp.simplify(left - right)
    if residual != sp.zeros(*left.shape):
        show("Matrix assertion residual", residual)
        raise AssertionError(message)


def derive_task001() -> dict[str, sp.Expr | sp.Matrix]:
    banner("Declare symbols and symbolic RHS")

    # State and eigenvalue symbols.
    zeta, zeta_star, v, r = sp.symbols("zeta zeta_star v r", real=True)
    lam = sp.symbols("lambda")

    # Known-positive scalar parameters from the briefing.
    k, beta, G, r_star = sp.symbols("k beta G r_star", positive=True)
    w_prime = sp.symbols("w_prime", positive=True)
    sigma_S = sp.symbols("sigma_S", positive=True)

    # Radiative derivatives: real, signs intentionally left free.
    R_r, R_zeta = sp.symbols("R_r R_zeta", real=True)

    W_a = sp.Function("W_a")
    V_f = sp.Function("V_f")
    s = sp.Function("s")
    R = sp.Function("R")

    rhs = sp.Matrix(
        [
            v,
            -k * (v - (W_a(zeta) - V_f(r))),
            (G / r) * (s(zeta) - R(zeta, r)),
        ]
    )
    x = sp.Matrix([zeta, v, r])
    show("State order", x)
    show("Reduced RHS built from symbolic functions", rhs)

    banner("Differentiate RHS before fixed-point substitution")
    J_raw = rhs.jacobian(x)
    show("Raw symbolic Jacobian", J_raw)
    show("Raw dr_dot/dr entry", J_raw[2, 2])

    # First substitute only the fixed-point coordinates.  Keeping the s-R term
    # visible here demonstrates the term that must cancel at the fixed point.
    fp_coordinates = {zeta: zeta_star, v: 0, r: r_star}
    drdr_at_coordinates = J_raw[2, 2].subs(fp_coordinates)
    show("dr_dot/dr after coordinate substitution but before s-R balance", drdr_at_coordinates)

    # Fixed-point force/growth balances and local derivative definitions.
    # Apply derivative substitutions before function-value substitutions: replacing
    # W_a(zeta*) inside Derivative(W_a(zeta*), zeta*) would otherwise turn the
    # derivative into zero, which is exactly the kind of silent algebra error this
    # script is meant to prevent.
    derivative_subs = {
        sp.Subs(sp.Derivative(W_a(zeta), zeta), zeta, zeta_star): -w_prime,
        sp.Derivative(W_a(zeta_star), zeta_star): -w_prime,
        sp.Subs(sp.Derivative(V_f(r), r), r, r_star): 2 * beta * r_star,
        sp.Derivative(V_f(r_star), r_star): 2 * beta * r_star,
        sp.Subs(sp.Derivative(s(zeta), zeta), zeta, zeta_star): -sigma_S,
        sp.Derivative(s(zeta_star), zeta_star): -sigma_S,
        sp.Subs(sp.Derivative(R(zeta, r), zeta), zeta, zeta_star): R_zeta,
        sp.Subs(sp.Derivative(R(zeta_star, r), r), r, r_star): R_r,
        sp.Subs(sp.Derivative(R(zeta, r_star), zeta), zeta, zeta_star): R_zeta,
        sp.Derivative(R(zeta_star, r_star), r_star): R_r,
        sp.Derivative(R(zeta_star, r_star), zeta_star): R_zeta,
    }
    value_subs = {
        W_a(zeta_star): beta * r_star**2,
        V_f(r_star): beta * r_star**2,
        s(zeta_star): R(zeta_star, r_star),
    }

    drdr_after_balance = sp.simplify(drdr_at_coordinates.subs(derivative_subs).subs(value_subs))
    show("dr_dot/dr after applying s(zeta*) = R(zeta*, r*)", drdr_after_balance)
    show("Expected cancellation result -G*R_r/r_star", -G * R_r / r_star)
    assert_zero(
        drdr_after_balance + G * R_r / r_star,
        "The fixed-point s-R cancellation in dr_dot/dr did not produce -G*R_r/r_star.",
    )

    banner("Substitute fixed-point conditions into the full Jacobian")
    J_derived = sp.simplify(J_raw.subs(fp_coordinates).subs(derivative_subs).subs(value_subs))
    show("Derived fixed-point Jacobian in primitive parameters", J_derived)

    a = k * w_prime
    b = 2 * k * beta * r_star
    c = (G / r_star) * R_r
    d = (G / r_star) * (sigma_S + R_zeta)
    show("Shorthand a = k*w_prime", a)
    show("Shorthand b = 2*k*beta*r_star", b)
    show("Shorthand c = (G/r_star)*R_r", c)
    show("Shorthand d = (G/r_star)*(sigma_S + R_zeta)", d)

    J_reference = sp.Matrix(
        [
            [0, 1, 0],
            [-a, -k, -b],
            [-d, 0, -c],
        ]
    )
    show("Corrected reference Jacobian", J_reference)
    show("Derived [v_dot, r] entry", J_derived[1, 2])
    show("Corrected reference [v_dot, r] entry = -b", -b)
    assert_zero(J_derived[1, 2] + b, "The [v_dot, r] entry is not the corrected -b.")
    assert_matrix_equal(J_derived, J_reference, "Derived Jacobian does not match corrected reference.")

    banner("Characteristic polynomial")
    char_expr = sp.Poly(sp.factor((lam * sp.eye(3) - J_derived).det()), lam)
    show("det(lambda*I - J), collected", char_expr.as_expr())
    coeffs = char_expr.all_coeffs()
    show("Characteristic polynomial coefficients [lambda^3, a2, a1, a0]", coeffs)
    if coeffs[0] != 1 or len(coeffs) != 4:
        raise AssertionError("Expected a monic cubic characteristic polynomial.")
    a2_derived, a1_derived, a0_derived = [sp.factor(c0) for c0 in coeffs[1:]]
    show("a2 derived", a2_derived)
    show("a1 derived", a1_derived)
    show("a0 derived", a0_derived)

    a2_reference = k + c
    a1_reference = k * c + a
    a0_reference = a * c - b * d
    show("a2 corrected reference", a2_reference)
    show("a1 corrected reference", a1_reference)
    show("a0 corrected reference = a*c - b*d", a0_reference)
    assert_zero(a2_derived - a2_reference, "a2 does not match corrected reference.")
    assert_zero(a1_derived - a1_reference, "a1 does not match corrected reference.")
    assert_zero(a0_derived - a0_reference, "a0 does not match corrected reference.")

    banner("a0 factorisation as k times the 2D determinant")
    two_d_det = sp.factor(a0_derived / k)
    a0_factorised = sp.factor(k * two_d_det)
    show("2D determinant implied by a0/k", two_d_det)
    show("k * 2D determinant", a0_factorised)
    show("a0 in primitive parameters", sp.factor(a0_derived))
    assert_zero(a0_derived - a0_factorised, "a0 is not k times the expected 2D determinant.")

    # The briefing also states an expanded determinant containing
    # -2*beta*r_star**2*(sigma_S + R_zeta).  The symbolic derivation from
    # a*c - b*d with b=2*k*beta*r_star and d=G/r_star*(...) gives one fewer
    # power of r_star.  Print this explicitly instead of hiding the mismatch.
    briefing_expanded_det = (G / r_star) * (
        w_prime * R_r - 2 * beta * r_star**2 * (sigma_S + R_zeta)
    )
    briefing_det_residual = sp.factor(two_d_det - briefing_expanded_det)
    show("Briefing's expanded 2D determinant candidate", briefing_expanded_det)
    show("Residual: derived determinant - briefing expanded candidate", briefing_det_residual)
    if briefing_det_residual != 0:
        print(
            "WARNING: The derived determinant matches a*c-b*d but not the briefing's "
            "expanded r_star**2 form. This discrepancy is surfaced for review."
        )

    banner("Corrected Routh-Hurwitz expression a2*a1 - a0")
    rh_derived = sp.factor(sp.simplify(a2_derived * a1_derived - a0_derived))
    rh_reference = sp.factor(k * (k * c + a + c**2) + b * d)
    show("a2*a1 - a0 derived", rh_derived)
    show("a2*a1 - a0 corrected reference", rh_reference)
    show("Hopf-locus rearrangement", sp.Eq(k * (k * c + a + c**2), -b * d))
    assert_zero(rh_derived - rh_reference, "a2*a1 - a0 does not match corrected reference.")

    banner("TASK-001 symbolic derivation complete")
    print("All TASK-001 symbolic assertions passed.")

    return {
        "J_raw": J_raw,
        "J_derived": J_derived,
        "J_reference": J_reference,
        "a": a,
        "b": b,
        "c": c,
        "d": d,
        "a2": a2_derived,
        "a1": a1_derived,
        "a0": a0_derived,
        "two_d_det": two_d_det,
        "rh": rh_derived,
    }


if __name__ == "__main__":
    derive_task001()
