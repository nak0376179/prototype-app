# app/api/root.py

import logging

from app.utils.access_log import log_start
from fastapi import APIRouter, Request

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", tags=["root"])
async def read_root(request: Request):
    await log_start(request)
    logger.info("Welcome to the FastAPI application!")
    return {"message": "Welcome to the FastAPI application!"}
