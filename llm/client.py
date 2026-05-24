"""OpenAI client initialization. Model is configurable via .env."""

import os
from functools import lru_cache

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


@lru_cache(maxsize=1)
def get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=MODEL,
        temperature=0.8,
        api_key=os.getenv("OPENAI_API_KEY"),
    )


@lru_cache(maxsize=1)
def get_structured_llm(schema: type) -> ChatOpenAI:
    """LLM configured to return structured JSON for modifier classification."""
    return get_llm().with_structured_output(schema)
