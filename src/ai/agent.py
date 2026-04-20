"""Core AI response logic — no Streamlit dependency."""
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from src.ai.clients import get_llm
from src.config import SYSTEM_PROMPT, PERSONA_PROMPTS
from src.utils.retry import api_retry


def _build_system_prompt(persona: str, stage: str) -> str:
    persona_instructions = PERSONA_PROMPTS.get(persona, "")
    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"=== ACTIVE SESSION CONFIG ===\n"
        f"Investor Persona: {persona}\n{persona_instructions}\n\n"
        f"Founder Stage: {stage}\n"
        f"Adjust scrutiny accordingly."
    )


@api_retry
def get_ai_response(
    user_input: str,
    history: list[dict],
    persona: str = "Seed VC",
    stage: str = "🌱 Pre-Seed",
) -> str:
    llm = get_llm()
    system_prompt = _build_system_prompt(persona, stage)
    msgs = [SystemMessage(content=system_prompt)]
    for msg in history:
        if msg["role"] == "user":
            msgs.append(HumanMessage(content=msg["content"]))
        else:
            msgs.append(AIMessage(content=msg["content"]))
    msgs.append(HumanMessage(content=user_input))
    return llm.invoke(msgs).content
