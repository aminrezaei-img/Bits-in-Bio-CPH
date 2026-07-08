"""
Evidence table builder for Bio Project Triage.
Pure functions — no API calls, fully testable with mock data.
"""
from typing import Any


def _truncate(text: str, max_len: int = 120) -> str:
    """Truncate text for table display."""
    if not text:
        return "N/A"
    return text[:max_len] + "…" if len(text) > max_len else text


def _safe_get(rec: dict, *keys, default: str = "") -> str:
    """Safely extract a field from a nested dict, returning string."""
    val = rec
    for key in keys:
        if isinstance(val, dict):
            val = val.get(key)
        elif val is None:
            return default
        else:
            return default
    if val is None:
        return default
    if not isinstance(val, str):
        val = str(val)
    return val


def build_paper_rows(papers: list[dict], max_rows: int = 10) -> list[dict]:
    """Convert BiomedCore records into evidence table rows."""
    rows = []
    for rec in papers[:max_rows]:
        amass_id = _safe_get(rec, "amassId")
        pub_types = rec.get("publicationTypes", [])
        status = ", ".join(pub_types) if pub_types else _safe_get(rec, "language") or "—"
        cite_count = rec.get("citationCount", 0) or 0

        signal_parts = []
        if cite_count:
            signal_parts.append(f"Cited {cite_count}x")
        if rec.get("journalQualityJufo") and rec["journalQualityJufo"] >= 2:
            signal_parts.append("High-tier journal")

        rows.append({
            "Source": "📄 Paper",
            "Title": _truncate(rec.get("title", "N/A")),
            "Status": status,
            "Date": _safe_get(rec, "publicationDate"),
            "Signal": ", ".join(signal_parts) if signal_parts else "—",
            "ID": amass_id if amass_id else "—",
        })
    return rows


def build_trial_rows(trials: list[dict], max_rows: int = 10) -> list[dict]:
    """Convert TrialCore records into evidence table rows."""
    rows = []
    STOPPED = {"TERMINATED", "WITHDRAWN", "SUSPENDED"}
    for rec in trials[:max_rows]:
        amass_id = _safe_get(rec, "amassId")
        phase = _safe_get(rec, "phase")
        ov_status = _safe_get(rec, "overallStatus")
        status = f"{ov_status}" if ov_status else "—"
        if phase:
            status = f"Phase {phase.replace('PHASE', '')} · {status}"

        is_stopped = rec.get("overallStatus", "") in STOPPED
        signal = "⚠️ Stopped/withdrawn" if is_stopped else "—"
        if not is_stopped and rec.get("hasResults"):
            signal = "Has results"

        rows.append({
            "Source": "🔬 Trial",
            "Title": _truncate(rec.get("briefTitle") or rec.get("officialTitle") or "N/A"),
            "Status": status,
            "Date": _safe_get(rec, "startDate"),
            "Signal": signal,
            "ID": amass_id if amass_id else "—",
        })
    return rows


def build_drug_rows(drugs: list[dict], max_rows: int = 10) -> list[dict]:
    """Convert DrugCore records into evidence table rows."""
    rows = []
    for rec in drugs[:max_rows]:
        amass_id = _safe_get(rec, "amassId")
        drug_type = _safe_get(rec, "drugType")
        stage = _safe_get(rec, "maxClinicalStage")
        status = f"{stage}" if stage else "—"
        if drug_type:
            status = f"{drug_type} · {status}"

        is_approved = rec.get("maxClinicalStage") == "APPROVAL"
        signal = "✅ Approved" if is_approved else "—"

        rows.append({
            "Source": "💊 Drug",
            "Title": _truncate(rec.get("name", "N/A")),
            "Status": status,
            "Date": "",  # DrugCore has no single date field
            "Signal": signal,
            "ID": amass_id if amass_id else "—",
        })
    return rows


def build_evidence_table(
    papers: list[dict],
    trials: list[dict],
    drugs: list[dict],
    max_per_source: int = 10,
) -> list[dict]:
    """
    Build a unified evidence table from all three source groups.

    Returns a list of dicts with keys: Source, Title, Status, Date, Signal, ID.
    """
    table = []
    table.extend(build_paper_rows(papers, max_per_source))
    table.extend(build_trial_rows(trials, max_per_source))
    table.extend(build_drug_rows(drugs, max_per_source))
    return table
