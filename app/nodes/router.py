ROUTE_MAP = {
    "specificity": "strategy",
    "structure": "rewriter",
    "both": "strategy",
    "good": "feedback",
}


def route_by_problem_type(state: dict) -> str:
    problem_type = state.get("problem_type", "good")
    return ROUTE_MAP.get(problem_type, "feedback")
