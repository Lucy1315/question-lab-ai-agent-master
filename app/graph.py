from __future__ import annotations

from langgraph.graph import END, StateGraph

from app.agents.quiz import evaluate_quiz, generate_quiz
from app.agents.researcher import research
from app.agents.supervisor import route_to_agent
from app.nodes.diagnoser import diagnose
from app.nodes.export import export_session
from app.nodes.feedback import give_feedback
from app.nodes.parser import parse_input
from app.nodes.rewriter import rewrite_question
from app.nodes.router import route_by_problem_type
from app.nodes.strategy import suggest_strategy
from app.state import SessionState


def create_main_graph():
    graph = StateGraph(SessionState)

    graph.add_node("parser", parse_input)
    graph.add_node("export", export_session)
    graph.add_node("diagnoser", diagnose)
    graph.add_node("researcher", research)
    graph.add_node("strategy", suggest_strategy)
    graph.add_node("rewriter", rewrite_question)
    graph.add_node("feedback", give_feedback)
    graph.add_node("quiz_generate", generate_quiz)
    graph.add_node("quiz_evaluate", evaluate_quiz)

    graph.set_entry_point("parser")
    graph.add_conditional_edges(
        "parser",
        route_to_agent,
        {
            "tutor": "diagnoser",
            "quiz": "quiz_generate",
            "researcher": "researcher",
        },
    )

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

    graph.add_edge("quiz_generate", END)
    graph.add_edge("quiz_evaluate", END)
    graph.add_edge("researcher", END)
    graph.add_edge("export", END)

    return graph.compile()


def create_parallel_coach_graph():
    """Coach graph with parallel diagnoser + researcher (fan-out/fan-in)."""
    graph = StateGraph(SessionState)

    graph.add_node("parser", parse_input)
    graph.add_node("diagnoser", diagnose)
    graph.add_node("researcher", research)
    graph.add_node("strategy", suggest_strategy)
    graph.add_node("rewriter", rewrite_question)
    graph.add_node("feedback", give_feedback)

    graph.set_entry_point("parser")
    graph.add_edge("parser", "diagnoser")
    graph.add_edge("parser", "researcher")
    graph.add_edge("researcher", "strategy")
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
