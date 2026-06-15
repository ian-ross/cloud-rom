# Reviewer's checklist: judging the 3D fixed-point result (Hopf or saddle?)

A companion to the agent briefing. This is for *you* — how to read the agent's output, in what order, and what should make you stop. The aim is to reach a defensible go/no-go without re-reading the whole script. Read the output in the order below, not the order the script runs.

> **Note on the correction:** an earlier version of these documents assumed the transition was a Hopf bifurcation. That rested on a sign error in the Jacobian's [v_dot, r] entry (`+b` instead of the correct `-b`). With the sign fixed, the determinant coefficient is `a0 = a*c - b*d = k × (2D determinant)`, and the outcome — **Hopf or saddle** — now hinges on the sign of `sigma_S + R_zeta`, which is not yet established. The question is genuinely open. An honest saddle finding is as valuable as a Hopf and must not be massaged into the "hoped-for" answer.

## The one-line verdict you're after

> Is the baseline fixed point a **Hopf-capable stable spiral** (a0 > 0) or a **saddle** (a0 < 0)? That hinges on the sign of `sigma_S + R_zeta` — what did the symbolic derivation find that sign to be, and do the numerics agree?

Four load-bearing pieces: **(1) the corrected Jacobian sign, (2) the derived sign of `sigma_S + R_zeta`, (3) the root-tracking diagnosis, (4) consistency `a0 = k × 2D-det`.** Get those and the verdict follows.

## Read in this order

### 1. Confirm the sign correction landed
Before anything else, check the printed Jacobian's [v_dot, r] entry is **`-b` (= -k·V_f' = -2k·beta·r_star)**, and that `a0 = a*c - b*d` (minus, not plus). If the script still has `+b` / `a0 = a*c + b*d`, it inherited the old error and everything downstream is suspect. The finite-difference-Jacobian cross-check (below) should independently confirm the sign.

### 2. The pivotal number: sign of `sigma_S + R_zeta` (Task 1b)
This single sign decides Hopf vs. saddle. Find where the agent differentiated `R = Phi(T(zeta))·(eta_a(zeta)−1)·r` using Berton's `eta_a(z)` and `T(z)` profiles and computed `R_zeta`, then `sigma_S + R_zeta`.

- It should be **derived from the profiles**, not assumed. If the agent asserted a sign without differentiating the closed form, that's not good enough — it's the crux.
- Note both contributions to `R_zeta`: the `eta_a` gradient (rising 0.9→1.1 over 9→10 km) and the lapse-rate/thermodynamic term. Check both were included.
- **`sigma_S + R_zeta > 0` → points to saddle** (with cooling, R_r < 0). **`sigma_S + R_zeta < 0` → reopens Hopf.** Either is a legitimate finding.

### 3. The cheapest decisive check: root-tracking (Task 2)
Look at the roots-vs-k table.

- **Saddle:** a (near-)real root with **positive** real part at baseline k. Consistent with `a0 < 0`.
- **Hopf-capable:** all roots negative-real-part at baseline (stable spiral), complex pair with small real part; as k grows one real root → −k and the complex pair converges. Consistent with `a0 > 0`.
- **Stop and worry:** the diagnosis from this table contradicts the sign found in step 2. They must agree (`a0 < 0` ⟺ positive real root). If they don't, there's an inconsistency to chase before trusting anything.

This table tells you the answer directly. The symbolic work explains *why*.

### 4. The consistency check: `a0 = k × (2D determinant)` (Task 1a)
The corrected `a0` should factor as `k` times the 2D slaved determinant. Confirm the agent showed this. It's a strong internal check: the fully-relaxed fast variable must hand back the 2D slow system. If `a0` does not factor this way, the reduction has an error regardless of what the verdict claims.

### 5. The singular reduction, two routes (Task 3)
Relevant whichever way the verdict goes — it shows what slow dynamics survive.

- **Go:** Routes A (asymptotic factorisation) and B (Fenichel with the O(ε) inertial correction retained) both shown, reconciled with an explicit `simplify(A−B)==0`.
- **Stop:** only one route; or Route B collapsed to a bare 2D system (it must keep the inertial correction); or a seconds-scale period appears (the old k-cancellation failure — a previous hand attempt produced exactly this).
- If the slow pair is oscillatory, confirm its frequency matches Berton Eq. (119)'s structure (k absent).

### 6. Ties back to the validated model (Task 1a)
- Symbolic Jacobian evaluated at the fixed point vs. finite-difference Jacobian from the existing numerical RHS — should agree to FD accuracy. This both validates the reduced equations and independently confirms the corrected `-b` sign.
- The `s − R = 0` cancellation in `dr_dot/dr` should be *shown*.

## Cross-cutting things to confirm

- **Intermediates printed.** Char-poly coefficients, `a2·a1 − a0`, the `R_zeta` derivation, series terms — all visible. No black boxes.
- **Provenance of numbers.** `w_prime`, `sigma_S`, `R_r`, `R_zeta`, `r_star`, `G`, `beta` traceable to the existing model or a stated source.
- **Verdict not presupposed.** The output should read as "we derived sign(sigma_S + R_zeta) = X, therefore saddle/Hopf," not "we confirmed the Hopf." If the prose assumes Hopf throughout, the agent didn't internalise the reframing.

## How to read the overall outcome

**Clean result — saddle:** `sigma_S + R_zeta > 0` derived and confirmed, root table shows a positive real eigenvalue, `a0 = k × 2D-det < 0`, routes reconciled. → The oscillation Berton sees is **not** a Hopf limit cycle of this fixed point. This is a real finding. It means either (a) his damped oscillation is a transient of a different structure, or (b) the genuine oscillation requires a feedback this reduction froze — most likely the Re-dependence of the drag rate k itself, or the habit/capacitance size-dependence folded into G and beta. The project pivots to "what mechanism actually produces the oscillation, and is it a limit cycle, a center, or forced transient?" — harder, but a legitimate and interesting question.

**Clean result — Hopf:** `sigma_S + R_zeta < 0` derived, baseline is a stable spiral, tuning the updraft base crosses the locus, frequency matches Berton's ~7–10 hr via two reconciled routes. → The original hopd-for picture survives the sign correction. Strong basis to proceed to the contrail extension (Model B).

**Inconsistent / unresolved:** symbolic sign and numerical root diagnosis disagree, or routes won't reconcile, or `a0` doesn't factor as `k × 2D-det`. → Don't draw a conclusion yet. There's a residual error; the most likely culprits are the `R_zeta` derivation (profile handling) or a leftover sign slip. Resolve before investing further.

## A caution on what *not* to over-weight

- **Don't lean on the damping ratio.** Berton's ζ ≈ 0.01–0.02 is contaminated by forward-Euler numerical damping (his explicit scheme artificially anti-damps the oscillatory mode) and is good only to order of magnitude. Trust the *classification* (saddle vs. spiral) and, if oscillatory, the *period* and the *sign* of the radiative effect — not absolute ζ.
- **Don't treat a saddle as a failed run.** Given the sign correction, a saddle is a plausible and honest outcome. The earlier "Hopf, cooling-triggered" story was an artifact of the sign error; if the corrected algebra says saddle, that *is* the result, and it reshapes the project rather than ending it (the "oscillation is irreducibly 3D / inertia can't be eliminated" observation stands either way).

## If you want a second opinion

For a result this pivotal — and given it already turned on one sign error — the independent re-derivation of `a0`'s sign (and, if oscillatory, the slow-pair frequency) in Maxima or a second SymPy route is worth requesting even if the primary routes agree. I can also re-derive the sign of `sigma_S + R_zeta` by hand against the agent's printed `R_zeta` expansion as a further check, once you have the output — that's the number everything now hinges on.
