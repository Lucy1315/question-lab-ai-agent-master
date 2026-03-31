from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_all_llms():
    """Mock all invoke_llm calls across the entire graph."""
    patches = [
        patch("app.nodes.diagnoser.invoke_llm"),
        patch("app.nodes.strategy.invoke_llm"),
        patch("app.nodes.rewriter.invoke_llm"),
        patch("app.nodes.feedback.invoke_llm"),
        patch("app.agents.researcher.invoke_llm"),
        patch("app.agents.quiz.invoke_llm"),
    ]
    mocks = [p.start() for p in patches]

    def diagnoser_side_effect(messages):
        return json.dumps({
            "diagnosis": "구체성이 부족합니다",
            "problem_type": "specificity",
            "score": 3,
            "criteria_scores": {"specificity": 2, "context": 4, "answerability": 3, "scope": 5},
        })

    def researcher_side_effect(messages):
        return json.dumps({
            "examples": ["예시1", "예시2", "예시3"],
            "framework": "5W1H",
        })

    def quiz_side_effect(messages):
        return json.dumps({
            "bad_question": "알려줘",
            "problem_type": "specificity",
            "hint": "대상을 생각해보세요",
            "answer": "대상 없음",
            "good_version": "Python 리스트 정렬 방법 알려줘",
        })

    # diagnoser, strategy, rewriter, feedback, researcher, quiz
    mocks[0].side_effect = diagnoser_side_effect
    mocks[1].return_value = "전략 1: 대상 특정\n예시: auth.py"
    mocks[2].return_value = "리라이팅: auth.py 로그인 함수 보안 리뷰해줘\n변경 이유: 대상 구체화"
    mocks[3].return_value = "강점: 의도 명확\n개선점: 대상 특정\n팁: 파일명 포함"
    mocks[4].side_effect = researcher_side_effect
    mocks[5].side_effect = quiz_side_effect

    yield mocks
    for p in patches:
        p.stop()


def _get_initial_state(mode="coach"):
    return {
        "context": "AI 챗봇에게 질문할 때",
        "mode": mode,
        "attempts": [],
        "current_input": "코드 리뷰해줘",
        "user_decision": "",
        "research": None,
        "quiz_history": None,
        "diagnosis": None,
        "problem_type": None,
        "score": None,
        "strategy": None,
        "rewritten": None,
        "feedback": None,
        "error": None,
        "quiz_data": None,
        "quiz_evaluation": None,
        "user_answer": None,
        "export_path": None,
    }


def test_coach_mode_end_to_end(mock_all_llms):
    from app.graph import create_main_graph

    graph = create_main_graph()
    result = graph.invoke(_get_initial_state("coach"))
    assert len(result["attempts"]) == 1
    assert result["attempts"][0]["score"] == 3
    assert result["attempts"][0]["diagnosis"]
    assert result["attempts"][0]["feedback"]


def test_quiz_mode_end_to_end(mock_all_llms):
    from app.graph import create_main_graph

    graph = create_main_graph()
    result = graph.invoke(_get_initial_state("quiz"))
    assert result.get("quiz_data") is not None
    assert result["quiz_data"]["bad_question"]


def test_research_mode_end_to_end(mock_all_llms):
    from app.graph import create_main_graph

    graph = create_main_graph()
    result = graph.invoke(_get_initial_state("research"))
    assert result.get("research") is not None
    assert len(result["research"]["examples"]) == 3


def test_parallel_coach_end_to_end(mock_all_llms):
    from app.graph import create_parallel_coach_graph

    graph = create_parallel_coach_graph()
    state = _get_initial_state("coach")
    result = graph.invoke(state)
    assert len(result["attempts"]) == 1
    assert result.get("research") is not None
