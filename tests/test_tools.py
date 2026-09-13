from uuid import uuid4

from app.database import SessionLocal
from app.tools import create_url_tool, get_stats_tool


def test_create_url_tool():
    db = SessionLocal()

    try:
        result = create_url_tool(
            db=db,
            url="https://example.com",
        )

        assert result["success"] is True
        assert result["short_code"]
        assert result["short_url"]
        assert result["original_url"] == "https://example.com"
    finally:
        db.close()


def test_get_stats_tool():
    db = SessionLocal()

    try:
        custom_alias = f"tool-{uuid4().hex[:8]}"

        create_result = create_url_tool(
            db=db,
            url="https://example.com",
            custom_alias=custom_alias,
        )

        assert create_result["success"] is True

        stats_result = get_stats_tool(
            db=db,
            short_code=custom_alias,
        )

        assert stats_result["success"] is True
        assert stats_result["short_code"] == custom_alias
        assert stats_result["click_count"] == 0
    finally:
        db.close()


def test_get_stats_for_missing_url():
    db = SessionLocal()

    try:
        result = get_stats_tool(
            db=db,
            short_code="does-not-exist",
        )

        assert result["success"] is False
        assert result["error"] == "Short URL not found."
    finally:
        db.close()
