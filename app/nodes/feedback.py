from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from app.llm import LLMError, invoke_llm
from app.prompts.feedback_prompt import format_feedback_prompt
from app.prompts.system_prompt import SYSTEM_PROMPT
from app.state import Attempt


def give_feedback(state: dict) -> dict:
    prompt = format_feedback_prompt(
        question=state["current_input"],
        diagnosis=state["diagnosis"],
        score=state["score"],
        rewritten=state.get("rewritten"),
        previous_attempts=state.get("attempts"),
    )
    try:
        content = invoke_llm([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ])
    except LLMError as e:
        content = f"피드백 생성 중 오류가 발생했습니다: {e}"
    attempt: Attempt = {
        "question": state["current_input"],
        "diagnosis": state["diagnosis"],
        "problem_type": state["problem_type"],
        "strategy": state.get("strategy"),
        "rewritten": state.get("rewritten"),
        "score": state["score"],
        "feedback": content,
    }
    existing_attempts = list(state.get("attempts", []))
    existing_attempts.append(attempt)
    return {"feedback": content, "attempts": existing_attempts}
