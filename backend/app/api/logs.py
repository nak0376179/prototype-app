# app/api/logs.py

import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request

from app.api.utils.auth import AuthContext
from app.api.utils.authorization import authorize_group_access
from app.schemas.logs import ErrorResponse, LogItem, LogsResponse
from app.services.log_service import LogsService
from app.utils.access_log import log_start

logger = logging.getLogger(__name__)
router = APIRouter()


def get_auth_context(request: Request) -> AuthContext:
    return AuthContext(request)


@router.get(
    "/groups/{groupid}/logs",
    response_model=LogsResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Resource not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def list_logs(
    request: Request,
    groupid: str = Path(..., description="グループID（パーティションキー）"),
    limit: int = Query(25, ge=1, le=1000, description="最大取得数"),
    startkey: str | None = Query(None, description="ExclusiveStartKey（JSON文字列）"),
    begin: str | None = Query(None, description="開始日時(ISO)（>=）"),
    end: str | None = Query(None, description="終了日時(ISO)（<=）"),
    userid: str | None = Query(None, description="ユーザーIDでフィルタ"),
    type_: str | None = Query(None, alias="type", description="タイプでフィルタ"),
    auth: AuthContext = Depends(get_auth_context),
) -> LogsResponse:
    await log_start(request)
    authorize_group_access(auth, groupid, required_permission="list_logs")
    try:
        logs_service = LogsService()
        startkey_dict = json.loads(startkey) if startkey else None
        res = logs_service.list_logs(
            groupid=groupid,
            userid=userid,
            limit=limit,
            startkey=startkey_dict,
            begin=begin,
            end=end,
            type_=type_,
        )
        if res.data is None:
            logger.warning(f"No logs found for groupid={groupid}")
            return LogsResponse(Items=[], LastEvaluatedKey=None)
        logs = [LogItem.model_validate(item) for item in res.data.items if item is not None]
        logger.info(f"Logs retrieved successfully for groupid={groupid} (count={res.data.count})")
        return LogsResponse(Items=logs, LastEvaluatedKey=res.data.last_evaluated_key)

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid startkey format")
    except Exception:
        logger.exception(f"🔥 list_logs 例外 - groupid={groupid}, userid={userid}")
        raise HTTPException(status_code=500, detail="Failed to list logs")
