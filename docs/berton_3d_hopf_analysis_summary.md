# Berton reduced 3D fixed point: Hopf-capable spiral vs saddle

## Executive verdict

For the corrected reduced 3D Berton fixed point analyzed here, the baseline is a **Hopf-capable stable spiral**, not a corrected-Jacobian saddle.

The controlling sign is

```text
sigma_S + R_zeta = -5.640219674712e-05 m^-1 < 0
```

so

```text
d = (G / r*) * (sigma_S + R_zeta) = -3.073061242928e-12 s^-1 m^-1 < 0.
```

Because `b > 0`, the corrected term `-b*d` is positive and raises `a0` above zero.  Root tracking then finds one fast stable real root and a stable slow complex pair over the tested drag-rate sweep.

## Reduced system and corrected Jacobian

The reduced variables are `(zeta, v, r)`:

```text
zeta_dot = v
v_dot    = -k * (v - (W_a(zeta) - V_f(r)))
r_dot    = (G / r) * (s(zeta) - R(zeta, r))
```

At the fixed point,

```text
v* = 0
W_a(zeta*) = V_f(r*) = beta * r*^2
s(zeta*) = R(zeta*, r*)
```

Define

```text
a = k * w
b = 2 * k * beta * r*
c = (G / r*) * R_r
d = (G / r*) * (sigma_S + R_zeta)
```

where `w = -dW_a/dzeta` at the fixed point.  The corrected symbolic Jacobian is

```text
J = [[ 0,   1,   0 ],
     [-a,  -k,  -b ],
     [-d,   0,  -c ]]
```

The important correction is the `-b` entry in the `v_dot`/`r` position:

```text
d(v_dot)/dr = -k * dV_f/dr = -2*k*beta*r* = -b.
```

## Characteristic polynomial and determinant factorization

For

```text
det(lambda I - J) = lambda^3 + a2*lambda^2 + a1*lambda + a0
```

SymPy gives

```text
a2 = k + c
a1 = k*c + a
a0 = a*c - b*d
```

The constant term factors as `k` times the determinant of the slaved 2D slow system:

```text
a0 / k = w*c - B*d,    B = 2*beta*r*
```

or, in primitive gradients,

```text
a0 / k = (G / r*) * (w*R_r - 2*beta*r* * (sigma_S + R_zeta)).
```

This is the determinant relation used for the Hopf-versus-saddle sign test.  The audited SymPy derivation also surfaced a discrepancy with the original briefing text: the briefing's expanded determinant candidate contains `r*^2` in the second term, while the symbolic derivation has one fewer power of `r*`.

The corrected Routh-Hurwitz Hopf condition is

```text
a2*a1 = a0
```

which is equivalent to

```text
k*(k*c + a + c^2) = -b*d
```

or, as a zero residual,

```text
k*(k*c + a + c^2) + b*d = 0.
```

## Radiative-gradient and supersaturation-gradient signs

Using the Berton Case-0 atmospheric profiles and the reduced radiative form

```text
R(z, r) = Phi(T(z)) * (eta_a(z) - 1) * r,
```

the baseline fixed point from the local reduced growth balance is

```text
z* = 9618.062976835217 m
r* = 6.550000000000e-05 m
eta_a(z*) = 1.023612595367
S_i(z*) - 1 = 2.207334580735e-03
R(z*, r*) = 2.207334580997e-03
```

The derived gradient values are

```text
sigma_S  = -7.507991401046e-05 m^-1
R_r      =  3.369976459537e+01 m^-1
R_zeta   =  1.867771726333e-05 m^-1
```

Therefore

```text
R_zeta > 0
sigma_S + R_zeta = -5.640219674712e-05 m^-1 < 0
d = -3.073061242928e-12 s^-1 m^-1 < 0
```

This negative `sigma_S + R_zeta` is the decisive difference from the saddle scenario assumed in the corrected hand-analysis branch where `sigma_S + R_zeta > 0`.

## Numerical root tracking

Holding the slow physical parameters fixed and sweeping `k`, the corrected cubic roots are:

| k [s^-1] | a2 | a1 | a0 | root 1 | root 2 | root 3 | diagnosis |
|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 1.00000184e+00 | 1.83612424e-06 | 5.63003586e-08 | -1.000000e+00+0.000000e+00j | -8.899119e-07-2.372753e-04j | -8.899119e-07+2.372753e-04j | stable; Hopf-capable sign structure |
| 10 | 1.00000018e+01 | 1.83612424e-05 | 5.63003586e-07 | -1.000000e+01+0.000000e+00j | -9.152471e-07-2.372752e-04j | -9.152471e-07+2.372752e-04j | stable; Hopf-capable sign structure |
| 100 | 1.00000002e+02 | 1.83612424e-04 | 5.63003586e-06 | -1.000000e+02+0.000000e+00j | -9.177806e-07-2.372752e-04j | -9.177806e-07+2.372752e-04j | stable; Hopf-capable sign structure |
| 1000 | 1.00000000e+03 | 1.83612424e-03 | 5.63003586e-05 | -1.000000e+03+0.000000e+00j | -9.180340e-07-2.372752e-04j | -9.180340e-07+2.372752e-04j | stable; Hopf-capable sign structure |
| 10000 | 1.00000000e+04 | 1.83612424e-02 | 5.63003586e-04 | -1.000000e+04+0.000000e+00j | -9.180593e-07-2.372752e-04j | -9.180593e-07+2.372752e-04j | stable; Hopf-capable sign structure |

At Berton's instantaneous drag rate from the local diagnostics,

```text
k = 2.164883811499e+01 s^-1
a0 = 1.218837350209e-06 > 0
a0/k = 5.630035864907e-08 > 0
a2*a1 - a0 = 8.593216061303e-04 > 0
```

Thus the corrected baseline is stable for the frozen parameters tested here: all swept roots have negative real parts.  The sweep is not by itself a Hopf bifurcation proof, because no physical control parameter is tuned through the Routh-Hurwitz surface, but it rules out the corrected-Jacobian saddle diagnosis for this baseline.

## Singular perturbation reduction: Routes A and B

For the slow limit, separate the `k`-free feedbacks as

```text
B = 2*beta*r*
F(zeta, r) = -w*zeta - B*r
g(zeta, r) = -d*zeta - c*r
```

so the full Jacobian is

```text
[[0, 1, 0], [-k*w, -k, -k*B], [-d, 0, -c]].
```

### Route A: cubic expansion

Substitute `k = 1/eps` into the corrected cubic and multiply by `eps` for slow roots `lambda = O(1)`:

```text
eps*P(lambda) = q0(lambda) + eps*q1(lambda)
```

with

```text
q0(lambda) = lambda^2 + (w + c)*lambda + (w*c - B*d)
q1(lambda) = lambda^3 + c*lambda^2.
```

The leading slow eigenvalues are

```text
lambda_slow = -(w + c)/2 ± 0.5*sqrt((w - c)^2 + 4*B*d).
```

If the discriminant is negative, the slow-pair frequency is

```text
omega0^2 = (w*c - B*d) - (w + c)^2/4
         = -((w - c)^2 + 4*B*d)/4.
```

### Route B: slow-fast reduction with inertial correction

Write the fast equation as

```text
eps*v_dot = F(zeta, r) - v.
```

The slow manifold including the first inertial correction is

```text
v = F + eps*h1 + O(eps^2)
h1 = -D F · [F, g]
   = -(w^2 + B*d)*zeta - B*(w + c)*r.
```

The corrected slow matrix is

```text
M0 + eps*M1

M0 = [[-w, -B],
      [-d, -c]]

M1 = [[-(w^2 + B*d), -B*(w + c)],
      [0,              0        ]]
```

Its leading characteristic polynomial is the same `q0(lambda)` as Route A.  The `O(eps)` corrections also reconcile: `q1_A - q1_B` has zero remainder modulo `q0`, and the slow eigenvalue corrections agree modulo `q0(lambda_slow)`.

Therefore Routes A and B agree, and the leading slow pair is genuinely independent of `k`.

## Comparison with Berton Eq. (119)

For an oscillatory slow pair, the leading frequency structure is

```text
omega0^2 = (w*c - B*d) - (w + c)^2/4.
```

In primitive Berton gradients, the dominant Eq. (119)-like product is

```text
-B*d = -2*beta*G*(sigma_S + R_zeta).
```

This has the expected fall-speed-gradient times microphysical-growth times supersaturation/radiative-gradient structure, with no spurious `k` dependence.  The factors of `r*` cancel in this dominant product.

For the baseline numbers, the slow complex pair from the large-`k` sweep has imaginary part approximately

```text
|Im(lambda)| = 2.372752e-04 s^-1
```

corresponding to a linear period of roughly

```text
2*pi / |Im(lambda)| ≈ 2.65e+04 s ≈ 7.4 h.
```

## Go/no-go conclusion

**Go for Hopf-capable sign structure; no for saddle at the analyzed baseline.**

The corrected analysis says:

- If `sigma_S + R_zeta > 0`, then `d > 0`; the corrected `-b*d` term can make `a0 < 0`, giving a saddle with a positive real eigenvalue and no Hopf at that fixed point.
- For the actual baseline derived from the current Berton Case-0 implementation, `sigma_S + R_zeta < 0`, so `d < 0`; the corrected `-b*d` term makes `a0 > 0`, and the root sweep shows a stable slow complex pair plus a fast stable root.

Destabilization toward a Hopf crossing requires moving the positive Routh-Hurwitz residual

```text
a2*a1 - a0 = k*(k*c + a + c^2) + b*d
```

toward zero.  In this frozen-parameter reduced model that means making `b*d` more negative, for example through stronger negative `sigma_S + R_zeta`, larger fall-speed slope `B`, or omitted feedbacks that reduce damping.  The Berton 10 km to 9 km transition should therefore be interpreted as moving the physical operating point relative to this Hopf surface, not as evidence for a saddle in the baseline corrected cubic.
