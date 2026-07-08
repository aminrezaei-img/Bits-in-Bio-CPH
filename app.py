"""
Viably — Unlocking data silos. Decide whether a bio project idea is worth pursuing.
Query studies, trials, interventions, and regulatory records. Get a first-pass recommendation.
"""
import streamlit as st
from amass_client import search_all, CORES
from table_builder import build_evidence_table
from summary_builder import build_summary
from scoring import compute_scores
from demo_data import get_demo_scenario, get_demo_scenarios
from evidence_map import build_evidence_map_html, has_evidence
from chat_panel import render_chat_panel, set_context
from session_manager import save_session, render_session_sidebar, get_active_session, restore_session
from globe_map import extract_countries, build_globe_html, has_country_data

st.set_page_config(page_title="Viably", page_icon="🧬", layout="wide")

# ── Custom CSS ──────────────────────────────────────────────
st.markdown("""
<style>
.viably-header {
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    padding: 12px 24px;
    border-radius: 10px;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.viably-header h1 {
    color: white;
    margin: 0;
    font-size: 22px;
    font-weight: 700;
}
.viably-header .tagline {
    color: #94a3b8;
    font-size: 12px;
}
.profile-section {
    background: #f8fafc;
    border-radius: 10px;
    padding: 12px;
    margin-top: 16px;
    border: 1px solid #e2e8f0;
}
</style>
""", unsafe_allow_html=True)

# ── Cached search ───────────────────────────────────────────
@st.cache_data(ttl=3600)
def cached_search(query: str, limit: int = 20):
    return search_all(query, limit=limit)


# ── Helpers ─────────────────────────────────────────────────
def get_signal_emoji(level):
    return {"High": "🔴", "Moderate": "🟡", "Low": "🟢"}.get(level, "⚪")


def _all_failed(results: dict) -> bool:
    for r in results.values():
        if r.get("records") and not r.get("error"):
            return False
    return True


def render_assessment(papers, trials, drugs, regulatory=None, patents=None, errors=None, idea=""):
    """Render the assessment results in the left panel."""
    scores = compute_scores(papers, trials, drugs, regulatory, patents)

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
        with cols[i]:
            st.metric(label=label, value=f"{get_signal_emoji(level)} {level}")

    # ── Counts row ──
    st.caption(
        f"Papers: {scores['counts']['papers']} · "
        f"Trials: {scores['counts']['trials']} · "
        f"Drugs: {scores['counts']['drugs']} · "
        f"Regulatory: {scores['counts'].get('regulatory', 0)} · "
        f"Patents: {scores['counts'].get('patents', 0)} · "
        f"Stopped: {scores['counts']['stopped']} · "
        f"Late-stage: {scores['counts']['late_stage']}"
    )

    # ── Why this matters ──
    st.subheader("💡 Why This Matters")
    for bullet in build_summary(scores):
        st.markdown(f"- {bullet}")

    # ── Evidence table ──
    st.subheader("📋 Supporting Evidence")
    table_rows = build_evidence_table(papers, trials, drugs, regulatory, patents, max_per_source=10)

    if table_rows:
        st.dataframe(
            table_rows,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Title": st.column_config.TextColumn("Title", width="large"),
                "Status": st.column_config.TextColumn("Status", width="small"),
                "Signals": st.column_config.TextColumn("Signals", width="small", help="Which evidence signals this record contributes to"),
            },
        )
    else:
        st.info("No records found across the sources.")

    # ── Errors ──
    if errors:
        for core_name, err_msg in errors.items():
            st.warning(f"⚠️ {CORES[core_name][1]}: {err_msg}")

    # ── Evidence map ──
    if has_evidence(papers, trials, drugs, regulatory, patents):
        with st.expander("🗺️ Evidence Map (click groups to expand, hover for details)", expanded=False):
            map_html = build_evidence_map_html(
                idea, papers, trials, drugs, regulatory, patents, max_per_source=5,
            )
            st.components.v1.html(map_html, height=500, scrolling=True)

    # ── Globe: country origins ──
    if has_country_data(trials, patents, regulatory):
        with st.expander("🌍 Evidence Globe — Where does this evidence come from?", expanded=False):
            countries = extract_countries(papers, trials, drugs, regulatory, patents)
            globe_html = build_globe_html(countries)
            st.components.v1.html(globe_html, height=300, scrolling=True)

    return scores


# ── Sidebar ─────────────────────────────────────────────────
with st.sidebar:
    # Logo / header
    st.markdown(
        "<div style='text-align:center;padding:8px 0 12px 0'>"
        "<div style='font-size:100px;line-height:1.1'>🧬</div>"
        "<span style='font-size:24px;font-weight:800;color:#1e293b'>Viably</span>"
        "<div style='font-size:14px;color:#64748b;margin-top:2px'>Evidence-based project triage</div>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # Quick Demo
    st.markdown("#### ⚡ Quick Demo")
    scenarios = get_demo_scenarios()
    demo_key = st.selectbox(
        "Load scenario:",
        options=["—"] + list(scenarios.keys()),
        format_func=lambda k: scenarios[k]["label"] if k != "—" else "Select a demo...",
        label_visibility="collapsed",
    )
    if demo_key != "—":
        sc = scenarios[demo_key]
        st.caption(f"*{sc['idea'][:60]}…*")
        st.caption(f"Expected: **{sc['expected_rec']}**")
        if st.button("🚀 Run Demo", use_container_width=True, type="primary"):
            st.session_state["run_demo"] = demo_key

    st.markdown("---")

    # Sessions
    render_session_sidebar()

    st.markdown("---")

    # Profile section at bottom
    st.markdown("""
    <div class="profile-section">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
            <div style="width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,#4f46e5,#7c3aed);
                 display:flex;align-items:center;justify-content:center;color:white;font-weight:700;font-size:14px">G</div>
            <div>
                <div style="font-weight:600;font-size:13px;color:#1e293b">Guest Researcher</div>
                <div style="font-size:10px;color:#94a3b8">Bits in Bio CPH</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("⚙️ Settings"):
        st.checkbox("Dark mode evidence map", value=False, key="setting_dark_map")
        st.checkbox("Auto-save sessions", value=True, key="setting_autosave")
        st.selectbox("Chat style", ["Concise", "Detailed", "Bullet points"], key="setting_chat_style")

    st.caption("Built with ❤️ [Amass API](https://platform.amass.tech)")
    st.caption("🐙 [Viably on GitHub](https://github.com/aminrezaei-img/Bits-in-Bio-CPH)")


# ── Main layout ─────────────────────────────────────────────
left_col, right_col = st.columns([3, 1], gap="medium")

with left_col:
    # ── Viably header ──
    st.markdown("""
    <div class="viably-header">
        <span style="font-size:28px">🧬</span>
        <div>
            <h1>Viably</h1>
            <div class="tagline">Decide whether a bio project idea is worth pursuing — before spending weeks on it.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Input ──
    idea = st.text_area(
        "What's your project idea?",
        placeholder="Describe the target, intervention, disease area, or hypothesis...",
        height=100,
        key="idea_input",
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        assess = st.button("🔍 Assess Project", type="primary", use_container_width=True)

    # ── Results ──
    # Path 1: Demo button
    if st.session_state.get("run_demo"):
        demo_key = st.session_state.pop("run_demo")
        sc = get_demo_scenario(demo_key)
        if sc:
            st.success(f"📦 Loaded demo: **{sc['label']}**")
            errors = {}
            for core_name in ["biomedcore", "trialcore", "drugcore", "regulatorycore", "patentcore"]:
                if sc[core_name].get("error"):
                    errors[core_name] = sc[core_name]["error"]

            papers = sc["biomedcore"]["records"]
            trials = sc["trialcore"]["records"]
            drugs = sc["drugcore"]["records"]
            regulatory = sc["regulatorycore"]["records"]
            patents = sc["patentcore"]["records"]

            scores = render_assessment(
                papers, trials, drugs,
                regulatory=regulatory, patents=patents,
                errors=errors, idea=sc["idea"],
            )
            set_context(scores, sc["idea"], scores["counts"])
            save_session(sc["idea"], scores, papers, trials, drugs, regulatory, patents)

    # Path 2: User query
    elif assess and idea.strip():
        with st.spinner("Searching across studies, trials, interventions, regulatory, and patent records..."):
            results = cached_search(idea.strip(), limit=20)

        papers = results.get("biomedcore", {}).get("records", [])
        trials = results.get("trialcore", {}).get("records", [])
        drugs = results.get("drugcore", {}).get("records", [])
        regulatory = results.get("regulatorycore", {}).get("records", [])
        patents = results.get("patentcore", {}).get("records", [])

        if _all_failed(results):
            st.warning("⚠️ All API sources unavailable — showing cached demo data instead.")
            sc = get_demo_scenario("reframe")
            papers = sc["biomedcore"]["records"]
            trials = sc["trialcore"]["records"]
            drugs = sc["drugcore"]["records"]
            regulatory = sc["regulatorycore"]["records"]
            patents = sc["patentcore"]["records"]
            errors = {k: v.get("error", "API unavailable") for k, v in results.items() if v.get("error")}
        else:
            errors = {k: v["error"] for k, v in results.items() if v.get("error")}

        scores = render_assessment(
            papers, trials, drugs,
            regulatory=regulatory, patents=patents,
            errors=errors, idea=idea.strip(),
        )
        set_context(scores, idea.strip(), scores["counts"])
        save_session(idea.strip(), scores, papers, trials, drugs, regulatory, patents)

    elif assess and not idea.strip():
        st.warning("Please enter a project idea.")

    else:
        st.markdown("---")
        st.info("👆 Enter a project idea above and click **Assess Project** to get started — or pick a demo from the sidebar.")

        # How it works
        st.markdown("<div style='margin-top:24px'></div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(
                "<div style='background:#f8fafc;border-radius:10px;padding:20px;text-align:center;min-height:140px;display:flex;flex-direction:column;justify-content:center'>"
                "<div style='font-size:32px;margin-bottom:8px'>🔍</div>"
                "<div style='font-weight:600;color:#1e293b;margin-bottom:4px'>1. Describe</div>"
                "<div style='font-size:13px;color:#64748b'>Enter your project idea — target, intervention, disease, or hypothesis</div>"
                "</div>",
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                "<div style='background:#f8fafc;border-radius:10px;padding:20px;text-align:center;min-height:140px;display:flex;flex-direction:column;justify-content:center'>"
                "<div style='font-size:32px;margin-bottom:8px'>⚡</div>"
                "<div style='font-weight:600;color:#1e293b;margin-bottom:4px'>2. Assess</div>"
                "<div style='font-size:13px;color:#64748b'>We check 5 evidence sources — papers, trials, drugs, regulatory, patents</div>"
                "</div>",
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                "<div style='background:#f8fafc;border-radius:10px;padding:20px;text-align:center;min-height:140px;display:flex;flex-direction:column;justify-content:center'>"
                "<div style='font-size:32px;margin-bottom:8px'>💡</div>"
                "<div style='font-weight:600;color:#1e293b;margin-bottom:4px'>3. Decide</div>"
                "<div style='font-size:13px;color:#64748b'>Get a clear verdict: Proceed, Review carefully, or Reframe</div>"
                "</div>",
                unsafe_allow_html=True,
            )

        st.markdown("<div style='margin-top:28px'></div>", unsafe_allow_html=True)

        # Source badges
        st.caption("Powered by 5 evidence sources:")
        cols = st.columns(5)
        sources = [
            ("📄", "Literature", "#4f46e5"),
            ("🔬", "Trials", "#0891b2"),
            ("💊", "Drugs", "#7c3aed"),
            ("🏛️", "Regulatory", "#b45309"),
            ("📜", "Patents", "#059669"),
        ]
        for i, (icon, name, color) in enumerate(sources):
            with cols[i]:
                st.markdown(
                    f"<div style='text-align:center;font-size:13px;font-weight:500;color:{color}'>{icon} {name}</div>",
                    unsafe_allow_html=True,
                )

        with st.expander("💡 Example queries to try"):
            st.markdown("""
            - **CAR-T therapy for solid tumors** → expect *Reframe*
            - **CRISPR-based microbiome editing for depression** → expect *Proceed*
            - **GLP-1 receptor agonist for Alzheimer's** → expect *Review carefully*
            """)

    # Restore from session if clicked in sidebar (after rerun)
    active = get_active_session()
    if active and not assess and not st.session_state.get("run_demo"):
        st.markdown("---")
        st.info(f"📋 Viewing saved session: **{active['query'][:60]}** — {active['recommendation']}")
        # We can't re-render the full assessment without re-running the API,
        # but we show the saved context. For full restore, we'd need to store
        # the full record lists. For now, the context is in the chat panel.
        set_context(
            {"recommendation": active["recommendation"], "rationale": "",
             "studied_before": active["scores"]["studied_before"],
             "tested_in_practice": active["scores"]["tested_in_practice"],
             "translation_signal": active["scores"]["translation_signal"],
             "competitive_pressure": active["scores"]["competitive_pressure"],
             "failure_signal": "Low", "low_data": False},
            active["query"],
            active["scores"]["counts"],
        )

# ── Right panel: Chat ───────────────────────────────────────
with right_col:
    render_chat_panel()
