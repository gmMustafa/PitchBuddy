"""PitchBuddy — Streamlit entry point."""
import streamlit as st

from src.ui.styles import STYLES
from src.ui.auth import require_login, render_user_info
from src.ui.session import init_session, process_input, load_conversation
from src.ui.sidebar import render_sidebar
from src.ui.chat import render_welcome_screen, render_chat_history
from src.ui.input_bar import render_input_bar

_HEADER_HTML = """
<div class="app-header">
    <h1>PitchBuddy</h1>
    <p>Practice your startup pitch with an AI-powered VC — get challenged, get sharp, get funded.</p>
    <span class="badge">Elevator Pitch</span>
    <span class="badge">TAM / SAM / SOM</span>
    <span class="badge">Business Model</span>
    <span class="badge">Traction & Metrics</span>
    <span class="badge">Funding Ask</span>
    <span class="badge">Powered by Gemini</span>
</div>
"""


def main() -> None:
    st.set_page_config(
        page_title="PitchBuddy",
        page_icon="🚀",
        layout="centered",
    )

    # ── Inject CSS early so login page is also styled ─────────────
    st.markdown(STYLES, unsafe_allow_html=True)

    # ── Auth gate — stops here if not signed in ───────────────────
    user_id = require_login()

    init_session()

    # ── Handle pending conversation load (before widgets render) ──
    if "_load_conv_id" in st.session_state:
        conv_id = st.session_state.pop("_load_conv_id")
        with st.spinner("Loading conversation…"):
            load_conversation(user_id, conv_id)

    # ── Handle pending suggestion-card clicks ─────────────────────
    if st.session_state.suggestion_pending:
        pending = st.session_state.suggestion_pending
        st.session_state.suggestion_pending = None
        process_input(pending, user_id)
        st.rerun()

    # ── Sidebar ───────────────────────────────────────────────────
    render_user_info()
    render_sidebar(user_id)

    # ── Header ───────────────────────────────────────────────────
    st.html(_HEADER_HTML)

    # ── Chat ──────────────────────────────────────────────────────
    render_welcome_screen()
    render_chat_history()
    render_input_bar(user_id)


if __name__ == "__main__":
    main()
