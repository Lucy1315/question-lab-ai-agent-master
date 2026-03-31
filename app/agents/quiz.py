from __future__ import annotations

import json

from langchain_core.messages import HumanMessage, SystemMessage

from app.llm import get_llm
from app.prompts.quiz_prompt import format_quiz_evaluate_prompt, format_quiz_generate_prompt
from app.prompts.system_prompt import SYSTEM_PROMPT


def generate_quiz(state: dict) -> dict:
    llm = get_llm()
    prompt = format_quiz_generate_prompt(context=state.get("context"))
    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=prompt),
    ])
    try:
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        data = json.loads(content)
        return {"quiz_data": data}
    except (json.JSONDecodeError, KeyError):
        return {
            "quiz_data": {
                "bad_question": "이거 어떻게 해?",
                "problem_type": "specificity",
                "hint": "무엇을 어떻게 하고 싶은지 생각해보세요",
                "answer": "대상과 방법이 불명확합니다",
                "good_version": "Python에서 리스트를 정렬하는 방법을 시간복잡도와 함께 설명해줘",
            }
        }


def evaluate_quiz(state: dict) -> dict:
    llm = get_llm()
    quiz_data = state["quiz_data"]
    prompt = format_quiz_evaluate_prompt(
        bad_question=quiz_data["bad_question"],
        answer=quiz_data["answer"],
        user_answer=state["user_answer"],
    )
    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=prompt),
    ])
    quiz_entry = {
        "bad_question": quiz_data["bad_question"],
        "user_answer": state["user_answer"],
        "evaluation": response.content.strip(),
        "correct_answer": quiz_data["answer"],
        "good_version": quiz_data["good_version"],
    }
    existing = list(state.get("quiz_history") or [])
    existing.append(quiz_entry)
    return {"quiz_evaluation": response.content.strip(), "quiz_history": existing}
