# app/services/group_service.py
import logging
from typing import Any

from app.repositories.groups import GroupsTable
from app.repositories.users import UsersTable

logger = logging.getLogger(__name__)


class GroupService:
    """
    グループに関連するビジネスロジックを提供するサービスクラス。
    """

    def __init__(
        self,
        groups_repo: GroupsTable = None,
        users_repo: UsersTable = None,
    ):
        """
        GroupService のインスタンスを初期化する。

        Args:
            groups_repo (GroupsTable, optional): グループ情報にアクセスするためのリポジトリ。
            users_repo (UsersTable, optional): ユーザー情報にアクセスするためのリポジトリ。
        """
        self.groups_repo = groups_repo or GroupsTable()
        self.users_repo = users_repo or UsersTable()

    def get_group_by_id(self, groupid: str) -> dict[str, Any] | None:
        """
        グループIDに基づいてグループ情報を取得する。

        Args:
            groupid (str): 取得対象のグループID。

        Returns:
            dict[str, Any] | None: グループ情報（存在しない場合は None）。
        """
        group = self.groups_repo.get_group_by_id(groupid)
        return group

    def get_group_members(self, groupid: str) -> dict[str, Any] | None:
        """
        指定されたグループに所属するユーザーの一覧を取得する。

        Args:
            groupid (str): 所属ユーザーを取得したいグループID。

        Returns:
            dict[str, Any] | None: 所属メンバー情報を含む辞書（存在しない場合は None）。
        """
        group = self.get_group_by_id(groupid)
        if group is None:
            logger.warning("グループが見つかりません: groupid=%s", groupid)
            return None

        # グループに登録されているユーザーIDのリストを取得
        user_entries = group.get("users", [])

        if not user_entries:
            logger.info("グループに所属するユーザーはいません: groupid=%s", groupid)
            return {"Items": []}

        # バッチでユーザー情報を取得
        users = self.users_repo.batch_get_users_by_ids(user_entries)

        # ユーザー情報を整形してメンバーリストを作成
        members = [
            {
                "userid": user["userid"],
                "username": user.get("username", "unknown"),
            }
            for user in users
        ]

        return {"Items": members}
