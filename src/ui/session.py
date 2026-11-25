"""Session state initialisation, chat management, and input processing."""
import re
import streamlit as st

from src.ai.agent import get_ai_response
from src.config import MAX_MESSAGES_PER_SESSION
from src.utils.retry import is_rate_limit
from src.db.store import (
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


def _user_turns() -> int:
    return sum(1 for m in st.session_state.messages if m["role"] == "user")


def process_input(user_input: str, user_id: str) -> None:
    # Free-tier guard: one shared API key serves every public visitor.
    if _user_turns() >= MAX_MESSAGES_PER_SESSION:
        st.session_state.flash = (
            f"You've reached the {MAX_MESSAGES_PER_SESSION}-message limit for this session. "
            "Start a new chat to keep practising."
        )
        return

    if st.session_state.conv_id is None:
        st.session_state.conv_id = new_conv_id()
        create_conversation(
            user_id,
            st.session_state.conv_id,
            _make_title(user_input),
            persona=st.session_state.get("persona", "Seed VC"),
            stage=st.session_state.get("stage", "🌱 Pre-Seed"),
        )

    history = list(st.session_state.messages)  # prior turns only (excludes this input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    save_message(user_id, st.session_state.conv_id, "user", user_input)

    try:
        with st.spinner("Thinking…"):
            ai_reply = get_ai_response(
                user_input,
                history,
                persona=st.session_state.get("persona", "Seed VC"),
                stage=st.session_state.get("stage", "🌱 Pre-Seed"),
            )
    except Exception as exc:
        st.session_state.messages.pop()  # drop the unanswered turn so history stays alternating
        st.session_state.flash = (
            "The AI is busy right now (free-tier rate limit reached). Please wait a minute and try again."
            if is_rate_limit(exc)
            else f"Something went wrong talking to the AI: {exc}"
        )
        return

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
