"""
Chat panel for Viably — discuss assessment results with context-aware responses.
Uses template-based responses for demo reliability; pluggable LLM hook.
"""
import streamlit as st
from chat_engine import generate_response


def init_chat():
    """Initialize chat session state if not present."""
    if "viably_chat" not in st.session_state:
        st.session_state.viably_chat = []
    if "viably_context" not in st.session_state:
        st.session_state.viably_context = {}


def set_context(scores: dict, idea: str, counts: dict):
    """Store the latest assessment context for the chat to reference."""
    st.session_state.viably_context = {
        "idea": idea,
        "recommendation": scores["recommendation"],
        "rationale": scores["rationale"],
        "studied_before": scores["studied_before"],
        "tested_in_practice": scores["tested_in_practice"],
        "translation_signal": scores["translation_signal"],
        "competitive_pressure": scores["competitive_pressure"],
        "failure_signal": scores["failure_signal"],
        "counts": counts,
    }


def render_chat_panel():
    """Render the right-side chat panel with collapse toggle."""
    init_chat()
    if "viably_chat_collapsed" not in st.session_state:
        st.session_state.viably_chat_collapsed = False

    # Collapse toggle button
    if st.session_state.viably_chat_collapsed:
        if st.button("💬 Open Chat", use_container_width=True):
            st.session_state.viably_chat_collapsed = False
            st.rerun()
        return

    with st.container(border=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown("### 💬 Discuss Results")
        with col2:
            if st.button("✕", help="Hide chat panel", key="collapse_chat"):
                st.session_state.viably_chat_collapsed = True
                st.rerun()

        # Context status
        ctx = st.session_state.viably_context
        if ctx:
            st.caption(
                f"Context: **{ctx['recommendation']}** — "
                f"{ctx['counts']['papers']}p/{ctx['counts']['trials']}t/{ctx['counts']['drugs']}d"
            )
        else:
            st.caption("Run an assessment to start chatting about the results.")

        # Chat messages
        chat_container = st.container(height=350)
        with chat_container:
            for msg in st.session_state.viably_chat:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        # Input
        if prompt := st.chat_input("Ask about the results...", key="viably_chat_input"):
            st.session_state.viably_chat.append({"role": "user", "content": prompt})
            response = generate_response(prompt, st.session_state.viably_context)
            st.session_state.viably_chat.append({"role": "assistant", "content": response})
            st.rerun()
