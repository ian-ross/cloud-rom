from __future__ import annotations

from pathlib import Path

REPORT = Path(
    "episodes/06-full-model-auto-seed-continuation/docs/full_berton_dynamics_continuation_report.md"
)


def test_task013_report_contains_required_evidence_chain() -> None:
    text = REPORT.read_text()

    required_phrases = [
        "damped transient approach to a stable equilibrium",
        "AUTO executable: `/usr/local/bin/auto`",
        "bash episodes/04-full-model-auto-equilibria/auto/berton_full/run_auto.sh",
        "uv run python episodes/05-full-model-oscillatory-orbit/scripts/berton_full_task011_classify.py",
        "bash episodes/06-full-model-auto-seed-continuation/auto/berton_full_task012/run_auto.sh",
        "No complex-conjugate pair approached the imaginary axis",
        "The refined late-time equilibrium was",
        "Periodic-orbit continuation was not attempted because there was no limit-cycle-like sampled orbit to seed",
        "The reduced 3D analysis found a corrected Hopf-capable sign structure",
        "Retry `H_a3` as the primary Hopf-control candidate",
    ]
    for phrase in required_phrases:
        assert phrase in text


def test_task013_report_verdict_is_not_overstated() -> None:
    text = REPORT.read_text()

    assert "not a validated local Hopf bifurcation" in text
    assert "not evidence for a periodic orbit" in text
    assert "not as proof" in text
    assert "parameter-dependent Hopf scenario" in text
    assert "remains possible" in text


def test_task013_report_links_expected_artifacts() -> None:
    text = REPORT.read_text()

    artifact_paths = [
        "episodes/04-full-model-auto-equilibria/outputs/task010/",
        "episodes/05-full-model-oscillatory-orbit/outputs/task011/",
        "episodes/06-full-model-auto-seed-continuation/outputs/task012/",
        "case0_late_envelope.png",
        "case0_solver_agreement.png",
        "continuation_equilibrium_seed.csv",
        "continuation_equilibrium_eigenvalues.csv",
    ]
    for path in artifact_paths:
        assert path in text
