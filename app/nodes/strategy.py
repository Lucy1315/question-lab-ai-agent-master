from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from app.llm import LLMError, invoke_llm
from app.prompts.strategy_prompt import format_strategy_prompt
from app.prompts.system_prompt import SYSTEM_PROMPT


def suggest_strategy(state: dict) -> dict:
    research = state.get("research")
    prompt = format_strategy_prompt(
        question=state["current_input"],
        diagnosis=state["diagnosis"],
        problem_type=state["problem_type"],
        context=state.get("context"),
        research_examples=research["examples"] if research else None,
        research_framework=research["framework"] if research else None,
    )
    try:
        content = invoke_llm([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ])
    except LLMError as e:
        content = f"전략 생성 중 오류가 발생했습니다: {e}"
    return {"strategy": content}
