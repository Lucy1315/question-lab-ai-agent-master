from app.nodes.feedback import parse_feedback_response


def test_parse_feedback_with_example_answers():
    response = (
        "강점: 질문의 의도가 명확합니다.\n"
        "개선점: 범위를 좁혀야 합니다.\n"
        "팁: 구체적인 기술 스택을 명시하세요.\n"
        "예시답변_현재: 어떤 프로젝트인지 좀 더 알려주시겠어요?\n"
        "예시답변_개선: React에서 캐싱 전략은 크게 3가지입니다."
    )
    result = parse_feedback_response(response)
    assert result["feedback"] == (
        "강점: 질문의 의도가 명확합니다.\n"
        "개선점: 범위를 좁혀야 합니다.\n"
        "팁: 구체적인 기술 스택을 명시하세요."
    )
    assert result["example_current"] == "어떤 프로젝트인지 좀 더 알려주시겠어요?"
    assert result["example_improved"] == "React에서 캐싱 전략은 크게 3가지입니다."


def test_parse_feedback_without_example_answers():
    response = (
        "강점: 좋은 질문입니다.\n"
        "개선점: 없습니다.\n"
        "팁: 계속 이렇게 질문하세요."
    )
    result = parse_feedback_response(response)
    assert result["feedback"] == response
    assert result["example_current"] is None
    assert result["example_improved"] is None


def test_parse_feedback_with_only_current_example():
    response = (
        "강점: 좋습니다.\n"
        "개선점: 범위를 좁히세요.\n"
        "팁: 맥락을 추가하세요.\n"
        "예시답변_현재: 좀 더 구체적으로 알려주세요."
    )
    result = parse_feedback_response(response)
    assert result["example_current"] == "좀 더 구체적으로 알려주세요."
    assert result["example_improved"] is None
