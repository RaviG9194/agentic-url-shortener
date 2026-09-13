import secrets
import string
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models import URL


def generate_short_code(length: int = 6) -> str:
    characters = string.ascii_letters + string.digits

    return "".join(
        secrets.choice(characters)
        for _ in range(length)
    )


def create_short_url(
    db: Session,
    original_url: str,
    custom_alias: str | None = None,
    expires_in_minutes: int | None = None,
) -> URL:
    short_code = custom_alias

    if short_code is not None:
        existing_url = (
            db.query(URL)
            .filter(URL.short_code == short_code)
            .first()
        )

        if existing_url is not None:
            raise ValueError(
                "Custom alias already exists."
            )
    else:
        while True:
            short_code = generate_short_code()

            existing_url = (
                db.query(URL)
                .filter(URL.short_code == short_code)
                .first()
            )

            if existing_url is None:
                break

    expires_at = None

    if expires_in_minutes is not None:
        expires_at = (
            datetime.now(timezone.utc)
            + timedelta(minutes=expires_in_minutes)
        )

    url_record = URL(
        original_url=original_url,
        short_code=short_code,
        expires_at=expires_at,
    )

    db.add(url_record)
    db.commit()
    db.refresh(url_record)

    return url_record


def get_url_by_short_code(
    db: Session,
    short_code: str,
) -> URL | None:
    return (
        db.query(URL)
        .filter(URL.short_code == short_code)
        .first()
    )


def record_click(
    db: Session,
    url_record: URL,
) -> URL:
    url_record.click_count += 1

    db.commit()
    db.refresh(url_record)

    return url_record


def get_url_stats(
    db: Session,
    short_code: str,
) -> URL | None:
    return get_url_by_short_code(
        db=db,
        short_code=short_code,
    )
