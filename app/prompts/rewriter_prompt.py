from __future__ import annotations

REWRITER_PROMPT = """다음 질문을 개선 전략을 반영해 리라이팅하라.

원본 질문: {question}
{context_section}
진단 결과: {diagnosis}
{strategy_section}

규칙:
- 원본의 의도를 유지하면서 개선하라.
- 리라이팅된 질문 1개만 제시하라.
- 원본과 달라진 부분을 1문장으로 설명하라.

아래 형식으로 응답하라:
리라이팅: [개선된 질문]
변경 이유: [1문장]"""


def format_rewriter_prompt(
    question: str,
    diagnosis: str,
    context: str | None = None,
    strategy: str | None = None,
) -> str:
    context_section = f"사용 맥락: {context}" if context else "사용 맥락: 없음"
    strategy_section = f"개선 전략:\n{strategy}" if strategy else "개선 전략: 없음"
    return REWRITER_PROMPT.format(
        question=question,
        context_section=context_section,
        diagnosis=diagnosis,
        strategy_section=strategy_section,
    )
