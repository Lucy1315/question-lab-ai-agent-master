from __future__ import annotations

from typing import List, Optional, TypedDict


class Attempt(TypedDict):
    question: str
    diagnosis: str
    problem_type: str  # "specificity" | "structure" | "both" | "good"
    strategy: Optional[str]
    rewritten: Optional[str]
    score: int
    feedback: str


class ResearchResult(TypedDict):
    examples: List[str]
    framework: str


class SessionState(TypedDict):
    context: Optional[str]
    mode: str  # "coach" | "quiz" | "research"
    attempts: List[Attempt]
    current_input: str
    user_decision: str  # "accept" | "edit" | "retry"
    research: Optional[ResearchResult]
    quiz_history: Optional[List[dict]]
    # transient fields set by diagnoser and consumed by downstream nodes
    diagnosis: Optional[str]
    problem_type: Optional[str]
    score: Optional[int]
    strategy: Optional[str]
    rewritten: Optional[str]
