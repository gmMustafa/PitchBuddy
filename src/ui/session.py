"""Session state initialisation, chat management, and input processing."""
import re
import streamlit as st

from src.ai.agent import get_ai_response
from src.db.firestore import (
    new_conv_id,
    create_conversation,
    get_conversation_meta,
    save_message,
    load_messages as _load_messages,
)


def init_session() -> None:
    defaults: dict = {
        "messages":           [],
        "suggestion_pending": None,
        "conv_id":            None,
        "persona":            "Seed VC",
        "stage":              "🌱 Pre-Seed",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def _make_title(text: str) -> str:
    text = re.sub(r'^(I\'m |I am |I |We |Our |My )', '', text.strip(), flags=re.IGNORECASE)
    text = re.sub(r'[^\w\s\-]', '', text)
    words = text.split()
    title = ' '.join(words[:6]).strip()
    return title.capitalize() if title else "New conversation"


def process_input(user_input: str, user_id: str) -> None:
    if st.session_state.conv_id is None:
        st.session_state.conv_id = new_conv_id()
        create_conversation(
            user_id,
            st.session_state.conv_id,
            _make_title(user_input),
            persona=st.session_state.get("persona", "Seed VC"),
            stage=st.session_state.get("stage", "🌱 Pre-Seed"),
        )

    st.session_state.messages.append({"role": "user", "content": user_input})
    save_message(user_id, st.session_state.conv_id, "user", user_input)

    with st.spinner("Thinking…"):
        ai_reply = get_ai_response(
            user_input,
            st.session_state.messages,
            persona=st.session_state.get("persona", "Seed VC"),
            stage=st.session_state.get("stage", "🌱 Pre-Seed"),
        )

    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
    save_message(user_id, st.session_state.conv_id, "assistant", ai_reply)


def load_conversation(user_id: str, conv_id: str) -> None:
    meta = get_conversation_meta(user_id, conv_id)
    st.session_state.conv_id            = conv_id
    st.session_state.messages           = _load_messages(user_id, conv_id)
    st.session_state.suggestion_pending = None
    if meta.get("persona"):
        st.session_state.persona = meta["persona"]
    if meta.get("stage"):
        st.session_state.stage = meta["stage"]


def new_conversation() -> None:
    st.session_state.conv_id = None
    st.session_state.messages = []
    st.session_state.suggestion_pending = None


def clear_chat() -> None:
    new_conversation()
