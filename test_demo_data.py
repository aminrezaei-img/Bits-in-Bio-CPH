"""
Unit tests for demo_data.py — validates all 3 scenarios,
including that they produce the expected recommendations.
Zero API calls.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from demo_data import get_demo_scenario, get_demo_scenarios, DEMO_SCENARIOS
from table_builder import build_evidence_table, build_paper_rows, build_trial_rows, build_drug_rows
from summary_builder import build_summary


def test_all_scenarios_present():
    assert set(DEMO_SCENARIOS.keys()) == {"proceed", "review", "reframe"}


def test_each_scenario_has_all_keys():
    required = {"label", "idea", "expected_rec", "biomedcore", "trialcore", "drugcore", "regulatorycore"}
    for key, sc in DEMO_SCENARIOS.items():
        missing = required - set(sc.keys())
        assert not missing, f"{key}: missing keys {missing}"


def test_each_scenario_has_records():
    for key, sc in DEMO_SCENARIOS.items():
        for core in ["biomedcore", "trialcore", "drugcore"]:
            records = sc[core]["records"]
            assert isinstance(records, list), f"{key}.{core}: records not a list"
            assert len(records) > 0, f"{key}.{core}: no records"
        # Regulatory may be empty for low-data scenarios
        reg = sc["regulatorycore"]["records"]
        assert isinstance(reg, list), f"{key}.regulatorycore: records not a list"


def test_scores_produce_expected_recommendations():
    """Simulate the scoring pipeline for each demo scenario."""
    for key, sc in DEMO_SCENARIOS.items():
        papers = sc["biomedcore"]["records"]
        trials = sc["trialcore"]["records"]
        drugs = sc["drugcore"]["records"]

        pc = len(papers)
        tc = len(trials)
        dc = len(drugs)

        stopped = sum(
            1 for t in trials if t.get("overallStatus") in ("TERMINATED", "WITHDRAWN", "SUSPENDED")
        )
        late_stage = sum(
            1 for d in drugs if d.get("maxClinicalStage") in ("PHASE3", "PREAPPROVAL", "APPROVAL")
        )

        low_data = (pc + tc + dc) < 5
        failure = "High" if stopped >= 3 else "Moderate" if stopped >= 1 else "Low"
        competitive = "High" if dc >= 10 else "Moderate" if dc >= 3 else "Low"
        translation = "High" if late_stage >= 3 else "Moderate" if late_stage >= 1 else "Low"

        if low_data:
            rec = "Proceed"
        elif failure == "High":
            rec = "Reframe"
        elif competitive == "High" and translation in ("Moderate", "High"):
            rec = "Reframe"
        elif tc >= 10 or dc >= 3:  # tested moderate/high or competitive moderate
            # Simpler approximation of the actual logic
            rec = "Review carefully"
        else:
            rec = "Proceed"

        assert rec == sc["expected_rec"], (
            f"{key}: expected {sc['expected_rec']}, got {rec} "
            f"(pc={pc}, tc={tc}, dc={dc}, stopped={stopped}, late={late_stage})"
        )


def test_proceed_low_counts():
    sc = DEMO_SCENARIOS["proceed"]
    total = (
        len(sc["biomedcore"]["records"])
        + len(sc["trialcore"]["records"])
        + len(sc["drugcore"]["records"])
    )
    assert total < 10, f"Proceed should be low-data, got {total} records"


def test_reframe_high_counts():
    sc = DEMO_SCENARIOS["reframe"]
    dc = len(sc["drugcore"]["records"])
    assert dc >= 5, f"Reframe should have many drugs, got {dc}"


def test_demo_data_builds_valid_table():
    """Table builder works with demo data."""
    for key, sc in DEMO_SCENARIOS.items():
        table = build_evidence_table(
            sc["biomedcore"]["records"],
            sc["trialcore"]["records"],
            sc["drugcore"]["records"],
            sc["regulatorycore"]["records"],
        )
        assert len(table) > 0, f"{key}: empty table"
        for row in table:
            assert set(row.keys()) == {"Source", "Title", "Status", "Date", "Signal", "ID"}


def test_demo_data_builds_valid_summary():
    """Summary builder works with demo data and produces expected rec."""
    for key, sc in DEMO_SCENARIOS.items():
        papers = sc["biomedcore"]["records"]
        trials = sc["trialcore"]["records"]
        drugs = sc["drugcore"]["records"]
        regulatory = sc["regulatorycore"]["records"]

        from scoring import compute_scores
        scores = compute_scores(papers, trials, drugs, regulatory)

        assert scores["recommendation"] == sc["expected_rec"], (
            f"{key}: expected {sc['expected_rec']}, got {scores['recommendation']}"
        )

        bullets = build_summary(scores)
        assert len(bullets) == 3
        for b in bullets:
            assert len(b) > 20


# ── Run ────────────────────────────────────────────────────
if __name__ == "__main__":
    tests = [
        test_all_scenarios_present,
        test_each_scenario_has_all_keys,
        test_each_scenario_has_records,
        test_scores_produce_expected_recommendations,
        test_proceed_low_counts,
        test_reframe_high_counts,
        test_demo_data_builds_valid_table,
        test_demo_data_builds_valid_summary,
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
