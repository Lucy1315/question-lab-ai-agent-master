from __future__ import annotations
from app.state import SessionState


def parse_input(state: SessionState) -> dict:
    current_input = state["current_input"].strip()
    if not current_input:
        return {"current_input": "", "error": "empty_input"}
    return {"current_input": current_input}
