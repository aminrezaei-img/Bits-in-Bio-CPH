"""
Unit tests for table_builder.py — mock data, zero API calls.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from table_builder import (
    build_paper_rows,
    build_trial_rows,
    build_drug_rows,
    build_evidence_table,
)


# ── Mock data ──────────────────────────────────────────────

MOCK_PAPERS = [
    {
        "amassId": "AMBC_p001",
        "title": "CAR-T Therapy for Solid Tumors: A Systematic Review",
        "publicationDate": "2024-03-15",
        "journal": "Nature Medicine",
        "publicationTypes": ["Journal Article", "Review"],
        "citationCount": 42,
        "journalQualityJufo": 3,
    },
    {
        "amassId": "AMBC_p002",
        "title": "Early Results of CAR-T in Pancreatic Cancer",
        "publicationDate": "2023-11-01",
        "journal": "Lancet Oncology",
        "publicationTypes": ["Clinical Trial", "Journal Article"],
        "citationCount": 15,
        "journalQualityJufo": 2,
    },
    {
        "amassId": "AMBC_p003",
        "title": None,
        "publicationDate": None,
        "journal": None,
        "publicationTypes": [],
        "citationCount": None,
        "journalQualityJufo": None,
    },
]

MOCK_TRIALS = [
    {
        "amassId": "AMTC_t001",
        "briefTitle": "CAR-T in HER2+ Solid Tumors Phase 2",
        "officialTitle": "A Phase 2 Study of CAR-T Cells in HER2-Positive Solid Tumors",
        "startDate": "2023-06-01",
        "phase": "PHASE2",
        "overallStatus": "RECRUITING",
        "hasResults": False,
    },
    {
        "amassId": "AMTC_t002",
        "briefTitle": None,
        "officialTitle": "CAR-T for Melanoma — Terminated Early",
        "startDate": "2021-01-15",
        "phase": "PHASE1",
        "overallStatus": "TERMINATED",
        "hasResults": True,
    },
    {
        "amassId": "AMTC_t003",
        "briefTitle": None,
        "officialTitle": None,
        "startDate": None,
        "phase": None,
        "overallStatus": None,
        "hasResults": None,
    },
]

MOCK_DRUGS = [
    {
        "amassId": "AMDC_d001",
        "name": "Tisagenlecleucel",
        "drugType": "ANTIBODY",
        "maxClinicalStage": "APPROVAL",
    },
    {
        "amassId": "AMDC_d002",
        "name": "Experimental CAR-T Construct XYZ",
        "drugType": "CELL",
        "maxClinicalStage": "PHASE1",
    },
    {
        "amassId": "AMDC_d003",
        "name": None,
        "drugType": None,
        "maxClinicalStage": None,
    },
]


# ── Tests ───────────────────────────────────────────────────

def test_build_paper_rows():
    rows = build_paper_rows(MOCK_PAPERS)
    assert len(rows) == 3, f"Expected 3 rows, got {len(rows)}"

    r0 = rows[0]
    assert r0["Source"] == "📄 Paper"
    assert "CAR-T Therapy" in r0["Title"]
    assert r0["Status"] == "Journal Article, Review"
    assert r0["Date"] == "2024-03-15"
    assert "Cited 42x" in r0["Signal"]
    assert "High-tier journal" in r0["Signal"]
    assert r0["ID"] == "AMBC_p001"

    # Null/empty record
    r2 = rows[2]
    assert r2["Title"] == "N/A"
    assert r2["Status"] == "—"
    assert r2["Signal"] == "—"
    assert r2["ID"] == "AMBC_p003"


def test_build_trial_rows():
    rows = build_trial_rows(MOCK_TRIALS)
    assert len(rows) == 3

    r0 = rows[0]
    assert r0["Source"] == "🔬 Trial"
    assert "HER2+" in r0["Title"]
    assert "Phase 2" in r0["Status"]
    assert "RECRUITING" in r0["Status"]
    assert r0["Date"] == "2023-06-01"
    assert r0["Signal"] == "—"
    assert r0["ID"] == "AMTC_t001"

    # Terminated trial
    r1 = rows[1]
    assert "TERMINATED" in r1["Status"]
    assert r1["Signal"] == "⚠️ Stopped/withdrawn"

    # Null record
    r2 = rows[2]
    assert r2["Title"] == "N/A"
    assert r2["Status"] == "—"
    assert r2["Signal"] == "—"


def test_build_drug_rows():
    rows = build_drug_rows(MOCK_DRUGS)
    assert len(rows) == 3

    r0 = rows[0]
    assert r0["Source"] == "💊 Drug"
    assert "Tisagenlecleucel" in r0["Title"]
    assert "ANTIBODY" in r0["Status"]
    assert "APPROVAL" in r0["Status"]
    assert r0["Signal"] == "✅ Approved"
    assert r0["ID"] == "AMDC_d001"

    # Null record
    r2 = rows[2]
    assert r2["Title"] == "N/A"
    assert r2["Status"] == "—"
    assert r2["Signal"] == "—"


def test_build_evidence_table():
    table = build_evidence_table(MOCK_PAPERS, MOCK_TRIALS, MOCK_DRUGS)
    assert len(table) == 9  # 3+3+3

    # Check ordering: papers first, then trials, then drugs
    assert table[0]["Source"] == "📄 Paper"
    assert table[3]["Source"] == "🔬 Trial"
    assert table[6]["Source"] == "💊 Drug"

    # All rows must have the 6 expected keys
    expected_keys = {"Source", "Title", "Status", "Date", "Signal", "ID"}
    for row in table:
        assert set(row.keys()) == expected_keys, f"Missing keys: {expected_keys - set(row.keys())}"


def test_max_rows_limit():
    """Only max_rows records per source."""
    big_papers = [MOCK_PAPERS[0].copy() for _ in range(15)]
    rows = build_paper_rows(big_papers, max_rows=10)
    assert len(rows) == 10


def test_empty_inputs():
    """Empty lists produce empty list."""
    table = build_evidence_table([], [], [])
    assert table == []


# ── Run ────────────────────────────────────────────────────
if __name__ == "__main__":
    tests = [
        test_build_paper_rows,
        test_build_trial_rows,
        test_build_drug_rows,
        test_build_evidence_table,
        test_max_rows_limit,
        test_empty_inputs,
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
