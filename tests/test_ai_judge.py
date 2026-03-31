from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest


def ai_judge(original: str, rewritten: str, diagnosis: str, llm) -> dict:
    """Use a separate LLM call to evaluate coaching quality."""
    prompt = f"""다음 질문 코칭 결과를 평가하라.

원본 질문: {original}
진단 결과: {diagnosis}
리라이팅: {rewritten}

평가 기준 (각 1~5점):
1. 진단 정확성 — 진단이 실제 문제를 짚었는가?
2. 리라이팅 개선도 — 원본 대비 실질적으로 나아졌는가?
3. 의도 보존 — 원본의 의도가 유지되었는가?
4. 실행 가능성 — 전략/피드백이 실행 가능한가?

반드시 아래 JSON 형식으로만 응답하라:
{{
    "diagnosis_accuracy": 점수,
    "improvement": 점수,
    "intent_preservation": 점수,
    "actionability": 점수,
    "overall": 평균점수,
    "reasoning": "평가 이유"
}}"""
    from langchain_core.messages import HumanMessage
    response = llm.invoke([HumanMessage(content=prompt)])
    try:
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        return json.loads(content)
    except (json.JSONDecodeError, KeyError):
        return {"overall": 0, "reasoning": "Failed to parse judge response"}


@pytest.fixture
def judge_llm():
    llm = MagicMock()
    llm.invoke.return_value = MagicMock(
        content=json.dumps({
            "diagnosis_accuracy": 4,
            "improvement": 4,
            "intent_preservation": 5,
            "actionability": 4,
            "overall": 4.25,
            "reasoning": "진단이 정확하고 리라이팅이 구체적으로 개선되었음",
        })
    )
    return llm


def test_judge_vague_question(judge_llm):
    result = ai_judge(
        original="알려줘",
        rewritten="Python에서 리스트 컴프리헨션의 기본 문법과 사용 예시를 설명해줘",
        diagnosis="구체성 부족 — 대상과 범위가 전혀 없음",
        llm=judge_llm,
    )
    assert result["overall"] >= 3
    assert result["improvement"] >= 3


def test_judge_good_question(judge_llm):
    judge_llm.invoke.return_value = MagicMock(
        content=json.dumps({
            "diagnosis_accuracy": 5,
            "improvement": 3,
            "intent_preservation": 5,
            "actionability": 4,
            "overall": 4.25,
            "reasoning": "이미 좋은 질문이라 개선 여지가 적음",
        })
    )
    result = ai_judge(
        original="Python에서 리스트와 튜플의 성능 차이를 메모리 할당 관점에서 설명해줘",
        rewritten="Python에서 리스트와 튜플의 성능 차이를 메모리 할당과 접근 속도 관점에서 비교 설명해줘",
        diagnosis="좋은 질문 — 구체적이고 범위가 적절함",
        llm=judge_llm,
    )
    assert result["diagnosis_accuracy"] >= 4
    assert result["intent_preservation"] >= 4


def test_judge_code_review_question(judge_llm):
    result = ai_judge(
        original="코드 리뷰해줘",
        rewritten="auth_handler.py의 로그인 함수를 보안 관점에서 리뷰해줘. SQL injection과 세션 관리를 중점적으로.",
        diagnosis="구체성 부족 — 대상 파일과 리뷰 관점이 없음",
        llm=judge_llm,
    )
    assert result["actionability"] >= 3
    assert result["overall"] >= 3


@pytest.mark.skipif(
    not __import__("os").getenv("ANTHROPIC_API_KEY")
    or __import__("os").getenv("ANTHROPIC_API_KEY") == "sk-ant-your-key-here",
    reason="ANTHROPIC_API_KEY not set — skip live AI judge test",
)
def test_judge_live_integration():
    """Live test with real LLM — only runs when API key is available."""
    from app.llm import get_llm

    llm = get_llm()
    result = ai_judge(
        original="알려줘",
        rewritten="Python에서 리스트 컴프리헨션의 기본 문법과 for 루프와의 성능 차이를 설명해줘",
        diagnosis="구체성 부족 — 무엇을 알려달라는 건지 대상이 없음",
        llm=llm,
    )
    assert "overall" in result
    assert isinstance(result["overall"], (int, float))
    assert 1 <= result["overall"] <= 5
