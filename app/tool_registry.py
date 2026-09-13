from app.tools import create_url_tool, get_stats_tool


TOOLS = {
    "create_url": create_url_tool,
    "get_stats": get_stats_tool,
}


def get_available_tools() -> list[str]:
    return list(TOOLS.keys())


def get_tool(name: str):
    return TOOLS.get(name)
