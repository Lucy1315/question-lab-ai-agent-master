from __future__ import annotations

import json

from langchain_core.messages import HumanMessage, SystemMessage

from app.llm import get_llm
from app.prompts.diagnoser_prompt import format_diagnoser_prompt
from app.prompts.system_prompt import SYSTEM_PROMPT
from app.state import SessionState


def diagnose(state: SessionState) -> dict:
    llm = get_llm()
    previous_scores = [a["score"] for a in state.get("attempts", [])]
    prompt = format_diagnoser_prompt(
        question=state["current_input"],
        context=state.get("context"),
        previous_scores=previous_scores if previous_scores else None,
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
            "diagnosis": data["diagnosis"],
            "problem_type": data["problem_type"],
            "score": max(1, min(10, int(data["score"]))),
        }
    except (json.JSONDecodeError, KeyError):
        return {
            "diagnosis": response.content,
            "problem_type": "both",
            "score": 5,
        }
