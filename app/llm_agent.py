import json
from typing import Any

from sqlalchemy.orm import Session

from app.config import OPENAI_API_KEY, OPENAI_MODEL
from app.tools import create_url_tool, get_stats_tool


SYSTEM_PROMPT = """
You are the decision-making agent for an Agentic URL Shortener.

Your job is to understand the user's request and decide which
available tool should be used.

Available tools:

1. create_url
   Use this when the user wants to shorten or create a short URL.

2. get_stats
   Use this when the user wants click statistics for a short URL.

3. none
   Use this when the request is unrelated or missing required information.

Return ONLY valid JSON in this format:

{
    "action": "create_url | get_stats | none",
    "url": "URL or null",
    "custom_alias": "alias or null",
    "expires_in_minutes": number or null,
    "short_code": "short code or null"
}

Never invent a URL or short code.
Never execute code.
Never generate SQL.
"""


def build_tool_definitions() -> list[dict[str, Any]]:
    return [
        {
            "name": "create_url",
            "description": (
                "Create a shortened URL. "
                "Requires a valid URL."
            ),
        },
        {
            "name": "get_stats",
            "description": (
                "Get click statistics for an existing "
                "short URL."
            ),
        },
    ]


def call_llm(message: str) -> dict[str, Any] | None:
    if not OPENAI_API_KEY:
        return None

    try:
        from openai import OpenAI

        client = OpenAI(
            api_key=OPENAI_API_KEY,
        )

        response = client.responses.create(
            model=OPENAI_MODEL,
            instructions=SYSTEM_PROMPT,
            input=message,
        )

        text = response.output_text.strip()

        result = json.loads(text)

        if not isinstance(result, dict):
            return None

        return result

    except Exception:
        return None


def validate_llm_result(
    result: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if result is None:
        return None

    allowed_actions = {
        "create_url",
        "get_stats",
        "none",
    }

    action = result.get("action")

    if action not in allowed_actions:
        return None

    return {
        "action": action,
        "url": result.get("url"),
        "custom_alias": result.get(
            "custom_alias"
        ),
        "expires_in_minutes": result.get(
            "expires_in_minutes"
        ),
        "short_code": result.get(
            "short_code"
        ),
    }


def execute_llm_action(
    result: dict[str, Any],
    db: Session,
) -> dict[str, Any]:
    action = result["action"]

    if action == "create_url":
        url = result.get("url")

        if not url:
            return {
                "success": False,
                "action": "create_url",
                "message": (
                    "I understood that you want "
                    "to create a short URL, but "
                    "I could not find a URL."
                ),
            }

        tool_result = create_url_tool(
            db=db,
            url=url,
            custom_alias=result.get(
                "custom_alias"
            ),
            expires_in_minutes=result.get(
                "expires_in_minutes"
            ),
        )

        if not tool_result["success"]:
            return {
                "success": False,
                "action": "create_url",
                "message": tool_result["error"],
            }

        return {
            "success": True,
            "action": "create_url",
            "message": (
                f"Your short URL is "
                f"{tool_result['short_url']}"
            ),
            "data": tool_result,
        }

    if action == "get_stats":
        short_code = result.get("short_code")

        if not short_code:
            return {
                "success": False,
                "action": "get_stats",
                "message": (
                    "I understood that you want "
                    "URL statistics, but I could "
                    "not find the short code."
                ),
            }

        tool_result = get_stats_tool(
            db=db,
            short_code=short_code,
        )

        if not tool_result["success"]:
            return {
                "success": False,
                "action": "get_stats",
                "message": tool_result["error"],
            }

        return {
            "success": True,
            "action": "get_stats",
            "message": (
                f"The short URL "
                f"{tool_result['short_code']} "
                f"has "
                f"{tool_result['click_count']} "
                f"clicks."
            ),
            "data": tool_result,
        }

    return {
        "success": False,
        "action": "none",
        "message": (
            "I could not understand your request. "
            "You can ask me to shorten a URL or "
            "show statistics for a short URL."
        ),
    }


def run_llm_agent(
    message: str,
    db: Session,
) -> dict[str, Any] | None:
    llm_result = call_llm(message)

    validated_result = validate_llm_result(
        llm_result
    )

    if validated_result is None:
        return None

    return execute_llm_action(
        result=validated_result,
        db=db,
    )
