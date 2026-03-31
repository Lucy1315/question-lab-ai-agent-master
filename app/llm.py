import os
from functools import lru_cache

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()


@lru_cache(maxsize=1)
def get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY"),
        max_tokens=2048,
    )


def invoke_llm(messages: list) -> str:
    """Invoke LLM with error handling. Returns content string or raises."""
    try:
        response = get_llm().invoke(messages)
        return response.content.strip()
    except Exception as e:
        raise LLMError(str(e)) from e


class LLMError(Exception):
    """Raised when LLM API call fails."""


def strip_code_fence(text: str) -> str:
    """Remove markdown code fences (```json ... ```) from LLM output."""
    import re
    m = re.match(r"^```\w*\n(.*?)```$", text, re.DOTALL)
    return m.group(1).strip() if m else text
