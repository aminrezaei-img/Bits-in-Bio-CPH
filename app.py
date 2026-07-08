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

# ── Design system: ported from frontend prototype ────────────
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  /* ── Base ── */
  .stApp { background: #F5F3EE; }
  .stMainBlockContainer { background: #F5F3EE; padding-top: 2rem; }

  /* ── Typography ── */
  h1, h2, h3 { font-family: 'Newsreader', Georgia, serif !important; font-weight: 500 !important; letter-spacing: -0.01em !important; }
  h1 { font-size: 38px !important; }
  h2 { font-size: 22px !important; }
  body, p, .stMarkdown, .stCaption { font-family: 'IBM Plex Sans', system-ui, sans-serif !important; color: #3A382F; }
  .st-cb, .st-cd, .st-ce { font-family: 'IBM Plex Mono', monospace !important; font-size: 11px !important; letter-spacing: 0.12em !important; text-transform: uppercase !important; color: #8C877D !important; }

  /* ── Viably header ── */
  .viably-header {
    display: flex; flex-direction: column; gap: 6px;
    padding: 0 0 20px 0; border-bottom: 1px solid #E4E1D9; margin-bottom: 24px;
  }
  .viably-header .mono-label {
    font-family: 'IBM Plex Mono', monospace; font-size: 11px;
    letter-spacing: 0.18em; text-transform: uppercase; color: #8C877D;
  }

  /* ── Cards ── */
  .ev-card {
    background: #FFFFFF; border: 1px solid #E4E1D9; border-radius: 10px;
    padding: 18px; display: flex; flex-direction: column; gap: 10px;
  }

  /* ── Verdict card ── */
  .verdict-card {
    background: #FFFFFF; border: 1px solid #E4E1D9; border-radius: 12px;
    overflow: hidden; display: flex; margin-bottom: 24px;
  }
  .verdict-bar { width: 6px; flex: none; }
  .verdict-body { padding: 24px 28px; flex: 1; }

  /* ── Evidence section ── */
  .evidence-section-title {
    font-family: 'Newsreader', Georgia, serif; font-weight: 500;
    font-size: 22px; margin: 0 0 16px 0; letter-spacing: -0.01em;
  }

  /* ── Input card ── */
  .input-card {
    background: #FFFFFF; border: 1px solid #E4E1D9; border-radius: 10px;
    padding: 20px; margin-bottom: 24px;
  }

  /* ── Sidebar ── */
  section[data-testid="stSidebar"] {
    background: #FBFAF7; border-right: 1px solid #E4E1D9;
  }

  /* ── Buttons ── */
  .stButton > button {
    font-family: 'IBM Plex Sans', sans-serif !important; font-weight: 600 !important;
    font-size: 13.5px !important; background: #1C1B19 !important; color: #F5F3EE !important;
    border: none !important; border-radius: 7px !important; padding: 11px 20px !important;
  }
  .stButton > button:hover { background: #000000 !important; }

  /* ── Profile ── */
  .profile-section {
    background: #FFFFFF; border: 1px solid #E4E1D9; border-radius: 10px;
    padding: 12px; margin-top: 16px;
  }

  /* ── Dataframe / table ── */
  .stDataFrame { border: 1px solid #E4E1D9 !important; border-radius: 10px !important; }
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
        "Proceed": "#2F7A50",
        "Review carefully": "#B8862F",
        "Reframe": "#A8552B",
    }.get(scores["recommendation"], "#6b7280")

    rec_summary = {
        "Proceed": "Low crowding · weak prior signal",
        "Review carefully": "Meaningful prior activity",
        "Reframe": "Crowded · tested · repeated stop signals",
    }.get(scores["recommendation"], "")

    st.markdown("---")
    st.markdown(
        f"""
        <div class="verdict-card">
            <div class="verdict-bar" style="background:{rec_color}"></div>
            <div class="verdict-body">
                <div style="font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:0.18em;text-transform:uppercase;color:#8C877D;margin-bottom:8px">Recommendation</div>
                <div style="display:flex;align-items:baseline;gap:16px;flex-wrap:wrap;margin-bottom:10px">
                    <div style="font-family:'Newsreader',Georgia,serif;font-weight:500;font-size:44px;line-height:1;letter-spacing:-0.015em;color:{rec_color}">{scores['recommendation']}</div>
                    <div style="font-family:'IBM Plex Mono',monospace;font-size:12px;color:#8C877D">{rec_summary}</div>
                </div>
                <p style="margin:0;font-size:16px;line-height:1.5;color:#3A382F;max-width:64ch;font-family:'IBM Plex Sans',sans-serif">{scores['rationale']}</p>
            </div>
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
        "<span style='font-size:24px;font-weight:800;color:#1e293b'>🧬 Viably</span>"
        "<div style='font-size:11px;color:#94a3b8;margin-top:2px'>Evidence-based project triage</div>"
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

    st.caption("Built with [Amass API](https://platform.amass.tech)")
    st.caption("[Viably on GitHub](https://github.com/aminrezaei-img/Bits-in-Bio-CPH)")


# ── Main layout ─────────────────────────────────────────────
left_col, right_col = st.columns([3, 1], gap="medium")

with left_col:
    # ── Viably header ──
    st.markdown("""
    <div class="viably-header">
        <div class="mono-label">Decision brief</div>
        <h1 style="margin:0;color:#1C1B19">Viably</h1>
        <p style="margin:0;font-size:15px;color:#6E6B64;max-width:52ch;font-family:'IBM Plex Sans',sans-serif">
            Decide whether a bio project idea is worth pursuing — before spending weeks on it.
        </p>
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

    # ── Footer ──
    st.markdown("---")
    st.markdown("""
    <footer style="display:flex;flex-direction:column;gap:6px;padding-top:4px">
        <p style="margin:0;font-size:13px;color:#6E6B64;max-width:70ch;font-family:'IBM Plex Sans',sans-serif">
            Viably turns scattered evidence into a first-pass project decision. It does not replace expert review.
        </p>
        <p style="margin:0;font-size:11px;color:#A8A498;font-family:'IBM Plex Mono',monospace">
            Recommendation grounded in retrieved records · LLM used only to phrase the brief
        </p>
    </footer>
    """, unsafe_allow_html=True)

# ── Right panel: Chat ───────────────────────────────────────
with right_col:
    render_chat_panel()
