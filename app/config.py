import os


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

OPENAI_MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-5.6",
)


def is_llm_available() -> bool:
    return bool(OPENAI_API_KEY)
