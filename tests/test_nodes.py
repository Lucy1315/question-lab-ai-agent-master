from app.state import Attempt, ResearchResult, SessionState


def test_attempt_creation():
    attempt: Attempt = {
        "question": "코드 리뷰해줘",
        "diagnosis": "구체성 부족",
        "problem_type": "specificity",
        "strategy": "대상 파일을 특정하세요",
        "rewritten": "auth_handler.py 로그인 함수를 보안 관점에서 리뷰해줘",
        "score": 3,
        "feedback": "대상과 관점을 추가하면 좋겠습니다",
    }
    assert attempt["question"] == "코드 리뷰해줘"
    assert attempt["score"] == 3
    assert attempt["problem_type"] in ("specificity", "structure", "both", "good")


def test_session_state_creation():
    state: SessionState = {
        "context": "AI 챗봇에게 질문할 때",
        "mode": "coach",
        "attempts": [],
        "current_input": "코드 리뷰해줘",
        "user_decision": "",
        "research": None,
        "quiz_history": None,
    }
    assert state["mode"] == "coach"
    assert state["attempts"] == []
    assert state["research"] is None


def test_research_result_creation():
    result: ResearchResult = {
        "examples": ["예시1", "예시2", "예시3"],
        "framework": "5W1H 프레임워크",
    }
    assert len(result["examples"]) == 3


from app.nodes.parser import parse_input
from app.nodes.router import route_by_problem_type


def test_parser_empty_input():
    state = {
        "current_input": "",
        "context": None,
        "mode": "coach",
        "attempts": [],
        "user_decision": "",
        "research": None,
        "quiz_history": None,
    }
    result = parse_input(state)
    assert result["current_input"] == ""
    assert result.get("error") == "empty_input"


def test_parser_normalizes():
    state = {
        "current_input": "  코드 리뷰해줘  \n ",
        "context": None,
        "mode": "coach",
        "attempts": [],
        "user_decision": "",
        "research": None,
        "quiz_history": None,
    }
    result = parse_input(state)
    assert result["current_input"] == "코드 리뷰해줘"


def test_router_specificity():
    result = route_by_problem_type({"problem_type": "specificity"})
    assert result == "strategy"


def test_router_structure():
    result = route_by_problem_type({"problem_type": "structure"})
    assert result == "rewriter"


def test_router_both():
    result = route_by_problem_type({"problem_type": "both"})
    assert result == "strategy"


def test_router_good():
    result = route_by_problem_type({"problem_type": "good"})
    assert result == "feedback"


import json
import pytest
from unittest.mock import MagicMock, patch

from app.nodes.diagnoser import diagnose
from app.nodes.strategy import suggest_strategy
from app.nodes.rewriter import rewrite_question
from app.nodes.feedback import give_feedback


@pytest.fixture
def mock_llm():
    with patch("app.nodes.diagnoser.get_llm") as d_mock, \
         patch("app.nodes.strategy.get_llm") as s_mock, \
         patch("app.nodes.rewriter.get_llm") as r_mock, \
         patch("app.nodes.feedback.get_llm") as f_mock:
        llm = MagicMock()
        d_mock.return_value = llm
        s_mock.return_value = llm
        r_mock.return_value = llm
        f_mock.return_value = llm
        yield llm


def test_diagnoser_returns_valid_json(mock_llm):
    mock_llm.invoke.return_value = MagicMock(
        content=json.dumps({
            "diagnosis": "구체성이 부족합니다",
            "problem_type": "specificity",
            "score": 3,
            "criteria_scores": {"specificity": 2, "context": 4, "answerability": 3, "scope": 5},
        })
    )
    state = {
        "current_input": "코드 리뷰해줘",
        "context": None,
        "attempts": [],
        "mode": "coach",
        "user_decision": "",
        "research": None,
        "quiz_history": None,
    }
    result = diagnose(state)
    assert result["problem_type"] in ("specificity", "structure", "both", "good")
    assert 1 <= result["score"] <= 10
    assert "diagnosis" in result


def test_diagnoser_score_range(mock_llm):
    mock_llm.invoke.return_value = MagicMock(
        content=json.dumps({
            "diagnosis": "좋은 질문입니다",
            "problem_type": "good",
            "score": 8,
            "criteria_scores": {"specificity": 8, "context": 7, "answerability": 9, "scope": 8},
        })
    )
    state = {
        "current_input": "Python 리스트 컴프리헨션의 메모리 사용량을 제너레이터와 비교 설명해줘",
        "context": "파이썬 학습 중",
        "attempts": [],
        "mode": "coach",
        "user_decision": "",
        "research": None,
        "quiz_history": None,
    }
    result = diagnose(state)
    assert 1 <= result["score"] <= 10


def test_strategy_actionable(mock_llm):
    mock_llm.invoke.return_value = MagicMock(
        content="전략 1: 리뷰 대상을 특정 파일로 좁히세요\n예시: auth.py의 login 함수"
    )
    state = {
        "current_input": "코드 리뷰해줘",
        "context": None,
        "diagnosis": "구체성 부족",
        "problem_type": "specificity",
        "research": None,
    }
    result = suggest_strategy(state)
    assert result["strategy"]
    assert len(result["strategy"]) > 0


def test_rewriter_preserves_intent(mock_llm):
    mock_llm.invoke.return_value = MagicMock(
        content="리라이팅: auth.py의 로그인 함수를 보안 관점에서 리뷰해줘\n변경 이유: 대상과 관점을 구체화"
    )
    state = {
        "current_input": "코드 리뷰해줘",
        "context": None,
        "diagnosis": "구체성 부족",
        "strategy": "대상을 특정하세요",
    }
    result = rewrite_question(state)
    assert result["rewritten"]
    assert len(result["rewritten"]) > 0


def test_feedback_has_score(mock_llm):
    mock_llm.invoke.return_value = MagicMock(
        content="강점: 의도가 명확합니다\n개선점: 대상 특정 필요\n팁: 파일명을 포함해보세요"
    )
    state = {
        "current_input": "코드 리뷰해줘",
        "diagnosis": "구체성 부족",
        "problem_type": "specificity",
        "score": 3,
        "strategy": "대상 특정",
        "rewritten": "auth.py 리뷰해줘",
        "attempts": [],
        "context": None,
    }
    result = give_feedback(state)
    assert "feedback" in result
    assert "attempts" in result
    assert len(result["attempts"]) == 1
    assert result["attempts"][0]["score"] == 3
