from __future__ import annotations

FEEDBACK_PROMPT = """다음 질문 코칭 결과를 바탕으로 피드백을 제공하라.

원본 질문: {question}
진단 결과: {diagnosis}
점수: {score}/10
{rewritten_section}
{previous_section}

규칙:
- 강점 1~2개를 먼저 언급하라.
- 개선점 1~2개를 제시하라.
- 다음에 시도할 팁 1개를 제안하라.
- 점수가 "good"이어도 미세 조정 포인트를 하나는 제시하라.
- 이전 시도가 있으면 점수 변화를 코멘트하라.
- 격려하는 톤을 유지하라.
- 현재 질문을 그대로 받았을 때, 답변자가 줄 수 있는 전형적인 답변 예시를 1개 작성하라. 질문의 한계로 인해 답변도 제한적일 수밖에 없음을 보여주는 답변이어야 한다.
- 리라이팅 제안이 있으면, 리라이팅된 질문에 대해 답변자가 줄 수 있는 고품질 답변 예시를 1개 작성하라. 구체적이고 실용적인 답변이어야 한다.

아래 형식으로 응답하라:
강점: [강점 설명]
개선점: [개선점 설명]
팁: [다음에 시도할 구체적 팁]
예시답변_현재: [현재 질문에 대해 답변자가 줄 수 있는 전형적 답변]
예시답변_개선: [리라이팅 질문에 대해 답변자가 줄 수 있는 고품질 답변]"""


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
