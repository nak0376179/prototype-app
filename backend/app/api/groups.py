# app/api/groups.py
import logging

from app.api.utils.auth import AuthContext
from app.api.utils.authorization import authorize_group_access
from app.api.utils.responses import CustomErrorResponses
from app.models.groups import Group
from app.models.users import UsersBriefResponse
from app.services.group_service import GroupService
from app.utils.access_log import log_start
from fastapi import APIRouter, Depends, HTTPException, Request

logger = logging.getLogger(__name__)
router = APIRouter()
group_service = GroupService()


def get_auth_context(request: Request) -> AuthContext:
    return AuthContext(request)


@router.get(
    "/groups/{groupid}",
    response_model=Group,
    summary="グループ情報の取得",
    description="指定したグループIDに該当するグループの詳細情報を取得します。",
    responses=CustomErrorResponses,
)
async def read_group(
    groupid: str,
    request: Request,
    auth: AuthContext = Depends(get_auth_context),
):
    await log_start(request)
    authorize_group_access(auth, groupid, required_permission="read_group")

    try:
        group = group_service.get_group_by_id(groupid)
    except Exception:
        logger.exception(f"🔥 read_group 例外 - groupid={groupid}")
        raise HTTPException(status_code=500, detail="Failed to retrieve group")

    if not group:
        logger.warning(f"Group not found - groupid={groupid}")
        raise HTTPException(status_code=404, detail="Group not found")

    logger.info(f"Group retrieved successfully - groupid={groupid}")
    return group


@router.get(
    "/groups/{groupid}/users",
    response_model=UsersBriefResponse,
    summary="グループメンバーの取得",
    description="指定されたグループIDに所属するユーザー一覧を取得します。",
)
async def get_group_members(
    groupid: str,
    request: Request,
    auth: AuthContext = Depends(get_auth_context),
):
    await log_start(request)
    authorize_group_access(auth, groupid, required_permission="get_members")

    try:
        members = group_service.get_group_members(groupid)
    except Exception:
        logger.exception(f"🔥 get_group_members 例外 - groupid={groupid}")
        raise HTTPException(status_code=500, detail="Failed to retrieve group members")

    if members is None:
        logger.warning(f"Group not found when getting members - groupid={groupid}")
        raise HTTPException(status_code=404, detail="Group not found")

    logger.info(f"Group members retrieved successfully - groupid={groupid}")
    return members
