"""Chat area: welcome screen and message history."""
import streamlit as st

from src.config import SUGGESTION_PROMPTS


def render_welcome_screen() -> None:
    """Show clickable suggestion cards when the conversation is empty."""
    if st.session_state.messages:
        return

    st.markdown("#### Try asking…")
    cols = st.columns(2)
    for i, (icon, title, prompt) in enumerate(SUGGESTION_PROMPTS):
        with cols[i % 2]:
            if st.button(
                f"{icon}  {title}",
                key=f"sug_{i}",
                use_container_width=True,
            ):
                st.session_state.suggestion_pending = prompt
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)


def render_chat_history() -> None:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
