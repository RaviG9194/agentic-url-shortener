from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field, HttpUrl
from sqlalchemy.orm import Session

from app.agent import run_agent
from app.database import Base, engine, get_db
from app.schemas import AgentResponse
from app.services import (
    create_short_url,
    get_url_by_short_code,
    get_url_stats,
    record_click,
)


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Agentic URL Shortener",
    description=(
        "An agentic URL shortener built with "
        "FastAPI, SQLite, and SQLAlchemy."
    ),
    version="1.0.0",
)


class URLRequest(BaseModel):
    url: HttpUrl
    custom_alias: str | None = Field(
        default=None,
        min_length=3,
        max_length=20,
        pattern=r"^[a-zA-Z0-9_-]+$",
    )
    expires_in_minutes: int | None = Field(
        default=None,
        gt=0,
        le=525600,
    )


class AgentRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=1000,
    )


@app.get("/")
def home():
    return {
        "message": "Agentic URL Shortener is running!"
    }


@app.post("/api/v1/urls")
def create_url(
    request: URLRequest,
    db: Session = Depends(get_db),
):
    try:
        new_url = create_short_url(
            db=db,
            original_url=str(request.url),
            custom_alias=request.custom_alias,
            expires_in_minutes=request.expires_in_minutes,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=409,
            detail=str(error),
        ) from error

    return {
        "short_code": new_url.short_code,
        "short_url": (
            f"http://127.0.0.1:8000/"
            f"{new_url.short_code}"
        ),
        "original_url": new_url.original_url,
        "expires_at": new_url.expires_at,
    }


@app.post(
    "/api/v1/agent",
    response_model=AgentResponse,
)
def agent_endpoint(
    request: AgentRequest,
    db: Session = Depends(get_db),
):
    return run_agent(
        message=request.message,
        db=db,
    )


@app.get("/api/v1/urls/{short_code}/stats")
def get_statistics(
    short_code: str,
    db: Session = Depends(get_db),
):
    url_record = get_url_stats(
        db=db,
        short_code=short_code,
    )

    if url_record is None:
        raise HTTPException(
            status_code=404,
            detail="Short URL not found.",
        )

    return {
        "short_code": url_record.short_code,
        "original_url": url_record.original_url,
        "click_count": url_record.click_count,
        "created_at": url_record.created_at,
        "expires_at": url_record.expires_at,
        "is_active": url_record.is_active,
    }


@app.get("/{short_code}")
def redirect_to_original(
    short_code: str,
    db: Session = Depends(get_db),
):
    url_record = get_url_by_short_code(
        db=db,
        short_code=short_code,
    )

    if url_record is None:
        raise HTTPException(
            status_code=404,
            detail="Short URL not found.",
        )

    if not url_record.is_active:
        raise HTTPException(
            status_code=410,
            detail="Short URL is inactive.",
        )

    if (
        url_record.expires_at is not None
        and url_record.expires_at <= datetime.now(timezone.utc).replace(tzinfo=None)
    ):
        raise HTTPException(
            status_code=410,
            detail="Short URL has expired.",
        )

    record_click(
        db=db,
        url_record=url_record,
    )

    return RedirectResponse(
        url=url_record.original_url
    )
