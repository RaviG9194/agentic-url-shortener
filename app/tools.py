from sqlalchemy.orm import Session

from app.services import (
    create_short_url,
    get_url_stats,
)


def create_url_tool(
    db: Session,
    url: str,
    custom_alias: str | None = None,
    expires_in_minutes: int | None = None,
) -> dict:
    try:
        new_url = create_short_url(
            db=db,
            original_url=url,
            custom_alias=custom_alias,
            expires_in_minutes=expires_in_minutes,
        )
    except ValueError as error:
        return {
            "success": False,
            "error": str(error),
        }

    return {
        "success": True,
        "short_code": new_url.short_code,
        "short_url": (
            f"http://127.0.0.1:8000/"
            f"{new_url.short_code}"
        ),
        "original_url": new_url.original_url,
        "expires_at": new_url.expires_at,
    }


def get_stats_tool(
    db: Session,
    short_code: str,
) -> dict:
    url_record = get_url_stats(
        db=db,
        short_code=short_code,
    )

    if url_record is None:
        return {
            "success": False,
            "error": "Short URL not found.",
        }

    return {
        "success": True,
        "short_code": url_record.short_code,
        "original_url": url_record.original_url,
        "click_count": url_record.click_count,
        "created_at": url_record.created_at,
        "expires_at": url_record.expires_at,
        "is_active": url_record.is_active,
    }
