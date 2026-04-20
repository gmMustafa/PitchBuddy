"""Cached Streamlit resource factory for Groq LLM."""
import streamlit as st
from langchain_groq import ChatGroq

from src.config import GROQ_API_KEY


@st.cache_resource
def get_llm() -> ChatGroq:
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=GROQ_API_KEY,
        temperature=0.7,
    )
