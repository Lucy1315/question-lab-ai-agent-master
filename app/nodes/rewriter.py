from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from app.llm import LLMError, invoke_llm
from app.prompts.rewriter_prompt import format_rewriter_prompt
from app.prompts.system_prompt import SYSTEM_PROMPT


def rewrite_question(state: dict) -> dict:
    prompt = format_rewriter_prompt(
        question=state["current_input"],
        diagnosis=state["diagnosis"],
        context=state.get("context"),
        strategy=state.get("strategy"),
    )
    try:
        content = invoke_llm([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ])
    except LLMError as e:
        return {"rewritten": f"리라이팅 중 오류가 발생했습니다: {e}"}
    rewritten = content
    if "리라이팅:" in content:
        rewritten = content.split("리라이팅:")[1].split("\n")[0].strip()
    return {"rewritten": rewritten}
