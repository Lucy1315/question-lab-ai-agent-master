from langgraph.graph import END, StateGraph

from app.nodes.diagnoser import diagnose
from app.nodes.feedback import give_feedback
from app.nodes.parser import parse_input
from app.nodes.rewriter import rewrite_question
from app.nodes.router import route_by_problem_type
from app.nodes.strategy import suggest_strategy
from app.state import SessionState


def create_tutor_graph():
    graph = StateGraph(SessionState)

    graph.add_node("parser", parse_input)
    graph.add_node("diagnoser", diagnose)
    graph.add_node("strategy", suggest_strategy)
    graph.add_node("rewriter", rewrite_question)
    graph.add_node("feedback", give_feedback)

    graph.set_entry_point("parser")
    graph.add_edge("parser", "diagnoser")
    graph.add_conditional_edges(
        "diagnoser",
        route_by_problem_type,
        {
            "strategy": "strategy",
            "rewriter": "rewriter",
            "feedback": "feedback",
        },
    )
    graph.add_edge("strategy", "rewriter")
    graph.add_edge("rewriter", "feedback")
    graph.add_edge("feedback", END)

    return graph.compile()
