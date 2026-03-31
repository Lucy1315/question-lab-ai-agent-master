from __future__ import annotations

import json

from langchain_core.messages import HumanMessage, SystemMessage

from app.llm import get_llm
from app.prompts.researcher_prompt import format_researcher_prompt
from app.prompts.system_prompt import SYSTEM_PROMPT


def research(state: dict) -> dict:
    llm = get_llm()
    prompt = format_researcher_prompt(
        question=state["current_input"],
        context=state.get("context"),
    )
    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=prompt),
    ])
    try:
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()
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
                "framework": response.content.strip(),
            }
        }
