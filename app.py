"""
Bio Project Triage — Unlocking data silos through a unified decision brief.
Query literature, trials, and drug records. Get a first-pass recommendation.
"""
import streamlit as st
from amass_client import search_all, CORES
from table_builder import build_evidence_table
from summary_builder import build_summary
from scoring import compute_scores
from demo_data import get_demo_scenario, get_demo_scenarios

st.set_page_config(page_title="Bio Project Triage", page_icon="🧬", layout="wide")

# ── Cached search ───────────────────────────────────────────
@st.cache_data(ttl=3600)
def cached_search(query: str, limit: int = 20):
    """Cache API results for 1 hour to avoid rate limits during demos."""
    return search_all(query, limit=limit)


# ── Helpers ─────────────────────────────────────────────────
def get_signal_emoji(level):
    return {"High": "🔴", "Moderate": "🟡", "Low": "🟢"}.get(level, "⚪")


def _all_failed(results: dict) -> bool:
    """True if every core returned an error or zero records."""
    for r in results.values():
        if r.get("records") and not r.get("error"):
            return False
    return True


def render_results(papers, trials, drugs, regulatory=None, errors=None):
    """Render the full results section from record lists."""
    scores = compute_scores(papers, trials, drugs, regulatory)

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
        f"Regulatory: {scores['counts'].get('regulatory', 0)} · "
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
    table_rows = build_evidence_table(papers, trials, drugs, regulatory, max_per_source=10)

    if table_rows:
        st.dataframe(table_rows, use_container_width=True, hide_index=True)
    else:
        st.info("No records found across the three sources.")

    # ── Errors ──
    if errors:
        for core_name, err_msg in errors.items():
            st.warning(f"⚠️ {CORES[core_name][1]}: {err_msg}")


# ── Sidebar: Quick Demo ─────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚡ Quick Demo")
    scenarios = get_demo_scenarios()
    demo_key = st.selectbox(
        "Load a pre-cached scenario:",
        options=["—"] + list(scenarios.keys()),
        format_func=lambda k: scenarios[k]["label"] if k != "—" else "Select a demo...",
        label_visibility="collapsed",
    )
    if demo_key != "—":
        sc = scenarios[demo_key]
        st.caption(f"*{sc['idea']}*")
        st.caption(f"Expected: **{sc['expected_rec']}**")
        if st.button("🚀 Run This Demo", use_container_width=True):
            st.session_state["run_demo"] = demo_key

    st.markdown("---")
    st.caption("Built with [Amass API](https://platform.amass.tech) · [Repo](https://github.com/aminrezaei-img/Bits-in-Bio-CPH)")


# ── Header ──────────────────────────────────────────────────
st.title("🧬 Bio Project Triage")
st.caption("Decide whether a bio idea is worth pursuing — before spending weeks on it.")
st.markdown("---")


# ── Input ───────────────────────────────────────────────────
idea = st.text_area(
    "What's your project idea?",
    placeholder="Describe the target, intervention, disease area, or hypothesis...",
    height=100,
    key="idea_input",
)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    assess = st.button("🔍 Assess Project", type="primary", use_container_width=True)


# ── Results ─────────────────────────────────────────────────
# Path 1: Demo button in sidebar
if st.session_state.get("run_demo"):
    demo_key = st.session_state.pop("run_demo")
    sc = get_demo_scenario(demo_key)
    if sc:
        st.success(f"📦 Loaded demo: **{sc['label']}**")
        errors = {}
        for core_name in ["biomedcore", "trialcore", "drugcore", "regulatorycore"]:
            if sc[core_name].get("error"):
                errors[core_name] = sc[core_name]["error"]
        render_results(
            sc["biomedcore"]["records"],
            sc["trialcore"]["records"],
            sc["drugcore"]["records"],
            regulatory=sc["regulatorycore"]["records"],
            errors=errors,
        )
        st.caption(f"💡 *Demo query idea:* {sc['idea']}")

# Path 2: User-entered query
elif assess and idea.strip():
    with st.spinner("Searching across literature, trials, drugs, and regulatory records..."):
        results = cached_search(idea.strip(), limit=20)

    papers = results.get("biomedcore", {}).get("records", [])
    trials = results.get("trialcore", {}).get("records", [])
    drugs = results.get("drugcore", {}).get("records", [])
    regulatory = results.get("regulatorycore", {}).get("records", [])

    # Fallback: if all cores failed, try demo data
    if _all_failed(results):
        st.warning("⚠️ All API sources unavailable — showing cached demo data instead.")
        # Use the reframe scenario as the safest fallback (most visually interesting)
        sc = get_demo_scenario("reframe")
        papers = sc["biomedcore"]["records"]
        trials = sc["trialcore"]["records"]
        drugs = sc["drugcore"]["records"]
        regulatory = sc["regulatorycore"]["records"]
        errors = {k: v.get("error", "API unavailable") for k, v in results.items() if v.get("error")}
    else:
        errors = {k: v["error"] for k, v in results.items() if v.get("error")}

    render_results(papers, trials, drugs, regulatory=regulatory, errors=errors)

elif assess and not idea.strip():
    st.warning("Please enter a project idea.")

else:
    # ── Empty state ──
    st.markdown("---")
    st.info("👆 Enter a project idea above and click **Assess Project** to get started — or pick a demo from the sidebar.")

    with st.expander("💡 Example queries to try"):
        st.markdown("""
        - **CAR-T therapy for solid tumors** → expect *Reframe* (crowded, translated)
        - **CRISPR-based microbiome editing for depression** → expect *Review carefully* or *Proceed*
        - **GLP-1 receptor agonist for Alzheimer's** → expect *Review carefully* (some testing, growing)
        """)
