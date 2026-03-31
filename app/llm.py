import os

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic

load_dotenv()


def get_llm() -> ChatAnthropic:
    return ChatAnthropic(
        model="claude-sonnet-4-20250514",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        max_tokens=2048,
    )
