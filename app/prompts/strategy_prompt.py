from __future__ import annotations

STRATEGY_PROMPT = """다음 질문의 진단 결과를 바탕으로 구체적인 개선 전략을 제안하라.

원본 질문: {question}
{context_section}
진단 결과: {diagnosis}
문제 유형: {problem_type}

규칙:
- 실행 가능한 전략 2~3개를 제안하라.
- 각 전략에 구체적인 예시를 포함하라.
- "더 구체적으로 하세요" 같은 추상적 조언은 금지.
- "X 대신 Y로 범위를 좁혀보세요" 같은 실행 가능한 형태로 제시하라.

{research_section}

아래 형식으로 응답하라:
전략 1: [전략 설명]
예시: [구체적 예시]

전략 2: [전략 설명]
예시: [구체적 예시]

전략 3: [전략 설명] (선택)
예시: [구체적 예시]"""


def format_strategy_prompt(
    question: str,
    diagnosis: str,
    problem_type: str,
    context: str | None = None,
    research_examples: list[str] | None = None,
    research_framework: str | None = None,
) -> str:
    context_section = f"사용 맥락: {context}" if context else "사용 맥락: 없음"
    if research_examples and research_framework:
        examples_str = "\n".join(f"  - {e}" for e in research_examples)
        research_section = (
            f"참고 사례:\n{examples_str}\n참고 프레임워크: {research_framework}"
        )
    else:
        research_section = ""
    return STRATEGY_PROMPT.format(
        question=question,
        context_section=context_section,
        diagnosis=diagnosis,
        problem_type=problem_type,
        research_section=research_section,
    )
