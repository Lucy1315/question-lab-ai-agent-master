from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from app.llm import get_llm
from app.prompts.strategy_prompt import format_strategy_prompt
from app.prompts.system_prompt import SYSTEM_PROMPT


def suggest_strategy(state: dict) -> dict:
    llm = get_llm()
    research = state.get("research")
    prompt = format_strategy_prompt(
        question=state["current_input"],
        diagnosis=state["diagnosis"],
        problem_type=state["problem_type"],
        context=state.get("context"),
        research_examples=research["examples"] if research else None,
        research_framework=research["framework"] if research else None,
    )
    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=prompt),
    ])
    return {"strategy": response.content.strip()}
