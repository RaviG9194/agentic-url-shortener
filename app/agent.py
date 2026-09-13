import re
from dataclasses import dataclass
from enum import Enum

from sqlalchemy.orm import Session

from app.llm_agent import run_llm_agent
from app.tools import (
    create_url_tool,
    get_stats_tool,
)


class AgentIntent(str, Enum):
    CREATE_URL = "create_url"
    GET_STATS = "get_stats"
    UNKNOWN = "unknown"


@dataclass
class AgentRequest:
    intent: AgentIntent
    url: str | None = None
    custom_alias: str | None = None
    expires_in_minutes: int | None = None
    short_code: str | None = None


def extract_url(message: str) -> str | None:
    match = re.search(
        r"https?://[^\s]+",
        message,
        re.IGNORECASE,
    )

    if match is None:
        return None

    return match.group(0).rstrip(".,!?)]}")


def extract_alias(message: str) -> str | None:
    patterns = [
        r"\balias\s*(?:is|=|:)?\s*([a-zA-Z0-9_-]+)",
        r"\bname\s*(?:is|=|:)?\s*([a-zA-Z0-9_-]+)",
        r"\bas\s+([a-zA-Z0-9_-]+)",
        r"\bcalled\s+([a-zA-Z0-9_-]+)",
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            message,
            re.IGNORECASE,
        )

        if match:
            return match.group(1)

    return None


def extract_expiration(message: str) -> int | None:
    match = re.search(
        r"(\d+)\s*(minute|minutes|hour|hours|day|days|week|weeks)",
        message,
        re.IGNORECASE,
    )

    if match is None:
        return None

    amount = int(match.group(1))
    unit = match.group(2).lower()

    multipliers = {
        "minute": 1,
        "minutes": 1,
        "hour": 60,
        "hours": 60,
        "day": 24 * 60,
        "days": 24 * 60,
        "week": 7 * 24 * 60,
        "weeks": 7 * 24 * 60,
    }

    return amount * multipliers[unit]


def extract_short_code(message: str) -> str | None:
    patterns = [
        r"(?:clicks|stats|statistics)\s+(?:for|of|on)\s+([a-zA-Z0-9_-]{3,20})",
        r"(?:short code|shortcode)\s*(?:is|=|:)?\s*([a-zA-Z0-9_-]{3,20})",
        r"(?:URL|url)\s+([a-zA-Z0-9_-]{3,20})\s+(?:stats|statistics)",
        r"clicks?\s+(?:did|does)\s+([a-zA-Z0-9_-]{3,20})",
    ]

    invalid_values = {
        "this",
        "that",
        "it",
        "the",
        "my",
        "your",
        "url",
        "short",
        "link",
        "one",
    }

    for pattern in patterns:
        match = re.search(
            pattern,
            message,
            re.IGNORECASE,
        )

        if match:
            candidate = match.group(1)

            if candidate.lower() in invalid_values:
                return None

            return candidate

    return None


def classify_request(message: str) -> AgentRequest:
    normalized_message = message.lower().strip()

    # Check creation requests FIRST.
    #
    # This prevents words such as "stats" or "clicks"
    # inside a custom alias from being treated as an
    # entirely different intent.
    if (
        "shorten" in normalized_message
        or "short url" in normalized_message
        or "shorten url" in normalized_message
    ):
        return AgentRequest(
            intent=AgentIntent.CREATE_URL,
            url=extract_url(message),
            custom_alias=extract_alias(message),
            expires_in_minutes=extract_expiration(message),
        )

    # Check statistics requests after creation requests.
    if (
        "click" in normalized_message
        or "stats" in normalized_message
        or "statistics" in normalized_message
    ):
        return AgentRequest(
            intent=AgentIntent.GET_STATS,
            short_code=extract_short_code(message),
        )

    return AgentRequest(
        intent=AgentIntent.UNKNOWN,
    )


def run_rule_based_agent(
    message: str,
    db: Session,
) -> dict:
    request = classify_request(message)

    if request.intent == AgentIntent.CREATE_URL:
        if request.url is None:
            return {
                "success": False,
                "message": (
                    "I understood that you want to "
                    "create a short URL, but I could "
                    "not find a URL in your request."
                ),
            }

        result = create_url_tool(
            db=db,
            url=request.url,
            custom_alias=request.custom_alias,
            expires_in_minutes=request.expires_in_minutes,
        )

        if not result["success"]:
            return {
                "success": False,
                "message": result["error"],
            }

        return {
            "success": True,
            "action": "create_url",
            "message": (
                f"Your short URL is "
                f"{result['short_url']}"
            ),
            "data": result,
        }

    if request.intent == AgentIntent.GET_STATS:
        if request.short_code is None:
            return {
                "success": False,
                "message": (
                    "I understood that you want "
                    "URL statistics, but I could "
                    "not find the short code."
                ),
            }

        result = get_stats_tool(
            db=db,
            short_code=request.short_code,
        )

        if not result["success"]:
            return {
                "success": False,
                "message": result["error"],
            }

        return {
            "success": True,
            "action": "get_stats",
            "message": (
                f"The short URL "
                f"{result['short_code']} has "
                f"{result['click_count']} clicks."
            ),
            "data": result,
        }

    return {
        "success": False,
        "message": (
            "I could not understand your request. "
            "You can ask me to shorten a URL or "
            "show statistics for a short URL."
        ),
    }


def run_agent(
    message: str,
    db: Session,
) -> dict:
    """
    Main agent entry point.

    The LLM is attempted first when configured.
    If the LLM is unavailable or produces an
    invalid response, the deterministic
    rule-based agent is used as a fallback.
    """

    llm_result = run_llm_agent(
        message=message,
        db=db,
    )

    if llm_result is not None:
        return llm_result

    return run_rule_based_agent(
        message=message,
        db=db,
    )
