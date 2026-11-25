"""Cached Streamlit resource factory for Groq LLMs (primary + free-tier fallback)."""
import streamlit as st
from langchain_groq import ChatGroq

from src.config import GROQ_API_KEY, GROQ_MODEL, GROQ_FALLBACK_MODEL, MAX_RESPONSE_TOKENS


def _make(model: str) -> ChatGroq:
    return ChatGroq(
        model=model,
        api_key=GROQ_API_KEY,
        temperature=0.7,
        max_tokens=MAX_RESPONSE_TOKENS,  # caps token spend per reply
        max_retries=0,                   # retries handled by tenacity / fallback
        **({"reasoning_effort": "low"} if "gpt-oss" in model else {}),  # fewer hidden tokens
    )


@st.cache_resource
def get_llm() -> ChatGroq:
    return _make(GROQ_MODEL)


@st.cache_resource
def get_fallback_llm() -> ChatGroq:
    return _make(GROQ_FALLBACK_MODEL)
