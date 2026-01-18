# app/api/groups.py
import logging

from fastapi import APIRouter, Depends, HTTPException, Request

from app.api.utils.auth import AuthContext
from app.api.utils.authorization import authorize_group_access
from app.schemas.groups import Group
from app.schemas.users import ErrorResponse, UserBrief, UsersBriefResponse
from app.services.group_service import GroupService
from app.utils.access_log import log_start

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
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Resource not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def read_group(
    groupid: str,
    request: Request,
    auth: AuthContext = Depends(get_auth_context),
) -> Group:
    await log_start(request)
    authorize_group_access(auth, groupid, required_permission="read_group")

    res = group_service.get_group_by_id(groupid)
    if res.code != 200:
        logger.exception(f"🔥 read_group 例外 - groupid={groupid}")
        raise HTTPException(status_code=res.code, detail=res.detail)

    logger.info(f"Group retrieved successfully - groupid={groupid}")
    return Group.model_validate(res.data)


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
) -> UsersBriefResponse:
    await log_start(request)
    authorize_group_access(auth, groupid, required_permission="get_members")

    try:
        res = group_service.get_group_members(groupid)
    except Exception:
        logger.exception(f"🔥 get_group_members 例外 - groupid={groupid}")
        raise HTTPException(status_code=500, detail="Failed to retrieve group members")

    if res.data is None:
        logger.warning(f"Group not found when getting members - groupid={groupid}")
        raise HTTPException(status_code=404, detail="Group not found")

    # 1. サービスから返ってきたデータ（リスト）を取得
    # res.data.item が list[dict] または list[User] である前提
    members_data = res.data.item if res.data.item is not None else []

    # 2. 各要素を UserBrief Pydanticモデルに変換してリスト化
    # こうすることで、型が list[UserBrief] に確定します
    validated_members = [UserBrief.model_validate(m) for m in members_data]
    logger.info(f"Group members retrieved successfully - groupid={groupid}")

    return UsersBriefResponse(Items=validated_members)
