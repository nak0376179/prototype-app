# app/services/auth.py

import base64
import json
import logging

from app.repositories.groups import GroupsTable
from app.repositories.users import UsersTable
from fastapi import HTTPException, Request

logger = logging.getLogger(__name__)


def parse_jwt_payload(token: str) -> dict:
    try:
        payload = token.split(".")[1]
        padding = "=" * (-len(payload) % 4)  # Base64URLパディング調整
        decoded = base64.urlsafe_b64decode(payload + padding)
        return json.loads(decoded)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid JWT format")


class AuthContext:
    def __init__(
        self,
        request: Request,
        groups_repo: GroupsTable = None,
        users_repo: UsersTable = None,
    ):
        self.groups_repo = groups_repo or UsersTable()
        self.users_repo = users_repo or UsersTable()
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing Authorization header")

        token = auth_header.split(" ")[1]
        claims = parse_jwt_payload(token)
        userid = claims.get("cognito:username", "unknown")
        self.userid = userid
        self.group_roles = ["view_logs"]
        # self.group_roles = {m["groupid"]: m["role"] for m in claims.get("group_memberships", [])}

    def is_member_of(self, groupid: str) -> bool:
        return groupid in self.group_roles

    def get_role_in(self, _groupid: str) -> str | None:
        return "view_logs"  # self.group_roles.get(groupid)
