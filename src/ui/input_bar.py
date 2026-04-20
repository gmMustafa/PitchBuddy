"""Bottom input bar: multiline textarea, submit via ➤ button."""
import streamlit as st

from src.ui.session import process_input


def render_input_bar(user_id: str) -> None:
    st.divider()

    with st.form("text_form", clear_on_submit=True):
        c1, c2 = st.columns([0.93, 0.07])
        with c1:
            user_text = st.text_area(
                "msg",
                placeholder="Type your message…",
                label_visibility="collapsed",
                height=80,
                key="chat_textarea",
            )
        with c2:
            submitted = st.form_submit_button("➤")

    if submitted and user_text and user_text.strip():
        process_input(user_text.strip(), user_id)
        st.rerun()
