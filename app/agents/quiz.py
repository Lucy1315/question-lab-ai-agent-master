from __future__ import annotations

import json

from langchain_core.messages import HumanMessage, SystemMessage

from app.llm import LLMError, invoke_llm, strip_code_fence
from app.prompts.quiz_prompt import format_quiz_evaluate_prompt, format_quiz_generate_prompt
from app.prompts.system_prompt import SYSTEM_PROMPT

_FALLBACK_QUIZ = {
    "bad_question": "이거 어떻게 해?",
    "problem_type": "specificity",
    "hint": "무엇을 어떻게 하고 싶은지 생각해보세요",
    "answer": "대상과 방법이 불명확합니다",
    "good_version": "Python에서 리스트를 정렬하는 방법을 시간복잡도와 함께 설명해줘",
}


def generate_quiz(state: dict) -> dict:
    prompt = format_quiz_generate_prompt(context=state.get("context"))
    try:
        content = invoke_llm([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ])
    except LLMError:
        return {"quiz_data": _FALLBACK_QUIZ}
    try:
        content = strip_code_fence(content)
        data = json.loads(content)
        return {"quiz_data": data}
    except (json.JSONDecodeError, KeyError):
        return {"quiz_data": _FALLBACK_QUIZ}


def evaluate_quiz(state: dict) -> dict:
    quiz_data = state["quiz_data"]
    prompt = format_quiz_evaluate_prompt(
        bad_question=quiz_data["bad_question"],
        answer=quiz_data["answer"],
        user_answer=state["user_answer"],
    )
    try:
        content = invoke_llm([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ])
    except LLMError as e:
        content = f"평가 중 오류가 발생했습니다: {e}"
    quiz_entry = {
        "bad_question": quiz_data["bad_question"],
        "user_answer": state["user_answer"],
        "evaluation": content,
        "correct_answer": quiz_data["answer"],
        "good_version": quiz_data["good_version"],
    }
    existing = list(state.get("quiz_history") or [])
    existing.append(quiz_entry)
    return {"quiz_evaluation": content, "quiz_history": existing}
