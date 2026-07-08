"""
Scoring logic for Bio Project Triage.
Pure functions — no API calls, no Streamlit dependency.
Transparent, deterministic rules per MVP spec §8.
"""
from typing import Any


def compute_scores(papers: list[dict], trials: list[dict], drugs: list[dict], regulatory: list[dict] | None = None) -> dict[str, Any]:
    """Compute evidence signals and recommendation from record lists."""
    if regulatory is None:
        regulatory = []
    pc = len(papers)
    tc = len(trials)
    dc = len(drugs)
    rc = len(regulatory)

    stopped = sum(
        1 for t in trials
        if t.get("overallStatus", "") in ("TERMINATED", "WITHDRAWN", "SUSPENDED")
    )
    late_stage = sum(
        1 for d in drugs
        if d.get("maxClinicalStage", "") in ("PHASE3", "PREAPPROVAL", "APPROVAL")
    )

    low_data = (pc + tc + dc + rc) < 5

    studied = (
        "High" if pc >= 25 else
        "Moderate" if pc >= 8 else
        "Low"
    )
    tested = (
        "High" if tc >= 10 else
        "Moderate" if tc >= 3 else
        "Low"
    )
    failure = (
        "High" if stopped >= 3 else
        "Moderate" if stopped >= 1 else
        "Low"
    )
    translation = (
        "High" if late_stage >= 3 else
        "Moderate" if late_stage >= 1 else
        "Low"
    )
    competitive = (
        "High" if dc >= 10 else
        "Moderate" if dc >= 3 else
        "Low"
    )

    # Recommendation
    if low_data:
        rec = "Proceed"
        rationale = "Limited indexed evidence found — this may be underexplored."
    elif failure == "High":
        rec = "Reframe"
        rationale = "Prior testing shows repeated stop or withdrawal signals."
    elif competitive == "High" and translation in ("Moderate", "High"):
        rec = "Reframe"
        rationale = "The space appears crowded and already translated."
    elif tested in ("Moderate", "High") or competitive == "Moderate":
        rec = "Review carefully"
        rationale = "Meaningful prior activity exists — a clearer angle is needed."
    else:
        rec = "Proceed"
        rationale = "No strong crowding or failure signal found."

    return {
        "studied_before": studied,
        "tested_in_practice": tested,
        "failure_signal": failure,
        "translation_signal": translation,
        "competitive_pressure": competitive,
        "recommendation": rec,
        "rationale": rationale,
        "low_data": low_data,
        "counts": {"papers": pc, "trials": tc, "drugs": dc, "regulatory": rc, "stopped": stopped, "late_stage": late_stage},
    }
