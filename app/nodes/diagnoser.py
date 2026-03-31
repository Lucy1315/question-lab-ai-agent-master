from __future__ import annotations

import json

from langchain_core.messages import HumanMessage, SystemMessage

from app.llm import LLMError, invoke_llm, strip_code_fence
from app.prompts.diagnoser_prompt import format_diagnoser_prompt
from app.prompts.system_prompt import SYSTEM_PROMPT
from app.state import SessionState


def diagnose(state: SessionState) -> dict:
    previous_scores = [a["score"] for a in state.get("attempts", [])]
    prompt = format_diagnoser_prompt(
        question=state["current_input"],
        context=state.get("context"),
        previous_scores=previous_scores if previous_scores else None,
    )
    try:
        content = invoke_llm([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ])
    except LLMError as e:
        return {
            "diagnosis": f"진단 중 오류가 발생했습니다: {e}",
            "problem_type": "both",
            "score": 5,
            "error": str(e),
        }
    try:
        content = strip_code_fence(content)
        data = json.loads(content)
        return {
            "diagnosis": data["diagnosis"],
            "problem_type": data["problem_type"],
            "score": max(1, min(10, int(data["score"]))),
        }
    except (json.JSONDecodeError, KeyError):
        return {
            "diagnosis": content,
            "problem_type": "both",
            "score": 5,
        }
