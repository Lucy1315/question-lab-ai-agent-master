import logging

logger = logging.getLogger(__name__)

ROUTE_MAP = {
    "specificity": "strategy",
    "structure": "rewriter",
    "both": "strategy",
    "good": "feedback",
}


def route_by_problem_type(state: dict) -> str:
    problem_type = state.get("problem_type", "good")
    if problem_type not in ROUTE_MAP:
        logger.warning("Unexpected problem_type '%s', falling back to 'feedback'", problem_type)
    return ROUTE_MAP.get(problem_type, "feedback")
