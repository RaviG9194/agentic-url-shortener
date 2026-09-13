from app.llm_agent import (
    build_tool_definitions,
    call_llm,
    execute_llm_action,
    run_llm_agent,
    validate_llm_result,
)
from app.database import SessionLocal


def test_build_tool_definitions():
    tools = build_tool_definitions()

    assert len(tools) == 2
    assert tools[0]["name"] == "create_url"
    assert tools[1]["name"] == "get_stats"


def test_call_llm_without_api_key(monkeypatch):
    monkeypatch.setattr(
        "app.llm_agent.OPENAI_API_KEY",
        None,
    )

    result = call_llm(
        "Shorten https://example.com"
    )

    assert result is None


def test_validate_llm_result():
    result = validate_llm_result(
        {
            "action": "create_url",
            "url": "https://example.com",
            "custom_alias": "example",
            "expires_in_minutes": None,
            "short_code": None,
        }
    )

    assert result is not None
    assert result["action"] == "create_url"


def test_validate_invalid_llm_result():
    result = validate_llm_result(
        {
            "action": "delete_database",
        }
    )

    assert result is None


def test_execute_create_action():
    db = SessionLocal()

    try:
        result = execute_llm_action(
            {
                "action": "create_url",
                "url": "https://example.com",
                "custom_alias": None,
                "expires_in_minutes": None,
                "short_code": None,
            },
            db,
        )

        assert result["success"] is True
        assert result["action"] == "create_url"
        assert result["data"]["short_code"]
    finally:
        db.close()


def test_run_llm_agent_without_api_key(
    monkeypatch,
):
    monkeypatch.setattr(
        "app.llm_agent.OPENAI_API_KEY",
        None,
    )

    db = SessionLocal()

    try:
        result = run_llm_agent(
            "Shorten https://example.com",
            db,
        )

        assert result is None
    finally:
        db.close()
