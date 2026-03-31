from __future__ import annotations

AGENT_ROUTE_MAP = {
    "coach": "tutor",
    "quiz": "quiz",
    "research": "researcher",
}


def route_to_agent(state: dict) -> str:
    if state.get("error"):
        return "end"
    mode = state.get("mode", "coach")
    return AGENT_ROUTE_MAP.get(mode, "tutor")
