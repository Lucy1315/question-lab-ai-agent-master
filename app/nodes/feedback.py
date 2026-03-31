from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from app.llm import get_llm
from app.prompts.feedback_prompt import format_feedback_prompt
from app.prompts.system_prompt import SYSTEM_PROMPT
from app.state import Attempt


def give_feedback(state: dict) -> dict:
    llm = get_llm()
    prompt = format_feedback_prompt(
        question=state["current_input"],
        diagnosis=state["diagnosis"],
        score=state["score"],
        rewritten=state.get("rewritten"),
        previous_attempts=state.get("attempts"),
    )
    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=prompt),
    ])
    attempt: Attempt = {
        "question": state["current_input"],
        "diagnosis": state["diagnosis"],
        "problem_type": state["problem_type"],
        "strategy": state.get("strategy"),
        "rewritten": state.get("rewritten"),
        "score": state["score"],
        "feedback": response.content.strip(),
    }
    existing_attempts = list(state.get("attempts", []))
    existing_attempts.append(attempt)
    return {"feedback": response.content.strip(), "attempts": existing_attempts}
