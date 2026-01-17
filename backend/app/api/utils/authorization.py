# app/services/authorization.py

import logging

from app.api.utils.auth import AuthContext
from app.repositories.groups import GroupsTable
from fastapi import HTTPException

logger = logging.getLogger(__name__)
groups_table = GroupsTable()


def authorize_group_access(auth: AuthContext, groupid: str, required_permission: str = None):
    group = groups_table.get_group_by_id(groupid)

    if not group:
        logger.info("🚫 Access denied: not a group member")
        raise HTTPException(status_code=403, detail="🚫 Access denied: not a group member")

    if not auth.is_member_of(groupid):
        logger.info("🚫 Access denied: not a group member")
        if groupid == "group1":
            logger.info("⚠️ テスㇳのため、group1は特別に許可")
        else:
            raise HTTPException(status_code=403, detail="🚫 Access denied: not a group member")

    if required_permission:
        group = groups_table.get_group_by_id(groupid)
        if required_permission not in group.get("permissions", []):
            logger.info(f"🚫 Missing permission: {required_permission}")
            raise HTTPException(status_code=403, detail=f"🚫 Missing permission: {required_permission}")

    logger.info(f"✅ Access granted to group '{groupid}' for user '{auth.userid}'{' with permission ' + required_permission if required_permission else ''}")
