# app/services/group_service.py
import logging

# 定義した型をインポート
from app.models.common import ServiceResponse, SingleItemData
from app.repositories.group_repo import GroupsTable
from app.repositories.user_repo import UsersTable

logger = logging.getLogger(__name__)


class GroupService:
    def __init__(
        self,
        groups_repo: GroupsTable | None = None,
        users_repo: UsersTable | None = None,
    ):
        self.groups_repo = groups_repo or GroupsTable()
        self.users_repo = users_repo or UsersTable()

    def get_group_by_id(self, groupid: str) -> ServiceResponse[SingleItemData]:
        """グループIDに基づいてグループ情報を取得する。"""
        repo_res = self.groups_repo.get_group_by_id(groupid)

        return ServiceResponse(
            code=repo_res.code,
            data=repo_res.data,
            detail=repo_res.detail,
        )

    def get_group_members(self, groupid: str) -> ServiceResponse[SingleItemData]:
        """指定されたグループに所属するユーザーの一覧を取得する。"""
        # 1. グループ情報の取得
        repo_res = self.get_group_by_id(groupid)
        return ServiceResponse(
            code=repo_res.code,
            data=repo_res.data,
            detail=repo_res.detail,
        )
