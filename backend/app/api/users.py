# app/api/users.py

import json
import logging
from datetime import UTC, datetime

from botocore.exceptions import ClientError
from fastapi import APIRouter, Body, HTTPException, Query, Request
from pydantic import ValidationError

from app.api.utils.auth import AuthContext
from app.schemas.users import (
    ErrorResponse,
    MessageResponse,
    User,
    UserCreate,
    UsersResponse,
    UserUpdate,
)
from app.services.user_service import UsersService
from app.utils.access_log import log_start

logger = logging.getLogger(__name__)
router = APIRouter()
users_service = UsersService()  # クラスのインスタンスとして利用


def get_auth_context(request: Request) -> AuthContext:
    return AuthContext(request)


@router.get(
    "/users",
    response_model=UsersResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Resource not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def list_users(
    request: Request,
    limit: int = Query(25, ge=1, le=1000, description="最大取得数"),
    startkey: str | None = Query(None, description="ExclusiveStartKey相当"),
) -> UsersResponse:
    await log_start(request)

    startkey_dict = json.loads(startkey) if startkey else None
    logger.info(f"Listing users with limit={limit} startkey={startkey_dict}")
    res = users_service.list_users(limit=limit, startkey=startkey_dict)

    # 失敗時、またはデータがない場合
    if not res.is_success or res.data is None:
        raise HTTPException(status_code=res.code, detail=res.detail)

    try:
        # model_validate を使うことで、型チェックとバリデーションが同時に行われます
        validated_users = [User.model_validate(item) for item in res.data.items if item is not None]
    except Exception as e:
        logger.error(f"User validation failed: {e}")
        raise HTTPException(status_code=500, detail="Data integrity error")  # noqa: B904

    return UsersResponse(Items=validated_users, LastEvaluatedKey=res.data.last_evaluated_key)


@router.post(
    "/users",
    response_model=User,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Resource not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def create_user(request: Request, body: UserCreate) -> UserCreate:
    await log_start(request)
    try:
        user = body.model_dump()
        created_user = users_service.create_user(user)
        return UserCreate.model_validate(created_user)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=f"Validation error: {e.errors()}")
    except RuntimeError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ClientError:
        logger.exception("🔥 create_user 例外")
        raise HTTPException(status_code=500, detail="Failed to create user")


@router.get(
    "/users/{userid}",
    response_model=User,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Resource not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def get_user_by_id(
    request: Request,
    userid: str,
) -> User:
    await log_start(request)

    try:
        user = users_service.get_user_by_id(userid)
        if user:
            return User.model_validate(user)
        raise HTTPException(status_code=404, detail="User not found")
    except ClientError:
        logger.exception("🔥 get_user_by_id 例外")
        raise HTTPException(status_code=500, detail="Failed to get user")


@router.put(
    "/users/{userid}",
    response_model=User,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Resource not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def update_user(
    request: Request,
    userid: str,
    user_create: UserCreate,
) -> MessageResponse:
    await log_start(request)
    try:
        # 1. 辞書への変換は別の変数名にするか、直接渡す
        user_data_dict = user_create.model_dump(exclude_unset=True)

        # 2. Service層の呼び出し（ServiceResponseを受け取る）
        res = users_service.update_user(userid, user_data_dict)

        # 3. ServiceResponse の結果に基づいて例外を投げる
        if not res.is_success:
            raise HTTPException(status_code=res.code, detail=res.detail)
        logger.info(f"User updated successfully, UserID: {userid}")
        return MessageResponse(message="OK")
    except ClientError:
        raise HTTPException(status_code=500, detail="Failed to update user")


@router.patch(
    "/users/{userid}",
    response_model=MessageResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Resource not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def update_user_partial(
    request: Request,
    userid: str,
    user_update: UserUpdate = Body(...),
) -> MessageResponse:
    await log_start(request)

    try:
        # 1. 辞書への変換は別の変数名にする
        update_data_dict = user_update.model_dump(exclude_unset=True)
        updated_at = datetime.now(UTC)
        update_data_dict["updated_at"] = updated_at
        res = users_service.update_user_partial(userid, update_data_dict)

        if not res.is_success:
            raise HTTPException(status_code=res.code, detail=res.detail)
        logger.info(f"User partially updated successfully, UserID: {userid}")

        return MessageResponse(message="OK")
    except ClientError:
        raise HTTPException(status_code=500, detail="Failed to update user")


@router.delete(
    "/users/{userid}",
    response_model=MessageResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Resource not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def delete_user(
    request: Request,
    userid: str,
) -> MessageResponse:
    await log_start(request)

    try:
        response = users_service.delete_user(userid)
        if not response.is_success:
            raise HTTPException(status_code=response.code, detail=response.detail)
        logger.info(f"User deleted successfully, UserID: {userid}")
        return MessageResponse(message="OK")
    except RuntimeError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ClientError:
        logger.exception("🔥 delete_user 例外")
        raise HTTPException(status_code=500, detail="Failed to delete user")
