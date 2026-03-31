from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from app.llm import get_llm
from app.prompts.rewriter_prompt import format_rewriter_prompt
from app.prompts.system_prompt import SYSTEM_PROMPT


def rewrite_question(state: dict) -> dict:
    llm = get_llm()
    prompt = format_rewriter_prompt(
        question=state["current_input"],
        diagnosis=state["diagnosis"],
        context=state.get("context"),
        strategy=state.get("strategy"),
    )
    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=prompt),
    ])
    content = response.content.strip()
    rewritten = content
    if "리라이팅:" in content:
        rewritten = content.split("리라이팅:")[1].split("\n")[0].strip()
    return {"rewritten": rewritten}
