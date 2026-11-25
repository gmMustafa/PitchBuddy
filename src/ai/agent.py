"""Core AI response logic — no Streamlit dependency."""
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from src.ai.clients import get_llm, get_fallback_llm
from src.config import SYSTEM_PROMPT, PERSONA_PROMPTS, MAX_HISTORY_MESSAGES
from src.utils.retry import api_retry, is_rate_limit


def _build_system_prompt(persona: str, stage: str) -> str:
    persona_instructions = PERSONA_PROMPTS.get(persona, "")
    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"=== ACTIVE SESSION CONFIG ===\n"
        f"Investor Persona: {persona}\n{persona_instructions}\n\n"
        f"Founder Stage: {stage}\n"
        f"Adjust scrutiny accordingly."
    )


def _build_messages(user_input: str, history: list[dict], persona: str, stage: str) -> list:
    msgs = [SystemMessage(content=_build_system_prompt(persona, stage))]
    # Only send the most recent turns — keeps tokens/request low on the free tier.
    for msg in history[-MAX_HISTORY_MESSAGES:]:
        cls = HumanMessage if msg["role"] == "user" else AIMessage
        msgs.append(cls(content=msg["content"]))
    msgs.append(HumanMessage(content=user_input))
    return msgs


@api_retry
def _invoke(llm, msgs) -> str:
    return llm.invoke(msgs).content


def get_ai_response(
    user_input: str,
    history: list[dict],
    persona: str = "Seed VC",
    stage: str = "🌱 Pre-Seed",
) -> str:
    msgs = _build_messages(user_input, history, persona, stage)
    try:
        return _invoke(get_llm(), msgs)
    except Exception as exc:
        if not is_rate_limit(exc):
            raise
        # Primary model's free quota exhausted → smaller model with a much larger quota.
        return _invoke(get_fallback_llm(), msgs)
