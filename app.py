"""
Bio Project Triage — Unlocking data silos through a unified decision brief.
Query literature, trials, and drug records. Get a first-pass recommendation.
"""
import streamlit as st
from amass_client import search_all, CORES
from table_builder import build_evidence_table
from summary_builder import build_summary

st.set_page_config(page_title="Bio Project Triage", page_icon="🧬", layout="wide")

# ── Cached search ───────────────────────────────────────────
@st.cache_data(ttl=3600)
def cached_search(query: str, limit: int = 20):
    """Cache API results for 1 hour to avoid rate limits during demos."""
    return search_all(query, limit=limit)


# ── Header ──────────────────────────────────────────────────
st.title("🧬 Bio Project Triage")
st.caption("Decide whether a bio idea is worth pursuing — before spending weeks on it.")
st.markdown("---")


# ── Input ───────────────────────────────────────────────────
idea = st.text_area(
    "What's your project idea?",
    placeholder="Describe the target, intervention, disease area, or hypothesis...",
    height=100,
)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    assess = st.button("🔍 Assess Project", type="primary", use_container_width=True)


# ── Scoring logic ───────────────────────────────────────────
def compute_scores(papers, trials, drugs):
    """Transparent, deterministic scoring — no LLM required."""
    pc = len(papers)
    tc = len(trials)
    dc = len(drugs)

    # Count terminated/withdrawn trials
    stopped = sum(
        1 for t in trials
        if t.get("overallStatus", "") in ("TERMINATED", "WITHDRAWN", "SUSPENDED")
    )

    # Count late-stage / approved drugs
    late_stage = sum(
        1 for d in drugs
        if d.get("maxClinicalStage", "") in ("PHASE3", "PREAPPROVAL", "APPROVAL")
    )

    low_data = (pc + tc + dc) < 5

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
        "counts": {"papers": pc, "trials": tc, "drugs": dc, "stopped": stopped, "late_stage": late_stage},
    }


def get_signal_emoji(level):
    return {"High": "🔴", "Moderate": "🟡", "Low": "🟢"}.get(level, "⚪")


# ── Results ─────────────────────────────────────────────────
if assess and idea.strip():
    with st.spinner("Searching across literature, trials, and drugs..."):
        results = cached_search(idea.strip(), limit=20)

    # Build flat record list per core
    papers = results.get("biomedcore", {}).get("records", [])
    trials = results.get("trialcore", {}).get("records", [])
    drugs = results.get("drugcore", {}).get("records", [])

    scores = compute_scores(papers, trials, drugs)

    # ── Recommendation card ──
    rec_color = {
        "Proceed": "#16a34a",
        "Review carefully": "#d97706",
        "Reframe": "#dc2626",
    }.get(scores["recommendation"], "#6b7280")

    st.markdown("---")
    st.markdown(
        f"""
        <div style="background:{rec_color};padding:24px;border-radius:12px;color:white;margin-bottom:20px">
            <h2 style="margin:0;color:white">{scores['recommendation']}</h2>
            <p style="margin:8px 0 0 0;opacity:0.9">{scores['rationale']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if scores["low_data"]:
        st.warning(
            "⚠️ **Low data warning:** Absence of records does not prove novelty. "
            "The query may be too narrow, newly emerging, or not well indexed."
        )

    # ── Evidence cards ──
    st.subheader("📊 Evidence Signals")
    cols = st.columns(4)

    signals = [
        ("📄 Studied before", scores["studied_before"]),
        ("🔬 Tested in practice", scores["tested_in_practice"]),
        ("💊 Translation signal", scores["translation_signal"]),
        ("🏭 Competitive pressure", scores["competitive_pressure"]),
    ]

    for i, (label, level) in enumerate(signals):
        emoji = get_signal_emoji(level)
        with cols[i]:
            st.metric(label=label, value=f"{emoji} {level}")

    # ── Counts row ──
    st.caption(
        f"Papers: {scores['counts']['papers']} · "
        f"Trials: {scores['counts']['trials']} · "
        f"Drugs: {scores['counts']['drugs']} · "
        f"Stopped trials: {scores['counts']['stopped']} · "
        f"Late-stage: {scores['counts']['late_stage']}"
    )

    # ── Why this matters ──
    st.subheader("💡 Why This Matters")
    bullets = build_summary(scores)
    for bullet in bullets:
        st.markdown(f"- {bullet}")

    # ── Evidence table ──
    st.subheader("📋 Supporting Evidence")

    table_rows = build_evidence_table(papers, trials, drugs, max_per_source=10)

    if table_rows:
        st.dataframe(table_rows, use_container_width=True, hide_index=True)
    else:
        st.info("No records found across the three sources.")

    # ── Errors ──
    for core_name, result in results.items():
        if result.get("error"):
            st.warning(f"⚠️ {CORES[core_name][1]}: {result['error']}")

elif assess and not idea.strip():
    st.warning("Please enter a project idea.")
else:
    # ── Empty state ──
    st.markdown("---")
    st.info("👆 Enter a project idea above and click **Assess Project** to get started.")

    with st.expander("💡 Example queries to try"):
        st.markdown("""
        - **CAR-T therapy for solid tumors** → expect *Reframe* (crowded, translated)
        - **CRISPR-based microbiome editing for depression** → expect *Review carefully* or *Proceed*
        - **GLP-1 receptor agonist for Alzheimer's** → expect *Review carefully* (some testing, growing)
        """)
