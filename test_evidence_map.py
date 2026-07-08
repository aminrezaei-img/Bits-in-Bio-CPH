"""
Unit tests for evidence_map.py — zero API calls.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from evidence_map import build_evidence_map_html, has_evidence


MOCK_PAPERS = [{"title": "CAR-T for Solid Tumors: A Review", "citationCount": 42}]
MOCK_TRIALS = [{"briefTitle": "HER2-CAR-T Phase 2 Trial", "overallStatus": "COMPLETED"}]
MOCK_DRUGS = [{"name": "Tisagenlecleucel", "maxClinicalStage": "APPROVAL"}]
MOCK_REG = [{"name": "Kymriah", "agency": "FDA", "authorizationStatus": "ACTIVE"}]
MOCK_PAT = [{"title": "CAR-T targeting solid tumors", "publicationNumber": "US-10533054-B2"}]


def test_build_evidence_map_html_renders():
    html = build_evidence_map_html("CAR-T therapy", MOCK_PAPERS, MOCK_TRIALS, MOCK_DRUGS)
    assert "CAR-T therapy" in html
    assert "Literature" in html
    assert "Trials" in html
    assert "Drugs" in html
    assert "CAR-T for Solid Tumors" in html
    assert "HER2-CAR-T" in html
    assert "Tisagenlecleucel" in html
    assert "click" in html.lower() or "expand" in html.lower()  # Interactive


def test_build_evidence_map_with_all_sources():
    html = build_evidence_map_html(
        "CAR-T for solid tumors",
        MOCK_PAPERS, MOCK_TRIALS, MOCK_DRUGS,
        regulatory=MOCK_REG, patents=MOCK_PAT,
    )
    assert "Regulatory" in html
    assert "Patents" in html
    assert "Kymriah" in html


def test_build_evidence_map_empty():
    html = build_evidence_map_html("test", [], [], [])
    assert "No evidence to map" in html


def test_build_evidence_map_truncates_idea():
    long_idea = "A" * 100
    html = build_evidence_map_html(long_idea, MOCK_PAPERS, [], [])
    assert "A" * 80 in html
    assert "…" in html


def test_has_evidence():
    assert has_evidence(MOCK_PAPERS, [], []) is True
    assert has_evidence([], [], []) is False
    assert has_evidence([], [], [], regulatory=MOCK_REG) is True


def test_max_per_source_capped():
    many_papers = [{"title": f"Paper {i}"} for i in range(10)]
    html = build_evidence_map_html("test", many_papers, [], [], max_per_source=5)
    assert "Paper 4" in html
    assert "Paper 5" not in html  # Should be capped


# ── Run ────────────────────────────────────────────────────
if __name__ == "__main__":
    tests = [
        test_build_evidence_map_html_renders,
        test_build_evidence_map_with_all_sources,
        test_build_evidence_map_empty,
        test_build_evidence_map_truncates_idea,
        test_has_evidence,
        test_max_per_source_capped,
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
