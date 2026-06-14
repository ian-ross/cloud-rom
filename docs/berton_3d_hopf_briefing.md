# Briefing: Symbolic + numerical analysis of the 3D fixed point in the Berton (2023) cirrus-parcel model — Hopf or saddle?

## Purpose

You have already built a numerical implementation of the Berton (2023) cirrus-uncinus parcel model (Eqs. 1a, 1b, 10 of that paper, with the supporting microphysics). This task is a *separate, complementary* piece of work: a **symbolic linear-stability analysis** of a reduced 3D version of that model, plus a **numerical root-tracking cross-check**, to determine the *nature* of the steady→oscillatory transition Berton observed — specifically, whether it is a Hopf bifurcation or whether the fixed point is a saddle.

**The question is genuinely open.** An earlier hand-derivation tentatively concluded "Hopf, triggered by radiative cooling," but that conclusion rested on a sign error in the Jacobian (an off-diagonal entry). With the sign corrected, the outcome hinges on the sign of a particular combination of gradients (`sigma_S + R_zeta`) that has **not** been reliably established. The whole point of this calculation is to settle that, symbolically and numerically, without presupposing the answer.

The deliverable is a single, well-documented Python script (or small set of scripts) using **SymPy** for the symbolic work and **NumPy** for the numerical cross-check. Correctness and verifiability matter far more than cleverness or brevity. Every non-trivial symbolic step must print its intermediate result so a human can check it.

This is an analysis task, not a simulation task. Do **not** reproduce the full Berton integration here. Reuse the existing numerical model only as a *source of parameter values and as an independent sanity check*.

---

## Background: the reduced 3D system

The analysis concerns a reduced model with three state variables:

- `zeta` — parcel altitude relative to the generating level (z − z₀)
- `v` — vertical velocity (ζ̇)
- `r` — mean ice-crystal radius

The governing equations are:

```
zeta_dot = v
v_dot    = -k * ( v - (W_a(zeta) - V_f(r)) )
r_dot    = (G / r) * ( s(zeta) - R(zeta, r) )
```

where:

- `k` is the drag relaxation rate (≈ 15–20 s⁻¹ in Berton's runs; the inverse drag time τ_D).
- `W_a(zeta)` is the prescribed ambient updraft profile.
- `V_f(r) = beta * r**2` is the Stokes fall speed (`beta = 2*rho_i*g/(9*nu) > 0`).
- `G > 0` is the growth diffusivity (units m²/s) from the capacitance growth law; treat as a positive constant.
- `s(zeta)` is the ambient supersaturation sampled along the trajectory.
- `R(zeta, r)` is the radiative term.

### Closed forms to use for the linearization

For the radiative term, use the closed form derived analytically (verify it symbolically if practical, but it may be taken as given):

```
R(zeta, r) = Phi(T(zeta)) * (eta_a(zeta) - 1) * r
```

i.e. **R is linear in r at fixed crystal habit**, with `Phi > 0` a slowly varying thermodynamic prefactor. This gives the key partial derivatives:

```
R_r    = dR/dr    = R / r        (sign = sign(eta_a - 1))
R_zeta = dR/dzeta                (sign UNCERTAIN — see below; this is pivotal)
```

For the ambient supersaturation gradient, define:

```
sigma_S = -ds/dz   (> 0 in Berton's setup: humidity falls with height)
```

**The sign of `R_zeta`, and specifically the sign of the combination `sigma_S + R_zeta`, is the crux of this whole analysis.** A prior hand-derivation argued `R_zeta > 0` in the cooling regime (which would make `sigma_S + R_zeta > 0`), but this is exactly a hand result that must be checked symbolically from the closed form of R (differentiate `Phi(T(zeta)) * (eta_a(zeta) - 1) * r` using Berton's `eta_a(z)` profile, Eqs. 80–81, and `T(z)` profile, Eqs. 75–76). **Do not assume its sign. Derive it, and report it prominently, because it determines whether the system is a Hopf or a saddle.**

Linearize `s` and `R` to first order about the fixed point. Keep `R_r`, `R_zeta`, `sigma_S` as **symbolic parameters with declared signs where known** (`sigma_S > 0`; `R_r` sign = sign(eta_a − 1); `R_zeta` sign FREE) so the sign structure stays explicit.

---

## The fixed point

At the fixed point `(zeta_*, v_*, r_*)`:

```
v_* = 0
W_a(zeta_*) = V_f(r_*) = beta * r_***2      # force balance
s(zeta_*)  = R(zeta_*, r_*)                  # driving balance (s - R = 0)
```

The condition `s - R = 0` at the fixed point is important: it makes the `-(G/r**2)(s-R)` term in `dr_dot/dr` vanish. The code should **demonstrate** this cancellation symbolically rather than assume it.

---

## Reference hand-derivation (CORRECTED — for cross-checking only)

The hand analysis, **after correcting the sign error**, gives the following. The code must independently confirm these (do **not** hard-code them — derive them and compare).

Define shorthand parameters:
- `a = k * w_prime`            where `w_prime = -dW_a/dzeta` at the fixed point (`w_prime > 0`)
- `b = 2 * k * beta * r_star`  (`b > 0`)
- `c = (G / r_star) * R_r`     (sign = sign of R_r = sign(eta_a − 1))
- `d = (G / r_star) * (sigma_S + R_zeta)`   (sign = sign of (sigma_S + R_zeta) — UNCERTAIN)

Jacobian — **note the corrected [v_dot, r] entry is `-b` (= -k*V_f'), NOT +b**:

```
J = [[ 0,    1,   0  ],
     [ -a,  -k,  -b  ],
     [ -d,   0,  -c  ]]
```

(The [1,2] entry is `d(v_dot)/dr = -k * V_f'(r_star) = -2*k*beta*r_star = -b`. An earlier version had `+b`; that was wrong and inverted the conclusion.)

Characteristic polynomial (λ³ + a₂λ² + a₁λ + a₀):

```
a2 = k + c                 # unchanged by the fix
a1 = k*c + a               # unchanged by the fix
a0 = a*c - b*d             # CORRECTED: was a*c + b*d
```

Only `a0` changed. Crucially:

```
a0 = (k*G/r_star) * ( w_prime*R_r - 2*beta*r_star**2*(sigma_S + R_zeta) )
   = k * (2D determinant)
```

i.e. `a0` equals `k` times the determinant of the 2D slaved system. This consistency (the fully-relaxed fast variable handing back the 2D slow system) is itself a check: if the code's `a0` does **not** factor as `k × (2D det)`, something is wrong.

Routh–Hurwitz Hopf condition (a₂a₁ = a₀, with a₂>0, a₀>0):

```
a2*a1 - a0 = k*(k*c + a + c**2) + b*d         # CORRECTED: was - b*d
```

so the Hopf locus is:

```
k*(k*c + a + c**2) = -b*d                      # CORRECTED: RHS sign flipped
```

Onset frequency (if a Hopf exists): `Omega_0**2 = a1 = k*c + a`.

**These corrected reference results may still contain errors.** The symbolic pass exists to confirm or correct them. If SymPy disagrees, trust SymPy and flag the discrepancy.

---

## The central question: Hopf or saddle?

For a **Hopf** bifurcation we need `a2 > 0`, `a0 > 0`, and `a2*a1 = a0` at onset, with the pair crossing transversally. The blocking issue is `a0 > 0`:

```
a0 = (k*G/r_star) * ( w_prime*R_r - 2*beta*r_star**2*(sigma_S + R_zeta) )
```

Consider the two candidate regimes (note `w_prime > 0`, `k, G, beta, r_star > 0`):

- **If `R_r < 0` (cooling, eta_a < 1) AND `sigma_S + R_zeta > 0`:** then `w_prime*R_r < 0` and `-2*beta*r_star**2*(sigma_S+R_zeta) < 0`. Both terms negative → **`a0 < 0` → a positive real eigenvalue → SADDLE, no Hopf.** This is the outcome the corrected hand-algebra points to *if* the prior `R_zeta > 0` claim holds.

- **If `sigma_S + R_zeta < 0`** (radiative altitude-gradient negative and steep enough to overcome the humidity gradient): then `d < 0`, the second term flips positive, and `a0 > 0` becomes possible — reopening the door to a Hopf.

**Therefore the entire Hopf-vs-saddle outcome hinges on the sign of `sigma_S + R_zeta`.** This is why deriving `R_zeta` symbolically (Task 1b below) is the single most important step. Do not presuppose either outcome.

---

## Tasks

### Task 1a — Symbolic Jacobian and characteristic polynomial

1. Declare symbols with assumptions where known:
   - `k, beta, G, r_star` — positive
   - `w_prime` — positive
   - `sigma_S` — positive
   - `R_r, R_zeta` — real (signs left free)
2. Build the Jacobian **from the reduced equations symbolically** — define the three RHS expressions with general `W_a(zeta)`, `V_f(r)`, `s(zeta)`, `R(zeta, r)` as SymPy `Function`s, differentiate, then substitute the fixed-point conditions (including `s - R = 0`). Do not type in the Jacobian by hand; let SymPy build it, then compare against the corrected reference `J` above and assert equality. **Pay particular attention to the sign of the [v_dot, r] entry** — confirm it is `-k*V_f'` = `-b`.
3. Compute the characteristic polynomial, `collect` in `lam`, extract `a2, a1, a0`. Print them. Compare against the corrected reference and assert equality. Confirm `a0` factors as `k × (2D determinant)`.
4. Form `a2*a1 - a0`, `simplify`/`factor`, confirm it equals `k*(k*c + a + c**2) + b*d`. Print both forms.

### Task 1b — Derive the sign of R_zeta (PIVOTAL)

1. Take the closed form `R(zeta, r) = Phi(T(zeta)) * (eta_a(zeta) - 1) * r`.
2. Using Berton's `eta_a(z)` profile (Eqs. 80–81: piecewise linear, 0.9 at 9 km to 1.1 at 10 km, transition at 9.5 km) and `T(z)` profile (Eqs. 75–76, lapse rate in the relevant layer), differentiate symbolically to get `R_zeta = dR/dzeta` at the operating altitude (parcel sits near z ≈ 8.3–9.6 km in Berton's oscillatory cases).
3. Evaluate the sign of `R_zeta` and, critically, the sign of `sigma_S + R_zeta`, at the baseline operating point. `sigma_S` comes from the ambient humidity profile (Eqs. 78–79).
4. **Report both signs prominently.** This determines Hopf vs. saddle per the section above.

### Task 2 — Numerical root-tracking across k (the cheap reality check)

Do this early. It directly reveals Hopf vs. saddle without any singular-limit algebra.

1. Pull `k, beta, G, r_star` and the derived `w_prime, sigma_S, R_r, R_zeta` from the existing numerical model's parameters and fixed-point state (Berton baseline, cooling regime). Document the provenance of each number.
2. Substitute into the corrected `a2, a1, a0`.
3. For `k` in `[1, 10, 100, 1000, 1e4]` s⁻¹ (holding slow physical parameters fixed), compute the three roots with `numpy.roots([1, a2, a1, a0])`.
4. Print the roots at each k. **Diagnostic:**
   - **Saddle outcome:** one root has positive real part and is (near-)real → fixed point unstable via real eigenvalue, no oscillatory instability. Consistent with `a0 < 0`.
   - **Hopf-capable outcome:** all roots have negative real part at baseline (stable), with a complex pair whose real part is small and approaches zero as a parameter is tuned; one real root → −k as k grows, the complex pair converges. Consistent with `a0 > 0`.
5. Whichever it is, report it plainly. A saddle is a legitimate and important result, not a failure to be hidden.

### Task 3 — The singular-perturbation reduction (k → ∞), done carefully

Relevant whether the outcome is Hopf or saddle — it tells you what slow dynamics survive. Do it symbolically and redundantly.

**Route A — asymptotic factorisation of the cubic.** Substitute `k = 1/eps`, seek slow roots as a series in `eps`, collect order by order, print each order, extract the reduced quadratic and read off the slow-pair eigenvalues. Check whether the slow pair is genuinely k-independent.

**Route B — direct slow-fast (Tikhonov/Fenichel) reduction.** Treat `v` as fast with quasi-steady value `v = W_a(zeta) - V_f(r)`, but **retain the O(eps) inertial correction** — do NOT collapse to a bare 2D system (that discards the inertial overshoot). Derive the corrected slow dynamics to O(eps) and obtain the slow eigenvalues.

**Reconcile A and B** with an explicit `simplify(A - B) == 0` check. If they disagree, surface it.

**Cross-check against Berton Eq. (119).** If the slow pair is oscillatory, confirm its frequency matches the structure of Berton's linearized oscillator (slow microphysical rate × gravity/fall term × supersaturation gradient, with k absent). Note: a previous hand attempt at this limit produced a spurious seconds-scale period by failing to cancel k — watch for that.

### Task 4 — Stability classification and sign conclusions

1. State the corrected Hopf locus `k*(k*c + a + c**2) = -b*d` and the determinant `a0 = k × (2D det)`.
2. Using the `R_zeta` sign from Task 1b, classify the baseline fixed point: Hopf-capable (a0 > 0) or saddle (a0 < 0)?
3. If saddle: state it clearly and identify what would have to change (sign of `sigma_S + R_zeta`, or a feedback omitted from this reduction — e.g. the Re-dependence of the drag rate k itself, which was frozen) for an oscillatory instability to exist.
4. If Hopf-capable: give the onset frequency, the destabilising direction, and how lowering the updraft base moves the system relative to the locus (compare to Berton's 10 km → 9 km transition).

### Task 5 — Reporting

Produce a concise Markdown summary containing:
- The symbolic Jacobian (with the corrected `-b` entry), characteristic polynomial, and `a0 = k × (2D det)` factorisation as confirmed/corrected by SymPy.
- The derived sign of `R_zeta` and of `sigma_S + R_zeta` (Task 1b) — highlighted.
- The root-tracking table and its Hopf-vs-saddle diagnosis.
- The reduced slow-pair eigenvalues from Routes A and B, whether they agree, and (if oscillatory) whether they match Berton Eq. (119).
- A clear verdict: **Is the baseline fixed point a Hopf-capable stable spiral or a saddle? On what sign does that hinge, and what is that sign?** This is the go/no-go output. Either answer is acceptable; an honest saddle finding is as valuable as a Hopf.

---

## Connection to the existing numerical code

- **Reuse parameters, not structure.** Import/copy physical constants and the computed fixed-point state (`r_star`, `w_prime`, `sigma_S`, `R_r`, `R_zeta`) from the existing model. Document provenance of each value.
- **Mirror naming and ordering.** Keep state order `(zeta, v, r)` and symbol names (`W_a`, `V_f`, `s`, `R`, `k`, `G`, `beta`) aligned with the numerical code so the symbolic Jacobian reads alongside it.
- **Independent validation.** Evaluate the symbolic Jacobian numerically at the fixed point and compare against a finite-difference Jacobian from the existing numerical RHS at the same point. They should agree to FD accuracy. This catches transcription errors in the reduced equations — and would independently confirm the corrected sign of the [v_dot, r] entry.

---

## Methodological requirements

- **Print every intermediate.** Jacobian, char-poly coefficients, `a2*a1 - a0`, the `R_zeta` derivation, series expansions, reduced eigenvalues — all printed readably (`sympy.pprint` or LaTeX). No black boxes.
- **Assert, don't assume.** Encode the corrected reference results as SymPy equality checks and assert them. Make failures loud.
- **Do not presuppose Hopf.** The framing is Hopf-OR-saddle. The sign of `sigma_S + R_zeta` decides it and must be derived, not assumed. A saddle is a real outcome.
- **Two routes for the reduction.** The slow-pair eigenvalues must be obtained two independent ways (Routes A and B) and reconciled.
- **Numerical before symbolic for the singular limit.** Run Task 2 before Task 3.
- **Trust the tool over the hand-derivation.** If SymPy contradicts the corrected reference here, surface it; do not silently adjust SymPy to match.
- **Watch the units.** Keep dimensional consistency explicit; non-dimensionalise if helpful (scale time by growth time `tau_g = r_star**2/G`, altitude by `ell` with `sigma_S*ell = s_star`) and report dimensionless groups.

## Environment

- Python with `sympy` and `numpy` (`pip install sympy numpy`). No Mathematica/Maple dependency.
- Optional but recommended given the pivotal nature: re-derive the sign of `a0` (and, if oscillatory, the slow-pair frequency) in Maxima or a second structurally-different SymPy route, and confirm agreement.

## What success looks like

A reader can follow the printed output from the raw reduced equations to: a confirmed corrected Jacobian; a derived sign for `sigma_S + R_zeta`; a root-tracking table that diagnoses Hopf-capable vs. saddle; two reconciled reductions; and a clear, honestly-stated verdict on the nature of the fixed point. The symbolic code is legible alongside the existing numerical model. Any discrepancy with the corrected hand-derivation is surfaced, not hidden.
