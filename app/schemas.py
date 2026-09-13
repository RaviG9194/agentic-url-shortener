from typing import Any

from pydantic import BaseModel


class AgentResponse(BaseModel):
    success: bool
    action: str | None = None
    message: str
    data: dict[str, Any] | None = None
