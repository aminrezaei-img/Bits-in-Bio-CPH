"""
Signal mapper for Viably — connects evidence signals to individual records.
Shows which records contribute to each signal (Studied before, Tested in practice, etc.)
"""
from typing import Any


# Signal → emoji + label
SIGNAL_META = {
    "studied": ("📄", "Studied before"),
    "tested": ("🔬", "Tested in practice"),
    "translation": ("💊", "Translation"),
    "competitive": ("🏭", "Competitive"),
    "failure": ("⚠️", "Failure signal"),
    "regulatory": ("🏛️", "Regulatory"),
    "patent": ("📜", "Patent/IP"),
}


def get_record_signals(record: dict, source: str) -> list[str]:
    """
    Determine which evidence signals a single record contributes to.
    Returns list of signal keys (e.g. ['studied'], ['tested', 'failure']).
    """
    signals = []

    if source == "paper":
        signals.append("studied")

    elif source == "trial":
        signals.append("tested")
        status = record.get("overallStatus", "")
        if status in ("TERMINATED", "WITHDRAWN", "SUSPENDED"):
            signals.append("failure")

    elif source == "drug":
        signals.append("translation")
        signals.append("competitive")

    elif source == "regulatory":
        signals.append("translation")
        signals.append("regulatory")

    elif source == "patent":
        signals.append("competitive")
        signals.append("patent")

    return signals


def format_signal_badges(signals: list[str]) -> str:
    """Format signal badges as a compact string."""
    parts = []
    for s in signals:
        meta = SIGNAL_META.get(s)
        if meta:
            parts.append(f"{meta[0]}")
    return " ".join(parts) if parts else "—"


def get_signal_label(signal_key: str) -> str:
    """Get human-readable label for a signal key."""
    meta = SIGNAL_META.get(signal_key)
    return f"{meta[0]} {meta[1]}" if meta else signal_key


def build_signal_summary(records_by_source: dict[str, list[dict]]) -> dict[str, int]:
    """
    Build a summary: which signals are backed by how many records.
    Returns {signal_key: record_count}.
    """
    counts = {}
    for source, records in records_by_source.items():
        for rec in records:
            for sig in get_record_signals(rec, source):
                counts[sig] = counts.get(sig, 0) + 1
    return counts
