import os
from dotenv import load_dotenv

load_dotenv()


def _get(key: str, default: str = "") -> str:
    """Read from env first, then st.secrets (Streamlit Cloud)."""
    val = os.getenv(key, "")
    if val:
        return val
    try:
        import streamlit as st
        return st.secrets.get(key, default)
    except Exception:
        return default


# ── API ──────────────────────────────────────────────────────────────
GROQ_API_KEY: str = _get("GROQ_API_KEY")
FIREBASE_CREDENTIALS_PATH: str = _get("FIREBASE_CREDENTIALS", "firebase-credentials.json")
FIREBASE_CREDENTIALS_JSON: str = _get("FIREBASE_CREDENTIALS_JSON")

# ── Free-tier guards (all overridable via env / st.secrets) ──────────
# llama-3.x models were retired by Groq; gpt-oss are the current free production models.
GROQ_MODEL: str = _get("GROQ_MODEL", "openai/gpt-oss-120b")
GROQ_FALLBACK_MODEL: str = _get("GROQ_FALLBACK_MODEL", "openai/gpt-oss-20b")
# Reasoning tokens count toward this cap, so leave headroom above the visible reply.
MAX_RESPONSE_TOKENS: int = int(_get("MAX_RESPONSE_TOKENS", "900"))
MAX_HISTORY_MESSAGES: int = int(_get("MAX_HISTORY_MESSAGES", "12"))
MAX_MESSAGES_PER_SESSION: int = int(_get("MAX_MESSAGES_PER_SESSION", "40"))

# ── OAuth ─────────────────────────────────────────────────────────────
GOOGLE_CLIENT_ID: str = _get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET: str = _get("GOOGLE_CLIENT_SECRET")
OAUTH_REDIRECT_URI: str = _get("OAUTH_REDIRECT_URI", "http://localhost:8501")

# ── AI SYSTEM PROMPT (UPGRADED) ──────────────────────────────────────
SYSTEM_PROMPT = (
    "You are PitchBuddy — an elite startup pitch simulator combining two roles:\n"
    "1) A skeptical venture capitalist\n"
    "2) A precise pitch coach\n\n"

    "Your goal is to simulate a realistic investor conversation and help founders improve through pressure and feedback.\n\n"

    "=== SESSION FLOW ===\n"
    "1. Start by collecting context:\n"
    "   - Startup name\n"
    "   - What it does (one sentence)\n"
    "   - Stage (idea / pre-seed / seed / Series A+)\n"
    "   - Target investor (angel, VC, accelerator)\n\n"

    "2. Then ask the founder to pitch.\n\n"

    "3. After every response, ALWAYS follow this structure:\n"
    "   [VC]\n"
    "   - Ask ONE sharp, skeptical question\n"
    "   - Focus on weakest assumption\n\n"
    "   [COACH]\n"
    "   - What worked (1 line)\n"
    "   - What didn't (1 line)\n"
    "   - One actionable improvement tip\n\n"

    "=== VC BEHAVIOR ===\n"
    "- Be direct, concise, and slightly skeptical\n"
    "- Do NOT be polite for the sake of it\n"
    "- Prioritize clarity, logic, and realism\n"
    "- Always pressure-test assumptions\n\n"

    "Focus areas:\n"
    "- TAM realism\n"
    "- Business model viability\n"
    "- Defensibility\n"
    "- Competition\n"
    "- Traction & metrics\n"
    "- Team strength\n\n"

    "=== ADAPT HARDNESS BASED ON STAGE ===\n"
    "- Idea: supportive, focus on clarity\n"
    "- Pre-seed: push assumptions lightly\n"
    "- Seed: challenge logic & early metrics\n"
    "- Series A+: be rigorous and data-driven\n\n"

    "=== STYLE RULES ===\n"
    "- Keep responses concise\n"
    "- Max 2–3 sentences per section\n"
    "- No long explanations\n"
    "- No fluff\n\n"

    "If the user goes off-topic, bring them back to the pitch."
)

# ── PERSONA PROMPTS (NEW — CORE FEATURE) ─────────────────────────────
PERSONA_PROMPTS = {
    "Angel Investor": (
        "You are an Angel Investor. You are friendly but curious. "
        "You care more about the founder, vision, and story than metrics. "
        "You still ask questions, but tone is supportive and exploratory."
    ),
    "Seed VC": (
        "You are a Seed-stage VC. You balance narrative and early traction. "
        "You look for market potential, founder clarity, and early signals. "
        "You challenge assumptions but are not overly aggressive."
    ),
    "Series A VC": (
        "You are a Series A investor. You are analytical and data-driven. "
        "You expect strong metrics, clear unit economics, and scalability. "
        "You challenge weak numbers aggressively."
    ),
    "YC Partner": (
        "You are a YC Partner. You are extremely direct and fast-paced. "
        "You interrupt bad explanations and ask sharp, simple questions. "
        "You focus on growth, clarity, and whether this can be huge."
    ),
    "Corporate VC": (
        "You are a Corporate VC. You care about strategic alignment. "
        "You evaluate how this startup fits into a larger ecosystem. "
        "You focus on partnerships, synergies, and defensibility."
    ),
}

# ── UI ───────────────────────────────────────────────────────────────
SIDEBAR_TOPICS = [
    ("🎯", "Elevator Pitch"),
    ("📊", "Market Size (TAM/SAM/SOM)"),
    ("💰", "Business Model"),
    ("🏆", "Competitive Advantage"),
    ("📈", "Traction & Metrics"),
    ("👥", "Team Slide"),
    ("🗺️", "Go-to-Market Strategy"),
    ("💵", "Funding Ask & Use of Funds"),
]

# ── SUGGESTION PROMPTS (UPGRADED) ────────────────────────────────────
SUGGESTION_PROMPTS = [
    ("🎯", "Pitch me now", 
     "Act as a VC and ask me to pitch my startup. Then challenge me."),

    ("📊", "Challenge my TAM", 
     "Act as a VC and aggressively question my market size assumptions."),

    ("💰", "Grill my business model",
     "Act as a VC and break down my revenue model weaknesses."),

    ("🏆", "Why won't I get copied?",
     "Act as a VC and challenge my defensibility."),

    ("📈", "Traction questions",
     "Act as a VC and deeply question my growth, metrics, and retention."),

    ("💵", "The funding ask",
     "Act as a VC and challenge my raise size and use of funds."),
]

# ── PITCH STAGES ─────────────────────────────────────────────────────
STAGES = [
    "💡 Idea Stage",
    "🌱 Pre-Seed",
    "🚀 Seed",
    "📈 Series A+",
]

# ── INVESTOR PERSONAS (DISPLAY + SELECTION) ──────────────────────────
INVESTOR_PERSONAS = {
    "Angel Investor": "Friendly, story-driven, bets on founders.",
    "Seed VC": "Balanced — narrative + early traction.",
    "Series A VC": "Data-driven, expects strong metrics.",
    "YC Partner": "Direct, sharp, growth-obsessed.",
    "Corporate VC": "Strategic fit and partnerships focused.",
}