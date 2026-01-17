# app/api/users.py

import json
import logging

from app.api.utils.auth import AuthContext
from app.api.utils.responses import CustomErrorResponses
from app.models.users import MessageResponse, User, UserCreate, UsersResponse, UserUpdate
from app.services.user_service import UsersService
from app.utils.access_log import log_start
from botocore.exceptions import ClientError
from fastapi import APIRouter, Body, HTTPException, Query, Request
from pydantic import ValidationError

logger = logging.getLogger(__name__)
router = APIRouter()
users_service = UsersService()  # クラスのインスタンスとして利用


def get_auth_context(request: Request) -> AuthContext:
    return AuthContext(request)


@router.get("/users", response_model=UsersResponse, responses=CustomErrorResponses)
async def list_users(
    request: Request,
    limit: int = Query(25, ge=1, le=1000, description="最大取得数"),
    startkey: str | None = Query(None, description="ExclusiveStartKey相当"),
):
    await log_start(request)
    try:
        startkey_dict = json.loads(startkey) if startkey else None
        logger.info(f"Listing users with limit={limit} startkey={startkey_dict}")
        return users_service.list_users(limit=limit, startkey=startkey_dict)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid startkey format")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.exception("🔥 list_users 例外")
        raise HTTPException(status_code=500, detail="Failed to list users")


@router.post("/users", response_model=User, responses=CustomErrorResponses)
async def create_user(request: Request, user: User):
    await log_start(request)
    try:
        user = user.model_dump()
        created_user = users_service.create_user(user)
        return created_user
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=f"Validation error: {e.errors()}")
    except RuntimeError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ClientError:
        logger.exception("🔥 create_user 例外")
        raise HTTPException(status_code=500, detail="Failed to create user")


@router.get("/users/{userid}", response_model=User, responses=CustomErrorResponses)
async def get_user_by_id(
    request: Request,
    userid: str,
):
    await log_start(request)

    try:
        user = users_service.get_user_by_id(userid)
        if user:
            return user
        raise HTTPException(status_code=404, detail="User not found")
    except ClientError:
        logger.exception("🔥 get_user_by_id 例外")
        raise HTTPException(status_code=500, detail="Failed to get user")


@router.put("/users/{userid}", response_model=User, responses=CustomErrorResponses)
async def update_user(
    request: Request,
    userid: str,
    user_create: UserCreate,
):
    await log_start(request)
    try:
        user_create = user_create.model_dump()
        updated_user = users_service.update_user(userid, user_create)
        logger.info(f"User updated successfully, UserID: {userid}")
        return updated_user
    except RuntimeError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=f"Validation error: {e.errors()}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            raise HTTPException(status_code=404, detail="User not found")
        logger.exception("🔥 update_user 例外")
        raise HTTPException(status_code=500, detail="Failed to update user")


@router.patch("/users/{userid}", response_model=MessageResponse, responses=CustomErrorResponses)
async def update_user_partial(
    request: Request,
    userid: str,
    user_update: UserUpdate = Body(...),
):
    await log_start(request)

    try:
        user_update = user_update.model_dump(exclude_unset=True)
        updated_user = users_service.update_user_partial(userid, user_update)
        logger.info(f"User partially updated successfully, UserID: {userid}")
        return updated_user
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=f"Validation error: {e.errors()}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            raise HTTPException(status_code=404, detail="User not found")
        logger.exception("🔥 update_user_partial 例外")
        raise HTTPException(status_code=500, detail="Failed to update user")


@router.delete("/users/{userid}", response_model=MessageResponse, responses=CustomErrorResponses)
async def delete_user(
    request: Request,
    userid: str,
):
    await log_start(request)

    try:
        response = users_service.delete_user(userid)
        logger.info(f"User deleted successfully, UserID: {userid}")
        return response
    except RuntimeError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ClientError:
        logger.exception("🔥 delete_user 例外")
        raise HTTPException(status_code=500, detail="Failed to delete user")
