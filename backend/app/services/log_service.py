# app/services/log_service.py

from typing import Any

from app.models.common import ListItemData, ServiceResponse
from app.repositories.log_repo import LogsTable


class LogsService:
    def __init__(self, logs_repo: LogsTable | None = None):
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
    ) -> ServiceResponse[ListItemData]:
        res = self.logs_repo.list_logs(
            groupid=groupid,
            limit=limit,
            startkey=startkey,
            begin=begin,
            end=end,
            userid=userid,
            type_=type_,
        )
        return ServiceResponse(code=res.code, data=res.data, detail=res.detail)
