"""
Unit tests for summary_builder.py — zero API calls.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from summary_builder import build_summary, _plural


def test_plural():
    assert _plural(1, "paper") == "1 paper"
    assert _plural(0, "paper") == "0 papers"
    assert _plural(5, "trial") == "5 trials"
    assert _plural(2, "drug") == "2 drugs"


# ── Mock score dicts ──────────────────────────────────────

PROCEED_LOW = {
    "recommendation": "Proceed",
    "studied_before": "Low",
    "tested_in_practice": "Low",
    "translation_signal": "Low",
    "competitive_pressure": "Low",
    "failure_signal": "Low",
    "low_data": True,
    "rationale": "Limited indexed evidence found.",
    "counts": {"papers": 2, "trials": 1, "drugs": 0, "stopped": 0, "late_stage": 0},
}

PROCEED_MODERATE = {
    "recommendation": "Proceed",
    "studied_before": "Moderate",
    "tested_in_practice": "Low",
    "translation_signal": "Low",
    "competitive_pressure": "Low",
    "failure_signal": "Low",
    "low_data": False,
    "rationale": "No strong crowding or failure signal.",
    "counts": {"papers": 10, "trials": 2, "drugs": 1, "stopped": 0, "late_stage": 0},
}

REVIEW = {
    "recommendation": "Review carefully",
    "studied_before": "Moderate",
    "tested_in_practice": "Moderate",
    "translation_signal": "Low",
    "competitive_pressure": "Moderate",
    "failure_signal": "Low",
    "low_data": False,
    "rationale": "Meaningful prior activity — clearer angle needed.",
    "counts": {"papers": 12, "trials": 5, "drugs": 4, "stopped": 0, "late_stage": 1},
}

REVIEW_WITH_STOPPED = {
    "recommendation": "Review carefully",
    "studied_before": "Moderate",
    "tested_in_practice": "Moderate",
    "translation_signal": "Low",
    "competitive_pressure": "Moderate",
    "failure_signal": "Moderate",
    "low_data": False,
    "rationale": "One stopped trial.",
    "counts": {"papers": 8, "trials": 4, "drugs": 2, "stopped": 1, "late_stage": 0},
}

REFRAME_CROWDED = {
    "recommendation": "Reframe",
    "studied_before": "High",
    "tested_in_practice": "High",
    "translation_signal": "High",
    "competitive_pressure": "High",
    "failure_signal": "Low",
    "low_data": False,
    "rationale": "Crowded and already translated.",
    "counts": {"papers": 50, "trials": 20, "drugs": 15, "stopped": 0, "late_stage": 5},
}

REFRAME_FAILURES = {
    "recommendation": "Reframe",
    "studied_before": "High",
    "tested_in_practice": "High",
    "translation_signal": "Low",
    "competitive_pressure": "Low",
    "failure_signal": "High",
    "low_data": False,
    "rationale": "Repeated stop/withdrawal signals.",
    "counts": {"papers": 30, "trials": 12, "drugs": 2, "stopped": 4, "late_stage": 0},
}


# ── Tests ───────────────────────────────────────────────────

def test_build_summary_proceed_low():
    bullets = build_summary(PROCEED_LOW)
    assert len(bullets) == 3
    assert "underexplored" in bullets[0].lower() or "3 records" in bullets[0]
    assert "open" in bullets[1].lower() or "low" in bullets[1].lower()
    assert "absence" in bullets[2].lower() or "validate" in bullets[2].lower()


def test_build_summary_proceed_moderate():
    bullets = build_summary(PROCEED_MODERATE)
    assert len(bullets) == 3
    assert "10 papers" in bullets[0]
    assert "crowding" in bullets[0].lower() or "signal" in bullets[0].lower()


def test_build_summary_review():
    bullets = build_summary(REVIEW)
    assert len(bullets) == 3
    assert "12 papers" in bullets[0]
    assert "5 trials" in bullets[0]
    assert "differentiat" in bullets[-1].lower()


def test_build_summary_review_with_stopped():
    bullets = build_summary(REVIEW_WITH_STOPPED)
    assert len(bullets) == 3
    # Should mention the stopped trial
    assert "stopped" in bullets[1].lower() or "1 trial" in bullets[1]


def test_build_summary_reframe_crowded():
    bullets = build_summary(REFRAME_CROWDED)
    assert len(bullets) == 3
    assert "competitive" in bullets[0].lower() or "populated" in bullets[0].lower() or "15 drugs" in bullets[0]
    assert "late-stage" in bullets[1].lower() or "5 late-stage" in bullets[1]
    assert "hypothesis" in bullets[2].lower() or "population" in bullets[2].lower()


def test_build_summary_reframe_failures():
    bullets = build_summary(REFRAME_FAILURES)
    assert len(bullets) == 3
    assert "stopped" in bullets[0].lower() or "4 trials" in bullets[1] or "stopped" in bullets[1].lower()


def test_all_bullets_are_nonempty():
    """Every bullet across all scenarios is non-empty."""
    for scores in [
        PROCEED_LOW, PROCEED_MODERATE,
        REVIEW, REVIEW_WITH_STOPPED,
        REFRAME_CROWDED, REFRAME_FAILURES,
    ]:
        bullets = build_summary(scores)
        assert len(bullets) == 3, f"Expected 3 bullets for {scores['recommendation']}"
        for i, b in enumerate(bullets):
            assert b.strip(), f"Empty bullet {i} for {scores['recommendation']}"
            assert len(b) > 20, f"Bullet {i} too short: {b}"


# ── Run ────────────────────────────────────────────────────
if __name__ == "__main__":
    tests = [
        test_plural,
        test_build_summary_proceed_low,
        test_build_summary_proceed_moderate,
        test_build_summary_review,
        test_build_summary_review_with_stopped,
        test_build_summary_reframe_crowded,
        test_build_summary_reframe_failures,
        test_all_bullets_are_nonempty,
    ]
    passed = failed = 0
    for test in tests:
        try:
            test()
            print(f"✅ {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"💥 {test.__name__}: {e}")
            failed += 1

    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
