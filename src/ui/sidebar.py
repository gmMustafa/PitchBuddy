"""Sidebar: new chat + conversation history."""
import streamlit as st

from src.config import INVESTOR_PERSONAS, STAGES
from src.db.firestore import list_conversations, delete_conversation
from src.ui.session import new_conversation


def render_sidebar(user_id: str) -> None:
    with st.sidebar:
        st.markdown(
            "<div style='padding:6px 0 16px; font-size:1.1rem; font-weight:800;"
            " color:#0F172A; letter-spacing:-0.4px;'>✦ PitchBuddy</div>",
            unsafe_allow_html=True,
        )

        if st.button("＋  New Chat", use_container_width=True, type="primary"):
            new_conversation()
            st.rerun()

        st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)

        st.selectbox(
            "Investor persona",
            options=list(INVESTOR_PERSONAS.keys()),
            key="persona",
            help="Changes how the AI investor thinks and challenges you",
        )

        persona_desc = INVESTOR_PERSONAS[st.session_state.persona]
        st.markdown(
            f"<div style='font-size:0.75rem; color:#94A3B8; margin:-6px 0 12px;"
            f" line-height:1.4;'>{persona_desc}</div>",
            unsafe_allow_html=True,
        )

        st.selectbox(
            "Founder stage",
            options=STAGES,
            key="stage",
            help="Adjusts how hard the VC pushes back on your answers",
        )

        st.markdown("<div style='margin-top:4px;'></div>", unsafe_allow_html=True)

        st.markdown(
            "<div style='margin-top:22px; margin-bottom:6px; font-size:0.68rem;"
            " font-weight:600; color:#94A3B8; text-transform:uppercase;"
            " letter-spacing:0.09em;'>Recents</div>",
            unsafe_allow_html=True,
        )

        try:
            convs = list_conversations(user_id, limit=25)
        except Exception:
            convs = []

        if not convs:
            st.caption("No conversations yet.")
        else:
            current_id = st.session_state.get("conv_id")
            for conv in convs:
                cid    = conv["id"]
                raw    = conv.get("title", "Untitled")
                title  = (raw[:30] + "…") if len(raw) > 30 else raw
                active = cid == current_id
                label  = f"{'● ' if active else ''}{title}"

                col1, col2 = st.columns([0.84, 0.16])
                with col1:
                    if st.button(label, key=f"conv_{cid}", use_container_width=True):
                        if not active:
                            st.session_state._load_conv_id = cid
                            st.rerun()
                with col2:
                    if st.button("✕", key=f"del_{cid}", help="Delete"):
                        delete_conversation(user_id, cid)
                        if active:
                            new_conversation()
                        st.rerun()
