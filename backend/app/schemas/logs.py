from typing import Any

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: str


class LogItem(BaseModel):
    groupid: str
    created_at: str
    userid: str | None
    username: str | None
    type: str | None
    message: str | None


class LogsResponse(BaseModel):
    Items: list[LogItem]
    LastEvaluatedKey: dict[str, Any] | None = None
