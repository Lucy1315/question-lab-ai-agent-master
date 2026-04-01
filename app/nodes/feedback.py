from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from app.llm import LLMError, invoke_llm
from app.prompts.feedback_prompt import format_feedback_prompt
from app.prompts.system_prompt import SYSTEM_PROMPT
from app.state import Attempt


def parse_feedback_response(content: str) -> dict:
    """Parse LLM feedback response, extracting example answers if present."""
    example_current = None
    example_improved = None
    feedback_lines = []

    for line in content.split("\n"):
        if line.startswith("예시답변_현재:"):
            example_current = line[len("예시답변_현재:"):].strip()
        elif line.startswith("예시답변_개선:"):
            example_improved = line[len("예시답변_개선:"):].strip()
        else:
            feedback_lines.append(line)

    feedback = "\n".join(feedback_lines).strip()
    return {
        "feedback": feedback,
        "example_current": example_current or None,
        "example_improved": example_improved or None,
    }


def give_feedback(state: dict) -> dict:
    prompt = format_feedback_prompt(
        question=state["current_input"],
        diagnosis=state["diagnosis"],
        score=state["score"],
        rewritten=state.get("rewritten"),
        previous_attempts=state.get("attempts"),
    )
    try:
        raw_content = invoke_llm([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ])
    except LLMError as e:
        raw_content = f"피드백 생성 중 오류가 발생했습니다: {e}"

    parsed = parse_feedback_response(raw_content)
    attempt: Attempt = {
        "question": state["current_input"],
        "diagnosis": state["diagnosis"],
        "problem_type": state["problem_type"],
        "strategy": state.get("strategy"),
        "rewritten": state.get("rewritten"),
        "score": state["score"],
        "feedback": parsed["feedback"],
        "example_current": parsed["example_current"],
        "example_improved": parsed["example_improved"],
    }
    existing_attempts = list(state.get("attempts", []))
    existing_attempts.append(attempt)
    return {"feedback": parsed["feedback"], "attempts": existing_attempts}
