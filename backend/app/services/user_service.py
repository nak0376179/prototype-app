from typing import Any

from app.repositories.users import UsersTable


class UsersService:
    def __init__(self, users_repo: UsersTable = None):
        self.users_repo = users_repo or UsersTable()

    def fetch_users_by_ids(self, user_ids: list[str]) -> list[dict[str, Any]]:
        """
        複数のユーザーIDからユーザー情報を取得する。
        """
        return self.users_repo.batch_get_users_by_ids(user_ids)

    def get_user_by_id(self, userid: str) -> dict[str, Any] | None:
        return self.users_repo.get_user_by_id(userid)

    def batch_get_users_by_ids(self, userids: list[str]) -> list[dict[str, Any]]:
        return self.users_repo.batch_get_users_by_ids(userids)

    def list_users(self, limit: int = 25, startkey: dict[str, Any] | None = None):
        return self.users_repo.list_users(
            limit=limit,
            expr_attr_names=None,
            expr_attr_values=None,
            filter_expr=None,
            exclusive_start_key=startkey,
        )

    def create_user(self, user: dict[str, Any]):
        return self.users_repo.create_user(user)

    def update_user(self, userid: str, user_data: dict[str, Any]):
        return self.users_repo.update_user(userid, user_data)

    def update_user_partial(self, userid: str, update_data: dict[str, Any]):
        return self.users_repo.update_user_partial(userid, update_data)

    def delete_user(self, userid: str):
        return self.users_repo.delete_user(userid)
