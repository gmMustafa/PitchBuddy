"""Global CSS injected once per page load."""

STYLES = """
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ── Font ── */
html {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
body, p, div, h1, h2, h3, h4, h5, h6, li, label, input, textarea, button, select, a, td, th {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer { visibility: hidden; }

/* ── Global background & layout ── */
.stApp { background: #F8FAFC; }
.block-container {
    max-width: 960px;
    padding-top: 2rem;
    padding-bottom: 9rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

/* ════════════════════════════════════════
   SIDEBAR
   ════════════════════════════════════════ */
[data-testid="stSidebar"] > div:first-child {
    background: #F1F5F9;
    border-right: 1px solid #E2E8F0;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #0F172A !important; }
[data-testid="stSidebar"] hr  { border-color: #E2E8F0 !important; }
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span { color: #64748B !important; }

/* "RECENTS" section label */
[data-testid="stSidebar"] strong {
    color: #94A3B8 !important;
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.09em;
}

/* Caption (empty state) */
[data-testid="stSidebar"] .stCaption p { color: #94A3B8 !important; font-size: 0.8rem !important; }

/* Brand */
[data-testid="stSidebar"] h2 {
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.2px;
    color: #0F172A !important;
}

/* ── New Chat button (primary) ── */
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] {
    background: #6366F1 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.83rem !important;
    padding: 9px 14px !important;
    letter-spacing: 0.01em !important;
    box-shadow: 0 1px 3px rgba(99,102,241,0.25) !important;
    transition: background 0.15s, box-shadow 0.15s !important;
}
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"]:hover {
    background: #4F46E5 !important;
    box-shadow: 0 4px 12px rgba(99,102,241,0.30) !important;
}
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] p,
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] span {
    color: #ffffff !important;
}

/* ── Conversation items (secondary) ── */
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] {
    background: transparent !important;
    color: #334155 !important;
    border: none !important;
    border-radius: 8px !important;
    text-align: left !important;
    font-size: 0.83rem !important;
    font-weight: 450 !important;
    padding: 8px 12px !important;
    transition: background 0.15s, color 0.15s !important;
    line-height: 1.4 !important;
    overflow: hidden !important;
}
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] p {
    text-align: left !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    margin: 0 !important;
    color: inherit !important;
}
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:hover {
    background: #EEF2FF !important;
    color: #4338CA !important;
}

/* ── Delete button — invisible until row hover ── */
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] [data-testid="stColumn"]:last-child [data-testid="stBaseButton-secondary"] {
    opacity: 0 !important;
    font-size: 0.68rem !important;
    padding: 5px 4px !important;
    transition: opacity 0.15s, color 0.12s, background 0.12s !important;
}
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"]:hover [data-testid="stColumn"]:last-child [data-testid="stBaseButton-secondary"] {
    opacity: 1 !important;
    color: #94A3B8 !important;
    background: transparent !important;
}
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"]:hover [data-testid="stColumn"]:last-child [data-testid="stBaseButton-secondary"]:hover {
    background: #FEE2E2 !important;
    color: #DC2626 !important;
}

/* ════════════════════════════════════════
   APP HEADER
   ════════════════════════════════════════ */
.app-header {
    background: #ffffff;
    border: 1px solid #E2E8F0;
    border-radius: 18px;
    padding: 32px 36px 28px;
    margin-bottom: 28px;
    box-shadow: 0 1px 3px rgba(15,23,42,0.04), 0 4px 20px rgba(15,23,42,0.03);
    position: relative;
    overflow: hidden;
}
.app-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #6366F1, #8B5CF6, #A78BFA);
    border-radius: 18px 18px 0 0;
}
.app-header h1 {
    margin: 0 0 8px;
    font-size: 1.8rem;
    font-weight: 800;
    color: #0F172A;
    letter-spacing: -0.6px;
    line-height: 1.2;
}
.app-header p {
    margin: 0 0 18px;
    font-size: 0.92rem;
    color: #64748B;
    line-height: 1.6;
    font-weight: 400;
}
.app-header .badge {
    display: inline-block;
    background: #EEF2FF;
    border: 1px solid #C7D2FE;
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.72rem;
    font-weight: 500;
    color: #4F46E5;
    margin-right: 6px;
    margin-bottom: 5px;
    letter-spacing: 0.01em;
}
.app-header .badge:hover {
    background: #E0E7FF;
    border-color: #A5B4FC;
}

/* ════════════════════════════════════════
   SUGGESTION CARDS
   ════════════════════════════════════════ */
[data-testid="stMain"] [data-testid="stBaseButton-secondary"] {
    background: #ffffff !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 14px !important;
    text-align: left !important;
    padding: 16px 18px !important;
    min-height: 68px !important;
    height: auto !important;
    font-size: 0.88rem !important;
    white-space: normal !important;
    line-height: 1.55 !important;
    color: #374151 !important;
    font-weight: 500 !important;
    box-shadow: 0 1px 3px rgba(15,23,42,0.04) !important;
    transition: border-color 0.15s, box-shadow 0.15s, transform 0.12s !important;
}
[data-testid="stMain"] [data-testid="stBaseButton-secondary"]:hover {
    border-color: #A5B4FC !important;
    box-shadow: 0 4px 20px rgba(99,102,241,0.10) !important;
    transform: translateY(-2px) !important;
    background: #FAFAFE !important;
    color: #1F2937 !important;
}

/* "Try asking…" label */
[data-testid="stMain"] h4 {
    color: #94A3B8 !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    margin-bottom: 14px !important;
}

/* ════════════════════════════════════════
   CHAT MESSAGES
   ════════════════════════════════════════ */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 4px 0;
}

/* User bubble */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {
    background: #EEF2FF !important;
    border: 1px solid #C7D2FE !important;
}

/* Assistant bubble */
[data-testid="stChatMessageContent"] {
    background: #ffffff !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 14px !important;
    padding: 16px 20px !important;
    box-shadow: 0 1px 4px rgba(15,23,42,0.04);
    line-height: 1.75;
    font-size: 0.94rem;
    color: #1F2937 !important;
}

/* ════════════════════════════════════════
   INPUT FORM
   ════════════════════════════════════════ */
[data-testid="stHorizontalBlock"] { align-items: flex-end; }

div[data-testid="stForm"] {
    background: #ffffff;
    border: 1.5px solid #E2E8F0;
    border-radius: 18px;
    padding: 6px 10px 6px 18px;
    box-shadow: 0 1px 4px rgba(15,23,42,0.04);
    transition: border-color 0.2s, box-shadow 0.2s;
    margin: 0 !important;
}
div[data-testid="stForm"]:focus-within {
    border-color: #A5B4FC;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.08);
}

/* Textarea */
div[data-testid="stTextArea"] textarea {
    border: none !important;
    box-shadow: none !important;
    background: transparent !important;
    font-size: 0.94rem !important;
    color: #0F172A !important;
    padding: 6px 4px;
    resize: none;
    line-height: 1.6;
}
div[data-testid="stTextArea"] textarea::placeholder { color: #CBD5E1 !important; }
div[data-testid="stTextArea"] > div,
div[data-testid="stTextArea"] > div > div {
    border: none !important;
    box-shadow: none !important;
    background: transparent !important;
}

/* Send button */
div[data-testid="stFormSubmitButton"] > button {
    border: none !important;
    background: #6366F1 !important;
    box-shadow: 0 1px 3px rgba(99,102,241,0.25) !important;
    font-size: 1rem !important;
    padding: 8px 14px !important;
    border-radius: 12px !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    transition: background 0.15s, transform 0.1s !important;
    min-width: 40px;
}
div[data-testid="stFormSubmitButton"] > button:hover {
    background: #4F46E5 !important;
    transform: scale(1.04) !important;
}

/* ════════════════════════════════════════
   DIVIDER & SCROLLBAR
   ════════════════════════════════════════ */
[data-testid="stDivider"] hr {
    border-color: #F1F5F9 !important;
    margin: 12px 0 !important;
}

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #94A3B8; }

</style>
"""
