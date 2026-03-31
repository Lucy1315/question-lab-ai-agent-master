import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_ENV_PATH, override=True)


def _get_api_key() -> str:
    """Get API key from environment or Streamlit secrets."""
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        try:
            import streamlit as st
            if "OPENAI_API_KEY" in st.secrets:
                key = st.secrets["OPENAI_API_KEY"]
        except Exception:
            pass
    if not key:
        raise RuntimeError(
            "OPENAI_API_KEY not found. "
            "Set it in .env or Streamlit Cloud Secrets."
        )
    return key


@lru_cache(maxsize=1)
def get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model="gpt-4o-mini",
        api_key=_get_api_key(),
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
