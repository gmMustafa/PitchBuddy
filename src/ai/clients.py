"""Cached Streamlit resource factory for Google Gemini."""
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI

from src.config import GOOGLE_API_KEY


@st.cache_resource
def get_llm() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=GOOGLE_API_KEY,
        temperature=0.7,
        thinking_budget=0,
    )
