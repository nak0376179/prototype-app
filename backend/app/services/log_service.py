# app/services/log_service.py

from typing import Any

from app.repositories.logs import LogsTable


class LogsService:
    def __init__(self, logs_repo: LogsTable = None):
        self.logs_repo = logs_repo or LogsTable()

    def list_logs(
        self,
        groupid: str,
        limit: int = 25,
        startkey: dict[str, Any] | None = None,
        begin: str | None = None,
        end: str | None = None,
        userid: str | None = None,
        type_: str | None = None,
    ) -> dict[str, Any]:
        return self.logs_repo.list_logs(
            groupid=groupid,
            limit=limit,
            startkey=startkey,
            begin=begin,
            end=end,
            userid=userid,
            type_=type_,
        )
