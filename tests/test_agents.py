from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_llm_for_agents():
    """Mock invoke_llm that returns different responses based on call order."""
    with patch("app.nodes.diagnoser.invoke_llm") as d_mock, \
         patch("app.nodes.strategy.invoke_llm") as s_mock, \
         patch("app.nodes.rewriter.invoke_llm") as r_mock, \
         patch("app.nodes.feedback.invoke_llm") as f_mock:

        d_mock.return_value = json.dumps({
            "diagnosis": "구체성이 부족합니다",
            "problem_type": "specificity",
            "score": 3,
            "criteria_scores": {"specificity": 2, "context": 4, "answerability": 3, "scope": 5},
        })
        s_mock.return_value = "전략 1: 리뷰 대상을 특정하세요\n예시: auth.py"
        r_mock.return_value = "리라이팅: auth.py의 로그인 함수를 보안 관점에서 리뷰해줘\n변경 이유: 대상 구체화"
        f_mock.return_value = "강점: 의도 명확\n개선점: 대상 특정\n팁: 파일명 포함"
        yield {"diagnoser": d_mock, "strategy": s_mock, "rewriter": r_mock, "feedback": f_mock}


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


def test_researcher_returns_examples():
    mock_return = json.dumps({
        "examples": [
            "auth.py의 로그인 함수에서 SQL injection 취약점이 있는지 리뷰해줘",
            "session 만료 처리 로직이 OWASP 가이드라인에 맞는지 확인해줘",
            "비밀번호 해싱에 bcrypt 대신 sha256을 쓰고 있는데 보안상 문제가 있는지 알려줘",
        ],
        "framework": "OWASP 보안 코드 리뷰 체크리스트",
    })
    with patch("app.agents.researcher.invoke_llm", return_value=mock_return):
        from app.agents.researcher import research

        state = {
            "current_input": "코드 리뷰해줘",
            "context": "보안 코드 리뷰",
        }
        result = research(state)
        assert result["research"] is not None
        assert len(result["research"]["examples"]) == 3
        assert result["research"]["framework"]


def test_quiz_generates_question():
    mock_return = json.dumps({
        "bad_question": "알려줘",
        "problem_type": "specificity",
        "hint": "무엇을 알려달라는 건지 생각해보세요",
        "answer": "대상과 범위가 전혀 없는 질문입니다",
        "good_version": "Python의 리스트 컴프리헨션 문법을 예시와 함께 설명해줘",
    })
    with patch("app.agents.quiz.invoke_llm", return_value=mock_return):
        from app.agents.quiz import generate_quiz

        state = {"context": None}
        result = generate_quiz(state)
        assert result["quiz_data"]["bad_question"]
        assert result["quiz_data"]["problem_type"] in ("specificity", "structure", "both")
        assert result["quiz_data"]["answer"]
        assert result["quiz_data"]["good_version"]


def test_supervisor_routes_correctly():
    from app.agents.supervisor import route_to_agent

    assert route_to_agent({"mode": "coach"}) == "tutor"
    assert route_to_agent({"mode": "quiz"}) == "quiz"
    assert route_to_agent({"mode": "research"}) == "researcher"
    assert route_to_agent({"mode": "coach", "error": "empty_input"}) == "end"


def test_main_graph_compiles(mock_llm_for_agents):
    from app.graph import create_main_graph

    graph = create_main_graph()
    assert graph is not None


def test_parallel_graph_compiles(mock_llm_for_agents):
    from app.graph import create_parallel_coach_graph

    graph = create_parallel_coach_graph()
    assert graph is not None
