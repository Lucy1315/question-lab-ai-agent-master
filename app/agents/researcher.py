from __future__ import annotations

import json

from langchain_core.messages import HumanMessage, SystemMessage

from app.llm import LLMError, invoke_llm, strip_code_fence
from app.prompts.researcher_prompt import format_researcher_prompt
from app.prompts.system_prompt import SYSTEM_PROMPT


def research(state: dict) -> dict:
    prompt = format_researcher_prompt(
        question=state["current_input"],
        context=state.get("context"),
    )
    try:
        content = invoke_llm([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ])
    except LLMError:
        return {"research": {"examples": [], "framework": "조회 실패"}}
    try:
        content = strip_code_fence(content)
        data = json.loads(content)
        return {
            "research": {
                "examples": data["examples"][:3],
                "framework": data["framework"],
            }
        }
    except (json.JSONDecodeError, KeyError):
        return {
            "research": {
                "examples": [],
                "framework": content,
            }
        }
