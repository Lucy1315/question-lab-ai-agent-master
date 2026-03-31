from __future__ import annotations

RESEARCHER_PROMPT = """다음 질문의 도메인에 맞는 좋은 질문 사례와 프레임워크를 제공하라.

질문: {question}
{context_section}

규칙:
- 이 도메인에서 좋은 질문 예시 3개를 만들어라.
- 해당 도메인에서 자주 쓰이는 질문 프레임워크 1개를 추천하라.
- 예시는 구체적이고 답변 가능한 질문이어야 한다.

반드시 아래 JSON 형식으로만 응답하라:
{{
    "examples": [
        "좋은 질문 예시 1",
        "좋은 질문 예시 2",
        "좋은 질문 예시 3"
    ],
    "framework": "추천 프레임워크 이름과 간단한 설명"
}}"""


def format_researcher_prompt(
    question: str, context: str | None = None
) -> str:
    context_section = f"사용 맥락: {context}" if context else "사용 맥락: 일반"
    return RESEARCHER_PROMPT.format(
        question=question, context_section=context_section
    )
