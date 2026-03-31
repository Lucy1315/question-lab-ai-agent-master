from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_llm_for_agents():
    """Mock LLM that returns different responses based on call order."""
    with patch("app.nodes.diagnoser.get_llm") as d_mock, \
         patch("app.nodes.strategy.get_llm") as s_mock, \
         patch("app.nodes.rewriter.get_llm") as r_mock, \
         patch("app.nodes.feedback.get_llm") as f_mock:
        llm = MagicMock()
        call_count = {"n": 0}

        def side_effect(messages):
            call_count["n"] += 1
            n = call_count["n"]
            if n == 1:  # diagnoser
                return MagicMock(content=json.dumps({
                    "diagnosis": "구체성이 부족합니다",
                    "problem_type": "specificity",
                    "score": 3,
                    "criteria_scores": {"specificity": 2, "context": 4, "answerability": 3, "scope": 5},
                }))
            elif n == 2:  # strategy
                return MagicMock(content="전략 1: 리뷰 대상을 특정하세요\n예시: auth.py")
            elif n == 3:  # rewriter
                return MagicMock(content="리라이팅: auth.py의 로그인 함수를 보안 관점에서 리뷰해줘\n변경 이유: 대상 구체화")
            else:  # feedback
                return MagicMock(content="강점: 의도 명확\n개선점: 대상 특정\n팁: 파일명 포함")

        llm.invoke = MagicMock(side_effect=side_effect)
        d_mock.return_value = llm
        s_mock.return_value = llm
        r_mock.return_value = llm
        f_mock.return_value = llm
        yield llm


def test_tutor_full_loop(mock_llm_for_agents):
    from app.agents.tutor import create_tutor_graph

    graph = create_tutor_graph()
    initial_state = {
        "context": None,
        "mode": "coach",
        "attempts": [],
        "current_input": "코드 리뷰해줘",
        "user_decision": "",
        "research": None,
        "quiz_history": None,
    }
    result = graph.invoke(initial_state)
    assert len(result["attempts"]) == 1
    assert result["attempts"][0]["score"] == 3
    assert result["attempts"][0]["problem_type"] == "specificity"
    assert result["attempts"][0]["feedback"]
