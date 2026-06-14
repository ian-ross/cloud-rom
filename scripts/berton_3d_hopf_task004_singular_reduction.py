"""TASK-004: singular-perturbation reduction of the corrected Berton 3D fixed point.

The corrected linearized system for perturbations (zeta, v, r) is

    zeta_dot = v
    v_dot    = -k * (v - F(zeta, r))
    r_dot    = g(zeta, r)

with

    F = -w*zeta - B*r,        B = 2*beta*r_star
    g = -d*zeta - c*r,
    c = (G/r_star) R_r,
    d = (G/r_star) (sigma_S + R_zeta).

This notation separates the k-free slow feedbacks w, B, c, d from the Task-001
short-hands a=k*w and b=k*B.  The full corrected Jacobian is

    [[0, 1, 0], [-k*w, -k, -k*B], [-d, 0, -c]].

The script derives the k -> infinity slow dynamics two ways:

Route A: asymptotic factorisation/slow-root expansion of the cubic after
         substituting k = 1/eps.
Route B: direct slow-fast reduction with the O(eps) inertial correction to the
         quasi-steady velocity v = F.

Both routes are printed and reconciled with explicit SymPy simplification checks.
"""

from __future__ import annotations

import sympy as sp


def banner(title: str) -> None:
    print("\n" + "=" * 96)
    print(title)
    print("=" * 96)


def show(label: str, expr: sp.Expr | sp.Matrix | list[sp.Expr]) -> None:
    print(f"\n{label}:")
    sp.pprint(expr, use_unicode=True)


def assert_zero(expr: sp.Expr, message: str) -> None:
    residual = sp.factor(sp.simplify(expr))
    if residual != 0:
        show("Assertion residual", residual)
        raise AssertionError(message)


def assert_matrix_zero(expr: sp.Matrix, message: str) -> None:
    residual = sp.simplify(expr)
    if residual != sp.zeros(*expr.shape):
        show("Matrix assertion residual", residual)
        raise AssertionError(message)


def symbols() -> dict[str, sp.Symbol]:
    eps = sp.symbols("eps", positive=True)
    lam = sp.symbols("lambda")
    mu0, mu1 = sp.symbols("mu0 mu1")
    # w is the positive/zero local descent of the updraft profile; B is V_f'(r*).
    w, B, c = sp.symbols("w B c", positive=True)
    d = sp.symbols("d", real=True)
    return {"eps": eps, "lambda": lam, "mu0": mu0, "mu1": mu1, "w": w, "B": B, "c": c, "d": d}


def route_a_cubic_expansion() -> dict[str, sp.Expr]:
    """Derive the slow quadratic and O(eps) slow-root correction from the cubic."""

    s = symbols()
    eps, lam, mu0, mu1, w, B, c, d = (s[name] for name in ("eps", "lambda", "mu0", "mu1", "w", "B", "c", "d"))

    banner("Route A: substitute k=1/eps in the corrected cubic")
    # Task-001: a2=k+c, a1=k(c+w), a0=k(w*c - B*d).
    P_lambda = lam**3 + (1 / eps + c) * lam**2 + (1 / eps) * (c + w) * lam + (1 / eps) * (w * c - B * d)
    P_slow_scaled = sp.factor(eps * P_lambda)
    show("eps * P(lambda) for slow lambda=O(1)", P_slow_scaled)

    q0 = lam**2 + (w + c) * lam + (w * c - B * d)
    q1 = lam**3 + c * lam**2
    show("O(1) reduced slow quadratic q0(lambda)", q0)
    show("O(eps) cubic residue q1(lambda)", q1)
    assert_zero(P_slow_scaled - (q0 + eps * q1), "Scaled cubic did not split into q0 + eps*q1.")

    slow_roots_0 = sp.solve(q0, lam)
    show("Leading slow eigenvalues from Route A", slow_roots_0)
    trace0 = -(w + c)
    det0 = w * c - B * d
    discriminant0 = sp.factor((w - c) ** 2 + 4 * B * d)
    omega0_squared = sp.factor(det0 - (w + c) ** 2 / 4)
    show("Leading 2D trace", trace0)
    show("Leading 2D determinant", det0)
    show("Leading discriminant Delta = (w-c)^2 + 4*B*d", discriminant0)
    show("If Delta < 0, slow-pair omega_0^2 = det - trace^2/4", omega0_squared)

    banner("Route A: slow-root series lambda = mu0 + eps*mu1 + O(eps^2)")
    lam_series = mu0 + eps * mu1
    series_expr = sp.series(P_slow_scaled.subs(lam, lam_series), eps, 0, 2).removeO().expand()
    order0 = sp.factor(series_expr.coeff(eps, 0))
    order1 = sp.factor(series_expr.coeff(eps, 1))
    show("Collected O(1) equation", order0)
    show("Collected O(eps) equation", order1)
    assert_zero(order0 - q0.subs(lam, mu0), "Route A O(1) equation is not q0(mu0).")
    q0_prime = sp.diff(q0, lam).subs(lam, mu0)
    q1_mu0 = q1.subs(lam, mu0)
    mu1_from_cubic = sp.factor(-q1_mu0 / q0_prime)
    show("mu1 from O(eps): -q1(mu0)/q0'(mu0)", mu1_from_cubic)
    assert_zero(order1 - (mu1 * q0_prime + q1_mu0), "Route A O(eps) equation has unexpected form.")

    return {
        "P_slow_scaled": P_slow_scaled,
        "q0": q0,
        "q1": q1,
        "trace0": trace0,
        "det0": det0,
        "discriminant0": discriminant0,
        "omega0_squared": omega0_squared,
        "slow_roots_0": slow_roots_0,
        "order0": order0,
        "order1": order1,
        "q0_prime_mu0": q0_prime,
        "mu1_from_cubic": mu1_from_cubic,
    }


def route_b_slow_fast_reduction() -> dict[str, sp.Expr | sp.Matrix]:
    """Derive the direct slow-fast reduction including O(eps) inertial correction."""

    s = symbols()
    eps, lam, w, B, c, d = (s[name] for name in ("eps", "lambda", "w", "B", "c", "d"))
    zeta, r = sp.symbols("zeta r")

    banner("Route B: Tikhonov/Fenichel slow-fast reduction with O(eps) inertia")
    F = -w * zeta - B * r
    g = -d * zeta - c * r
    DF = sp.Matrix([[sp.diff(F, zeta), sp.diff(F, r)]])
    slow0 = sp.Matrix([F, g])
    h1 = -sp.factor((DF * slow0)[0])
    v_slow = sp.factor(F + eps * h1)
    show("Fast equation in standard form: eps*v_dot = F(zeta,r) - v", sp.Eq(eps * sp.Symbol("v_dot"), F - sp.Symbol("v")))
    show("Quasi-steady velocity F", F)
    show("Growth equation g", g)
    show("D F", DF)
    show("Invariance correction h1 = -D F dot [F, g]", h1)
    show("Slow manifold velocity v = F + eps*h1 + O(eps^2)", v_slow)

    M0 = sp.Matrix([[-w, -B], [-d, -c]])
    M1 = sp.Matrix([[sp.diff(h1, zeta), sp.diff(h1, r)], [0, 0]])
    M_eps = sp.simplify(M0 + eps * M1)
    show("Leading bare 2D matrix M0", M0)
    show("O(eps) inertial-correction matrix M1", M1)
    show("Corrected slow matrix M0 + eps*M1", M_eps)

    char_B_exact = sp.factor((lam * sp.eye(2) - M_eps).det())
    char_B_series = sp.series(char_B_exact, eps, 0, 2).removeO().expand()
    q0_B = sp.factor(char_B_series.coeff(eps, 0))
    q1_B = sp.factor(char_B_series.coeff(eps, 1))
    show("Route B characteristic through O(eps)", char_B_series)
    show("Route B O(1) quadratic", q0_B)
    show("Route B O(eps) correction", q1_B)

    return {
        "F": F,
        "g": g,
        "h1": h1,
        "M0": M0,
        "M1": M1,
        "M_eps": M_eps,
        "char_B_series": char_B_series,
        "q0_B": q0_B,
        "q1_B": q1_B,
    }


def reconcile_routes(route_a: dict[str, sp.Expr], route_b: dict[str, sp.Expr | sp.Matrix]) -> dict[str, sp.Expr]:
    """Prove Route A and Route B agree for slow eigenvalues through O(eps)."""

    s = symbols()
    lam, mu0, w, B, c, d = (s[name] for name in ("lambda", "mu0", "w", "B", "c", "d"))

    banner("Reconcile Route A and Route B")
    q0_A = sp.Poly(route_a["q0"], lam).as_expr()
    q0_B = sp.Poly(route_b["q0_B"], lam).as_expr()
    show("simplify(q0_A - q0_B)", sp.simplify(q0_A - q0_B))
    assert_zero(q0_A - q0_B, "Route A and Route B leading slow quadratics disagree.")

    # Route A q1=lambda^3+c*lambda^2; Route B q1 is an equivalent O(eps)
    # correction only on roots of q0.  Reduce their difference modulo q0.
    q1_A = route_a["q1"]
    q1_B = sp.Poly(route_b["q1_B"], lam).as_expr()
    remainder = sp.factor(sp.rem(sp.Poly(q1_A - q1_B, lam), sp.Poly(q0_A, lam)).as_expr())
    show("q1_A - q1_B", sp.factor(q1_A - q1_B))
    show("remainder of (q1_A - q1_B) modulo q0", remainder)
    assert_zero(remainder, "Route A and Route B O(eps) corrections differ on the slow eigenspace.")

    # Make the eigenvalue-correction equality explicit: substitute a symbolic
    # slow root mu0 satisfying q0(mu0)=0 and reduce the difference to zero.
    q0_mu0 = q0_A.subs(lam, mu0)
    q0_prime_mu0 = sp.diff(q0_A, lam).subs(lam, mu0)
    mu1_A = route_a["mu1_from_cubic"]
    q1_B_mu0 = q1_B.subs(lam, mu0)
    mu1_B = sp.factor(-q1_B_mu0 / q0_prime_mu0)
    mu1_diff_numer = sp.factor(sp.together(mu1_A - mu1_B).as_numer_denom()[0])
    mu1_diff_remainder = sp.factor(sp.rem(sp.Poly(mu1_diff_numer, mu0), sp.Poly(q0_mu0, mu0)).as_expr())
    show("mu1 from Route A", mu1_A)
    show("mu1 from Route B", mu1_B)
    show("remainder of numerator(mu1_A - mu1_B) modulo q0(mu0)", mu1_diff_remainder)
    assert_zero(mu1_diff_remainder, "Route A and Route B slow eigenvalue corrections disagree.")

    # k-independence: the leading slow quadratic contains only w,B,c,d, not k/eps.
    free_symbols_q0 = q0_A.free_symbols
    eps = s["eps"]
    k = sp.symbols("k")
    residual_k_symbols = free_symbols_q0 & {eps, k}
    show("Free symbols in leading slow quadratic", sorted(str(x) for x in free_symbols_q0))
    show("Residual k/eps symbols in leading slow quadratic", sorted(str(x) for x in residual_k_symbols))
    if residual_k_symbols:
        raise AssertionError("Leading slow pair has residual k/eps dependence.")

    return {
        "q0_difference": sp.simplify(q0_A - q0_B),
        "q1_remainder": remainder,
        "mu1_B": mu1_B,
        "mu1_diff_remainder": mu1_diff_remainder,
    }


def berton_eq119_frequency_check(route_a: dict[str, sp.Expr]) -> dict[str, sp.Expr]:
    """Print the k-free oscillatory frequency structure and compare to Eq. 119."""

    s = symbols()
    w, B, c, d = (s[name] for name in ("w", "B", "c", "d"))
    beta, G, r_star, sigma_S, R_zeta, R_r = sp.symbols(
        "beta G r_star sigma_S R_zeta R_r", positive=True
    )
    # R_zeta can have either sign; override the assumption generated above.
    R_zeta = sp.symbols("R_zeta", real=True)

    banner("Berton Eq. (119) frequency-structure check")
    omega0_squared = route_a["omega0_squared"]
    primitive_subs = {B: 2 * beta * r_star, c: G * R_r / r_star, d: G * (sigma_S + R_zeta) / r_star}
    omega_primitive = sp.factor(omega0_squared.subs(primitive_subs))
    zero_updraft_shear = sp.factor(omega_primitive.subs(w, 0))
    leading_if_c_small = sp.factor((-B * d).subs(primitive_subs))
    show("omega_0^2 = det - trace^2/4", omega0_squared)
    show("omega_0^2 in primitive Berton gradients", omega_primitive)
    show("For locally flat updraft (w=0), omega_0^2", zero_updraft_shear)
    show("Dominant Berton Eq. (119)-like product -B*d", leading_if_c_small)
    print(
        "\nInterpretation: for an oscillatory slow pair, the leading frequency is k-free. "
        "The dominant term -B*d = -2*beta*G*(sigma_S + R_zeta) has the expected "
        "fall-speed-gradient times microphysical growth times supersaturation/radiative-gradient structure; "
        "r_star and k cancel from that product."
    )
    for expr_name, expr in {
        "omega_0^2": omega0_squared,
        "primitive omega_0^2": omega_primitive,
        "dominant -B*d": leading_if_c_small,
    }.items():
        if any(str(sym) in {"k", "eps"} for sym in expr.free_symbols):
            raise AssertionError(f"{expr_name} contains spurious k/eps dependence: {expr.free_symbols}")

    return {
        "omega_primitive": omega_primitive,
        "omega_w0": zero_updraft_shear,
        "dominant_eq119_like": leading_if_c_small,
    }


def derive_task004() -> dict[str, object]:
    route_a = route_a_cubic_expansion()
    route_b = route_b_slow_fast_reduction()
    reconciliation = reconcile_routes(route_a, route_b)
    frequency = berton_eq119_frequency_check(route_a)
    banner("TASK-004 singular perturbation reduction complete")
    print("All TASK-004 symbolic assertions passed.")
    return {"route_a": route_a, "route_b": route_b, "reconciliation": reconciliation, "frequency": frequency}


if __name__ == "__main__":
    derive_task004()
