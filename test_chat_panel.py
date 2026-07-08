"""
Unit tests for chat_panel.py — zero API calls.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from chat_engine import generate_response

CONTEXT_REFRAME = {
    "idea": "CAR-T therapy for solid tumors",
    "recommendation": "Reframe",
    "rationale": "Crowded and already translated.",
    "studied_before": "High", "tested_in_practice": "High",
    "translation_signal": "High", "competitive_pressure": "High",
    "failure_signal": "Moderate",
    "counts": {"papers": 45, "trials": 18, "drugs": 12,
               "regulatory": 6, "patents": 8, "stopped": 2, "late_stage": 5},
}

CONTEXT_PROCEED = {
    "idea": "New target X for rare disease Y",
    "recommendation": "Proceed",
    "rationale": "Limited evidence.", "studied_before": "Low",
    "tested_in_practice": "Low", "translation_signal": "Low",
    "competitive_pressure": "Low", "failure_signal": "Low",
    "counts": {"papers": 2, "trials": 0, "drugs": 0,
               "regulatory": 0, "patents": 0, "stopped": 0, "late_stage": 0},
}


def test_no_context():
    r = generate_response("What now?", {})
    assert "don't have" in r.lower()


def test_why():
    r = generate_response("Why this?", CONTEXT_REFRAME)
    assert "Reframe" in r


def test_next_proceed():
    r = generate_response("What now?", CONTEXT_PROCEED)
    assert "validate" in r.lower()


def test_next_reframe():
    r = generate_response("What should I do?", CONTEXT_REFRAME)
    assert "hypothesis" in r.lower()


def test_stopped():
    r = generate_response("Tell me about stopped trials", CONTEXT_REFRAME)
    assert "2 stopped" in r or "caution" in r.lower()


def test_competitors():
    r = generate_response("competitive landscape?", CONTEXT_REFRAME)
    assert "competitive" in r.lower()


def test_regulatory():
    r = generate_response("FDA approvals?", CONTEXT_REFRAME)
    assert "authorization" in r.lower()


def test_patents():
    r = generate_response("patents?", CONTEXT_REFRAME)
    assert "patent" in r.lower()


def test_summary():
    r = generate_response("summary", CONTEXT_REFRAME)
    assert "Reframe" in r and "45 papers" in r


def test_default():
    r = generate_response("random biology", CONTEXT_REFRAME)
    assert "Reframe" in r


if __name__ == "__main__":
    tests = [test_no_context, test_why, test_next_proceed,
             test_next_reframe, test_stopped, test_competitors,
             test_regulatory, test_patents, test_summary, test_default]
    passed = failed = 0
    for t in tests:
        try:
            t()
            print(f"✅ {t.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"❌ {t.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"💥 {t.__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
