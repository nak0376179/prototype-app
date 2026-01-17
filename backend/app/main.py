# app/main.py

import logging
import os
import time

from app.api import groups, logs, root, users
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO, format="%(name)s: %(message)s")


logger = logging.getLogger("access")


app = FastAPI(
    title="FastAPIアプリケーション",
    version="1.0.0",
    openapi_tags=[
        {"name": "root", "description": "health check"},
        {"name": "users", "description": "User管理に関する操作。"},
        {"name": "groups", "description": "Group管理に関する操作。"},
        {"name": "logs", "description": "logに関する操作。"},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_access_middleware(request: Request, call_next):
    # pytest中ならログをスキップ
    if "PYTEST_CURRENT_TEST" in os.environ:
        return await call_next(request)

    if request.method == "OPTIONS":
        return await call_next(request)

    start_time = time.time()
    response: Response = await call_next(request)
    duration = time.time() - start_time

    client_ip = request.client.host if request.client else "unknown"
    method = request.method
    path = request.url.path
    query_str = f"?{request.url.query}" if request.url.query else ""
    status_code = response.status_code

    logger.info(f'{client_ip} - "{method} {path}{query_str} HTTP/1.1" {status_code} ({duration:.2f}s)')
    return response


app.include_router(root.router, tags=["root"])
app.include_router(users.router, tags=["users"])
app.include_router(groups.router, tags=["groups"])
app.include_router(logs.router, tags=["logs"])
