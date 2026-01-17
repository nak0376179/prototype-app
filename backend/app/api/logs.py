# app/api/logs.py

import json
import logging

from app.api.utils.auth import AuthContext
from app.api.utils.authorization import authorize_group_access
from app.api.utils.responses import CustomErrorResponses
from app.models.logs import LogsResponse
from app.services.log_service import LogsService
from app.utils.access_log import log_start
from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request

logger = logging.getLogger(__name__)
router = APIRouter()


def get_auth_context(request: Request) -> AuthContext:
    return AuthContext(request)


@router.get("/groups/{groupid}/logs", response_model=LogsResponse, responses=CustomErrorResponses)
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
):
    await log_start(request)
    authorize_group_access(auth, groupid, required_permission="list_logs")
    try:
        logs_service = LogsService()
        startkey = json.loads(startkey) if startkey else None
        result = logs_service.list_logs(
            groupid=groupid,
            userid=userid,
            limit=limit,
            startkey=startkey,
            begin=begin,
            end=end,
            type_=type_,
        )
        logger.info(f"Logs retrieved successfully for groupid={groupid} (count={len(result['Items'])})")
        return result

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid startkey format")
    except Exception:
        logger.exception(f"🔥 list_logs 例外 - groupid={groupid}, userid={userid}")
        raise HTTPException(status_code=500, detail="Failed to list logs")
