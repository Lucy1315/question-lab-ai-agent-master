from __future__ import annotations

FEEDBACK_PROMPT = """다음 질문 코칭 결과를 바탕으로 피드백을 제공하라.

원본 질문: {question}
진단 결과: {diagnosis}
점수: {score}/10
{rewritten_section}
{previous_section}

규칙:
- 강점 1개를 먼저 언급하라. (1문장)
- 개선점 1개를 제시하라. (1문장)
- 다음에 시도할 팁 1개를 제안하라. (1문장)
- 이전 시도가 있으면 점수 변화를 한 문장으로 코멘트하라.
- 격려하는 톤을 유지하라.
- 현재 질문에 대한 예상 답변 핵심을 2문장 이내로 요약하라.
- 리라이팅 질문에 대한 예상 답변 핵심을 2문장 이내로 요약하라.
- 전체 응답을 가능한 짧게 작성하라.

아래 형식으로 응답하라:
강점: [1문장]
개선점: [1문장]
팁: [1문장]
예시답변_현재: [2문장 이내 요약]
예시답변_개선: [2문장 이내 요약]"""


def format_feedback_prompt(
    question: str,
    diagnosis: str,
    score: int,
    rewritten: str | None = None,
    previous_attempts: list[dict] | None = None,
) -> str:
    rewritten_section = f"리라이팅 제안: {rewritten}" if rewritten else ""
    if previous_attempts:
        prev_str = "\n".join(
            f"  시도 {i+1}: {a['question']} ({a['score']}점)"
            for i, a in enumerate(previous_attempts)
        )
        previous_section = f"이전 시도:\n{prev_str}"
    else:
        previous_section = ""
    return FEEDBACK_PROMPT.format(
        question=question,
        diagnosis=diagnosis,
        score=score,
        rewritten_section=rewritten_section,
        previous_section=previous_section,
    )
