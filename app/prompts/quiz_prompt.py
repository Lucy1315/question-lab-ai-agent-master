from __future__ import annotations

QUIZ_GENERATE_PROMPT = """질문 개선 연습을 위한 퀴즈를 출제하라.

{context_section}

규칙:
- 의도적으로 문제가 있는 질문 1개를 만들어라.
- 문제 유형은 specificity, structure, both 중 하나를 포함해야 한다.
- 난이도는 중간 수준으로 — 명백히 나쁘지만 완전히 엉터리는 아닌 질문.

아래 JSON 형식으로 응답하라:
{{
    "bad_question": "문제가 있는 질문",
    "problem_type": "specificity 또는 structure 또는 both",
    "hint": "힌트 한 줄",
    "answer": "이 질문의 문제점 설명",
    "good_version": "개선된 버전"
}}"""

QUIZ_EVALUATE_PROMPT = """사용자의 답변을 평가하라.

퀴즈 질문: {bad_question}
실제 문제점: {answer}
사용자 답변: {user_answer}

규칙:
- 사용자가 문제점을 얼마나 정확히 짚었는지 평가하라.
- 맞은 부분을 인정하고, 놓친 부분을 보충하라.
- 격려하는 톤을 유지하라.

아래 형식으로 응답하라:
평가: [사용자 답변 평가]
정답 해설: [전체 문제점 설명]
개선 제안: [좋은 질문으로 바꾸는 방법]"""


def format_quiz_generate_prompt(context: str | None = None) -> str:
    context_section = f"질문 사용 맥락: {context}" if context else "질문 사용 맥락: 일반"
    return QUIZ_GENERATE_PROMPT.format(context_section=context_section)


def format_quiz_evaluate_prompt(
    bad_question: str, answer: str, user_answer: str
) -> str:
    return QUIZ_EVALUATE_PROMPT.format(
        bad_question=bad_question, answer=answer, user_answer=user_answer
    )
