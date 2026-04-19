"""Anonymous session-based user isolation — one UUID per browser session."""
import uuid
import streamlit as st


def require_login() -> str:
    """Returns a stable anonymous user_id for this browser session."""
    if "user_id" not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())
    return st.session_state.user_id


def render_user_info() -> None:
    """Nothing to render for anonymous sessions."""
    pass
