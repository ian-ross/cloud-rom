from __future__ import annotations

from pathlib import Path


REPORT = Path(__file__).resolve().parents[1] / "episodes" / "02-reduced-model-cas" / "docs" / "berton_3d_hopf_analysis_summary.md"


def report_text() -> str:
    text = REPORT.read_text(encoding="utf-8")
    assert len(text) > 1000
    return text


def test_report_contains_corrected_jacobian_polynomial_and_determinant():
    text = report_text()

    assert "[-a,  -k,  -b ]" in text
    assert "a2 = k + c" in text
    assert "a1 = k*c + a" in text
    assert "a0 = a*c - b*d" in text
    assert "a0 / k = w*c - B*d" in text
    assert "k*(k*c + a + c^2) = -b*d" in text
    assert "one fewer power of `r*`" in text


def test_report_highlights_gradient_signs_and_final_verdict():
    text = report_text()

    assert "R_zeta > 0" in text
    assert "sigma_S + R_zeta = -5.640219674712e-05 m^-1 < 0" in text
    assert "d = -3.073061242928e-12 s^-1 m^-1 < 0" in text
    assert "Hopf-capable stable spiral" in text
    assert "not a corrected-Jacobian saddle" in text
    assert "Go for Hopf-capable sign structure; no for saddle" in text


def test_report_includes_root_tracking_table_and_diagnosis():
    text = report_text()

    assert "| k [s^-1] | a2 | a1 | a0 | root 1 | root 2 | root 3 | diagnosis |" in text
    for k in ["| 1 |", "| 10 |", "| 100 |", "| 1000 |", "| 10000 |"]:
        assert k in text
    assert "2.372752e-04" in text
    assert "all root" in text or "all swept roots" in text
    assert "rules out the corrected-Jacobian saddle diagnosis" in text


def test_report_includes_route_a_route_b_agreement_and_eq119_frequency():
    text = report_text()

    assert "Route A" in text
    assert "Route B" in text
    assert "q0(lambda) = lambda^2 + (w + c)*lambda + (w*c - B*d)" in text
    assert "lambda_slow = -(w + c)/2" in text
    assert "Routes A and B agree" in text
    assert "-B*d = -2*beta*G*(sigma_S + R_zeta)" in text
    assert "no spurious `k` dependence" in text
