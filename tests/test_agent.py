from uuid import uuid4

from app.agent import AgentIntent, classify_request, run_agent
from app.database import SessionLocal


def test_agent_detects_create_intent():
    result = classify_request(
        "Please shorten this URL"
    )

    assert result.intent == AgentIntent.CREATE_URL


def test_agent_detects_stats_intent():
    result = classify_request(
        "How many clicks did abc123 get?"
    )

    assert result.intent == AgentIntent.GET_STATS


def test_agent_detects_unknown_request():
    result = classify_request(
        "What is the weather today?"
    )

    assert result.intent == AgentIntent.UNKNOWN


def test_agent_extracts_url():
    result = classify_request(
        "Shorten https://example.com"
    )

    assert result.intent == AgentIntent.CREATE_URL
    assert result.url == "https://example.com"


def test_agent_extracts_alias():
    result = classify_request(
        "Shorten https://example.com with alias portfolio"
    )

    assert result.custom_alias == "portfolio"


def test_agent_extracts_days():
    result = classify_request(
        "Shorten https://example.com for 30 days"
    )

    assert result.expires_in_minutes == 30 * 24 * 60


def test_agent_extracts_hours():
    result = classify_request(
        "Shorten https://example.com for 2 hours"
    )

    assert result.expires_in_minutes == 2 * 60


def test_agent_extracts_complete_request():
    result = classify_request(
        "Shorten https://example.com "
        "with alias portfolio for 30 days"
    )

    assert result.intent == AgentIntent.CREATE_URL
    assert result.url == "https://example.com"
    assert result.custom_alias == "portfolio"
    assert result.expires_in_minutes == 30 * 24 * 60


def test_agent_executes_create_tool():
    db = SessionLocal()

    try:
        custom_alias = f"agent-{uuid4().hex[:8]}"

        result = run_agent(
            message=(
                "Shorten https://example.com "
                f"with alias {custom_alias}"
            ),
            db=db,
        )

        assert result["success"] is True
        assert result["action"] == "create_url"
        assert result["data"]["short_code"] == custom_alias
    finally:
        db.close()


def test_agent_executes_stats_tool():
    db = SessionLocal()

    try:
        custom_alias = f"stats-{uuid4().hex[:8]}"

        create_result = run_agent(
            message=(
                "Shorten https://example.com "
                f"with alias {custom_alias}"
            ),
            db=db,
        )

        assert create_result["success"] is True

        stats_result = run_agent(
            message=(
                "How many clicks did "
                f"{custom_alias} get?"
            ),
            db=db,
        )

        assert stats_result["success"] is True
        assert stats_result["action"] == "get_stats"
        assert stats_result["data"]["click_count"] == 0
    finally:
        db.close()


def test_agent_handles_missing_url():
    db = SessionLocal()

    try:
        result = run_agent(
            message="Please shorten this URL",
            db=db,
        )

        assert result["success"] is False
        assert "could not find a URL" in result["message"]
    finally:
        db.close()


def test_agent_handles_missing_short_code():
    db = SessionLocal()

    try:
        result = run_agent(
            message="How many clicks did this get?",
            db=db,
        )

        assert result["success"] is False
        assert "could not find the short code" in result["message"]
    finally:
        db.close()


def test_agent_handles_unknown_request():
    db = SessionLocal()

    try:
        result = run_agent(
            message="Tell me a joke",
            db=db,
        )

        assert result["success"] is False
        assert "could not understand" in result["message"]
    finally:
        db.close()
