"""
Template summary builder for Bio Project Triage.
Generates the "Why this matters" three-bullet explanation.
Pure functions — no API calls, no LLM.

Per MVP spec §6, output section #3.
"""
from typing import Any


def _plural(n: int, word: str) -> str:
    """Return '1 paper' or '5 papers'."""
    return f"{n} {word}{'s' if n != 1 else ''}"


def build_summary(scores: dict[str, Any]) -> list[str]:
    """
    Build 3 contextual bullets for the "Why this matters" section.

    Args:
        scores: dict from compute_scores() with keys:
            recommendation, studied_before, tested_in_practice,
            translation_signal, competitive_pressure, failure_signal,
            low_data, rationale, counts

    Returns:
        list of 3 short bullet strings.
    """
    rec = scores["recommendation"]
    c = scores["counts"]

    if rec == "Proceed":
        return _proceed_bullets(scores, c)
    elif rec == "Review carefully":
        return _review_bullets(scores, c)
    else:  # Reframe
        return _reframe_bullets(scores, c)


def _proceed_bullets(scores: dict, c: dict) -> list[str]:
    bullets = []

    # Bullet 1: evidence landscape
    if scores["low_data"]:
        bullets.append(
            f"Only {_plural(c['papers'] + c['trials'] + c['drugs'], 'record')} "
            f"found across literature, trials, and drugs — "
            f"this space may be underexplored."
        )
    else:
        p = f"{_plural(c['papers'], 'paper')}" if c['papers'] else ""
        t = f"{_plural(c['trials'], 'trial')}" if c['trials'] else ""
        d = f"{_plural(c['drugs'], 'drug')}" if c['drugs'] else ""
        parts = [x for x in [p, t, d] if x]
        bullets.append(
            f"Found {', '.join(parts)} — "
            f"no strong crowding signal detected."
        )

    # Bullet 2: competitive / translation
    if c["drugs"] == 0 and c["late_stage"] == 0:
        bullets.append(
            "No approved or late-stage interventions found — "
            "the translational path appears open."
        )
    else:
        bullets.append(
            "Competitive pressure and translation signals are low — "
            "there is room to establish a position."
        )

    # Bullet 3: caveat
    bullets.append(
        "Absence of indexed evidence does not prove novelty — "
        "validate with domain experts before committing resources."
    )

    return bullets


def _review_bullets(scores: dict, c: dict) -> list[str]:
    bullets = []

    # Bullet 1: how much activity
    bullets.append(
        f"Found {_plural(c['papers'], 'paper')}, {_plural(c['trials'], 'trial')}, "
        f"and {_plural(c['drugs'], 'drug')} — "
        f"meaningful prior activity exists."
    )

    # Bullet 2: testing or competition
    if c["stopped"] > 0:
        bullets.append(
            f"{_plural(c['stopped'], 'trial')} stopped or withdrawn — "
            f"check why before committing to a similar approach."
        )
    elif scores["competitive_pressure"] == "Moderate":
        bullets.append(
            "Moderate competitive pressure detected — "
            "a clearer differentiating angle would strengthen the case."
        )
    else:
        bullets.append(
            "Some prior testing exists but no decisive failure signal — "
            "a sharper hypothesis could still succeed."
        )

    # Bullet 3: path forward
    bullets.append(
        "Consider refining the target population, mechanism, "
        "or methodology to differentiate from existing work."
    )

    return bullets


def _reframe_bullets(scores: dict, c: dict) -> list[str]:
    bullets = []

    # Bullet 1: crowding
    if scores["competitive_pressure"] == "High":
        bullets.append(
            f"Strong competitive signal: {_plural(c['drugs'], 'drug')} "
            f"with {_plural(c['late_stage'], 'late-stage intervention')} "
            f"— "
            f"the space is already populated."
        )
    else:
        bullets.append(
            f"Found {_plural(c['papers'] + c['trials'], 'record')} across literature "
            f"and trials — substantial prior investigation."
        )

    # Bullet 2: failure or translation
    if scores["failure_signal"] == "High":
        bullets.append(
            f"{_plural(c['stopped'], 'trial')} stopped, withdrawn, or suspended — "
            f"repeated practical failure signals warrant caution."
        )
    elif scores["translation_signal"] in ("Moderate", "High"):
        bullets.append(
            f"Translation signal is {scores['translation_signal'].lower()} — "
            f"late-stage or approved interventions already occupy this space."
        )
    else:
        bullets.append(
            "The combination of high literature activity and competitive pressure "
            "suggests the space is crowded."
        )

    # Bullet 3: path forward
    bullets.append(
        "Rather than treating this as a fresh idea, consider changing the "
        "hypothesis, target population, mechanism, or positioning."
    )

    return bullets
