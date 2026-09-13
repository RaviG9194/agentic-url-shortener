from app.tool_registry import (
    get_available_tools,
    get_tool,
)


def test_available_tools():
    tools = get_available_tools()

    assert "create_url" in tools
    assert "get_stats" in tools


def test_get_create_url_tool():
    tool = get_tool("create_url")

    assert tool is not None
    assert tool.__name__ == "create_url_tool"


def test_get_stats_tool():
    tool = get_tool("get_stats")

    assert tool is not None
    assert tool.__name__ == "get_stats_tool"


def test_unknown_tool_returns_none():
    tool = get_tool("does_not_exist")

    assert tool is None
