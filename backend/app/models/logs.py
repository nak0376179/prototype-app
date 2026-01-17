from pydantic import BaseModel


class LogItem(BaseModel):
    groupid: str
    created_at: str
    userid: str | None
    username: str | None
    type: str | None
    message: str | None


class LogsResponse(BaseModel):
    Items: list[LogItem]
    LastEvaluatedKey: dict | None = None
