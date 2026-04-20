"""Storage router: delegates to Firestore (logged-in) or session_store (guest)."""
import streamlit as st
from src.db import firestore, session_store


def _b():
    return session_store if st.session_state.get("is_guest") else firestore


def new_conv_id() -> str:
    return _b().new_conv_id()


def create_conversation(user_id: str, conv_id: str, title: str, persona: str = "", stage: str = "") -> None:
    _b().create_conversation(user_id, conv_id, title, persona, stage)


def get_conversation_meta(user_id: str, conv_id: str) -> dict:
    return _b().get_conversation_meta(user_id, conv_id)


def save_message(user_id: str, conv_id: str, role: str, content: str) -> None:
    _b().save_message(user_id, conv_id, role, content)


def list_conversations(user_id: str, limit: int = 20) -> list[dict]:
    return _b().list_conversations(user_id, limit)


def load_messages(user_id: str, conv_id: str) -> list[dict]:
    return _b().load_messages(user_id, conv_id)


def delete_conversation(user_id: str, conv_id: str) -> None:
    _b().delete_conversation(user_id, conv_id)
