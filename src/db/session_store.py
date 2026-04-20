"""In-memory conversation store for guest sessions (tab-scoped, no persistence)."""
import uuid
import streamlit as st


def _store() -> dict:
    if "guest_store" not in st.session_state:
        st.session_state.guest_store = {"conversations": {}, "messages": {}}
    return st.session_state.guest_store


def new_conv_id() -> str:
    return str(uuid.uuid4())


def create_conversation(user_id: str, conv_id: str, title: str, persona: str = "", stage: str = "") -> None:
    _store()["conversations"][conv_id] = {
        "id": conv_id, "title": title, "persona": persona, "stage": stage,
    }
    _store()["messages"][conv_id] = []


def get_conversation_meta(user_id: str, conv_id: str) -> dict:
    return _store()["conversations"].get(conv_id, {})


def save_message(user_id: str, conv_id: str, role: str, content: str) -> None:
    msgs = _store()["messages"]
    if conv_id not in msgs:
        msgs[conv_id] = []
    msgs[conv_id].append({"role": role, "content": content})


def list_conversations(user_id: str, limit: int = 20) -> list[dict]:
    convs = list(_store()["conversations"].values())
    return convs[::-1][:limit]


def load_messages(user_id: str, conv_id: str) -> list[dict]:
    return _store()["messages"].get(conv_id, [])


def delete_conversation(user_id: str, conv_id: str) -> None:
    _store()["conversations"].pop(conv_id, None)
    _store()["messages"].pop(conv_id, None)
