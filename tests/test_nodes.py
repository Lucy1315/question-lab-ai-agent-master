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
