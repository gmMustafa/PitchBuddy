"""Firestore persistence: user-scoped conversations + messages."""
import uuid
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

from src.config import FIREBASE_CREDENTIALS_PATH


@st.cache_resource
def get_db():
    if not firebase_admin._apps:
        cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred)
    return firestore.client()


def _convs(user_id: str):
    """Conversations collection scoped to a specific user."""
    return (
        get_db()
        .collection("users")
        .document(user_id)
        .collection("conversations")
    )


def new_conv_id() -> str:
    return str(uuid.uuid4())


def create_conversation(user_id: str, conv_id: str, title: str, persona: str = "", stage: str = "") -> None:
    _convs(user_id).document(conv_id).set({
        "title":      title,
        "persona":    persona,
        "stage":      stage,
        "created_at": firestore.SERVER_TIMESTAMP,
        "updated_at": firestore.SERVER_TIMESTAMP,
    })


def get_conversation_meta(user_id: str, conv_id: str) -> dict:
    doc = _convs(user_id).document(conv_id).get()
    return doc.to_dict() if doc.exists else {}


def save_message(user_id: str, conv_id: str, role: str, content: str) -> None:
    _convs(user_id).document(conv_id).collection("messages").add({
        "role":    role,
        "content": content,
        "ts":      firestore.SERVER_TIMESTAMP,
    })
    _convs(user_id).document(conv_id).update({
        "updated_at": firestore.SERVER_TIMESTAMP,
    })


def list_conversations(user_id: str, limit: int = 20) -> list[dict]:
    docs = (
        _convs(user_id)
        .order_by("updated_at", direction=firestore.Query.DESCENDING)
        .limit(limit)
        .stream()
    )
    return [{"id": doc.id, **doc.to_dict()} for doc in docs]


def load_messages(user_id: str, conv_id: str) -> list[dict]:
    docs = (
        _convs(user_id)
        .document(conv_id)
        .collection("messages")
        .order_by("ts")
        .stream()
    )
    return [{"role": d["role"], "content": d["content"]} for d in (doc.to_dict() for doc in docs)]


def delete_conversation(user_id: str, conv_id: str) -> None:
    for msg in _convs(user_id).document(conv_id).collection("messages").stream():
        msg.reference.delete()
    _convs(user_id).document(conv_id).delete()
