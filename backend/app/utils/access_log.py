# app/utils/access_log.py

import base64
import json
import logging
from typing import Any

from fastapi import Request

logger = logging.getLogger("access")
logger.setLevel(logging.INFO)


def parse_jwt_username(token: str) -> str:
    try:
        payload = token.split(".")[1]
        padding = "=" * (-len(payload) % 4)
        decoded = base64.urlsafe_b64decode(payload + padding)
        claims = json.loads(decoded)
        # username が無い場合は sub (ID) を返し、それも無ければ "unknown"
        return claims.get("cognito:username") or claims.get("sub") or "unknown"
    except Exception as e:
        logger.warning(f"[JWT Decode Error] {repr(e)}")
        return "unknown"


async def log_start(request: Request) -> dict[str, Any]:
    path = request.url.path
    query = dict(request.query_params)
    method = request.method
    headers = dict(request.headers)

    # request.client が None でないことを確認
    client_ip = request.client.host if request.client else "unknown"

    auth_header = headers.get("authorization", "")
    token = ""
    if auth_header.lower().startswith("bearer "):
        parts = auth_header.split(" ")
        if len(parts) == 2:
            token = parts[1]

    username = parse_jwt_username(token) if token else "unknown"

    body_str: str | None = None
    if method in ["POST", "PUT", "PATCH"]:
        try:
            body = await request.body()
            body_str = body.decode("utf-8")[:500]
        except Exception:
            body_str = "unreadable"

    log_entry = {"api": method + " " + path, "query": query, "user": username, "ip": client_ip}

    if body_str:
        log_entry["body"] = body_str

    # # structured log for backend
    # logger.info(json.dumps({**log_entry, "event": "start"}))

    # access-log-like plain format
    query_str = f"?{request.url.query}" if request.url.query else ""
    logger.info(f'▶️ {client_ip} - "{method} {path}{query_str} HTTP/1.1" by {username} START')

    return log_entry
