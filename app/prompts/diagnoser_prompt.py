from __future__ import annotations

DIAGNOSER_PROMPT = """다음 질문을 4가지 기준으로 평가하라.

질문: {question}
{context_section}
{previous_section}

평가 기준:
1. 구체성 (1~10): 질문 대상이 명확한가?
2. 맥락 포함 (1~10): 필요한 배경 정보가 있는가?
3. 답변 가능성 (1~10): 상대방이 답변할 수 있는가?
4. 범위 적절성 (1~10): 너무 넓거나 좁지 않은가?

반드시 아래 JSON 형식으로만 응답하라:
{{
    "diagnosis": "진단 결과를 2~3문장으로 설명",
    "problem_type": "specificity 또는 structure 또는 both 또는 good",
    "score": 종합점수(1~10 정수),
    "criteria_scores": {{
        "specificity": 점수,
        "context": 점수,
        "answerability": 점수,
        "scope": 점수
    }}
}}

problem_type 분류 기준:
- "specificity": 구체성 점수가 5 미만
- "structure": 맥락/답변가능성/범위 중 하나라도 5 미만 (구체성은 5 이상)
- "both": 구체성 5 미만 + 다른 기준도 5 미만
- "good": 모든 기준이 5 이상"""


def format_diagnoser_prompt(
    question: str,
    context: str | None = None,
    previous_scores: list[int] | None = None,
) -> str:
    context_section = f"사용 맥락: {context}" if context else "사용 맥락: 없음"
    if previous_scores:
        score_str = " → ".join(str(s) for s in previous_scores)
        previous_section = f"이전 시도 점수: {score_str}\n이전 점수와 비교하여 변화를 언급하라."
    else:
        previous_section = ""
    return DIAGNOSER_PROMPT.format(
        question=question,
        context_section=context_section,
        previous_section=previous_section,
    )
