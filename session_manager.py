"""
Session manager for Viably — save, restore, and navigate past assessments.
Persists in st.session_state. Client-side only (survives reruns, not browser refreshes).
"""
import streamlit as st
import time
from typing import Any


def init_sessions():
    """Initialize session storage if not present."""
    if "viably_sessions" not in st.session_state:
        st.session_state.viably_sessions = []
    if "viably_active_session" not in st.session_state:
        st.session_state.viably_active_session = None


def save_session(idea: str, scores: dict, papers, trials, drugs, regulatory, patents):
    """Save the current assessment as a named session."""
    init_sessions()
    session = {
        "id": f"sess_{int(time.time())}",
        "query": idea,
        "recommendation": scores["recommendation"],
        "scores": {
            "studied_before": scores["studied_before"],
            "tested_in_practice": scores["tested_in_practice"],
            "translation_signal": scores["translation_signal"],
            "competitive_pressure": scores["competitive_pressure"],
            "counts": dict(scores["counts"]),
        },
        "papers": papers,
        "trials": trials,
        "drugs": drugs,
        "regulatory": regulatory,
        "patents": patents,
        "timestamp": time.strftime("%H:%M"),
    }
    # Avoid duplicates — replace if same query
    existing = [s for s in st.session_state.viably_sessions if s["query"] != idea]
    st.session_state.viably_sessions = [session] + existing
    # Keep max 10 sessions
    st.session_state.viably_sessions = st.session_state.viably_sessions[:10]
    st.session_state.viably_active_session = session["id"]


def get_sessions() -> list[dict]:
    """Return all saved sessions, newest first."""
    init_sessions()
    return st.session_state.viably_sessions


def get_active_session() -> dict | None:
    """Return the currently active session data."""
    init_sessions()
    active_id = st.session_state.viably_active_session
    if active_id:
        for s in st.session_state.viably_sessions:
            if s["id"] == active_id:
                return s
    return None


def restore_session(session_id: str):
    """Set a session as active (for chat context)."""
    init_sessions()
    st.session_state.viably_active_session = session_id


def delete_session(session_id: str):
    """Remove a session from storage."""
    init_sessions()
    st.session_state.viably_sessions = [
        s for s in st.session_state.viably_sessions if s["id"] != session_id
    ]
    if st.session_state.viably_active_session == session_id:
        st.session_state.viably_active_session = None


def render_session_sidebar():
    """Render the session navigation section in the sidebar."""
    init_sessions()
    sessions = get_sessions()

    if sessions:
        st.markdown("#### 📋 Recent Sessions")
        for i, sess in enumerate(sessions[:8]):
            query_short = sess["query"][:45] + ("…" if len(sess["query"]) > 45 else "")
            rec_emoji = {"Proceed": "🟢", "Review carefully": "🟡", "Reframe": "🔴"}.get(
                sess["recommendation"], "⚪"
            )
            is_active = st.session_state.viably_active_session == sess["id"]

            col1, col2 = st.columns([5, 1])
            with col1:
                label = f"{rec_emoji} {query_short}"
                if is_active:
                    label = f"**{label}** *(active)*"
                if st.button(
                    label,
                    key=f"session_{sess['id']}",
                    use_container_width=True,
                    type="secondary" if not is_active else "primary",
                ):
                    restore_session(sess["id"])
                    st.rerun()
            with col2:
                if st.button("✕", key=f"del_{sess['id']}", help="Delete this session"):
                    delete_session(sess["id"])
                    st.rerun()
            st.caption(f"   {sess['timestamp']} — {sess['recommendation']}")

    else:
        st.caption("No sessions yet. Run an assessment to save it here.")
