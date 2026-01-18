import logging
from typing import Any

from app.models.common import ListItemData, MessageData, ServiceResponse, SingleItemData
from app.repositories.user_repo import UsersTable

logger = logging.getLogger(__name__)


class UsersService:
    def __init__(self, users_repo: UsersTable | None = None):
        self.users_repo = users_repo or UsersTable()

    def fetch_users_by_ids(self, user_ids: list[str]) -> ServiceResponse[ListItemData]:
        """
        複数のユーザーIDからユーザー情報を取得する。
        """
        res = self.users_repo.batch_get_users_by_ids(user_ids)
        return ServiceResponse(code=res.code, data=res.data, detail=res.detail)

    def get_user_by_id(self, userid: str) -> ServiceResponse[SingleItemData]:
        res = self.users_repo.get_user_by_id(userid)
        return ServiceResponse(code=res.code, data=res.data, detail=res.detail)

    def batch_get_users_by_ids(self, userids: list[str]) -> ServiceResponse[ListItemData]:
        res = self.users_repo.batch_get_users_by_ids(userids)
        return ServiceResponse(code=res.code, data=res.data, detail=res.detail)

    def list_users(self, limit: int = 25, startkey: dict[str, Any] | None = None) -> ServiceResponse[ListItemData]:
        res = self.users_repo.list_users(
            limit=limit,
            expr_attr_names=None,
            expr_attr_values=None,
            filter_expr=None,
            startkey=startkey,
        )

        # 失敗時、またはデータがない場合
        if not res.is_success or res.data is None:
            return ServiceResponse(
                code=res.code,
                data=ListItemData(),  # 初期値(items=[])が入る
                detail=res.detail,
            )

        # res.data は ListItemData インスタンスなのでドットでアクセス
        items = res.data.items
        last_evaluated_key = res.data.last_evaluated_key

        logger.info(f"Retrieved items count: {len(items)}")

        return ServiceResponse(
            code=res.code,
            data=ListItemData(
                items=items,
                last_evaluated_key=last_evaluated_key,
                size=res.data.size,
                count=res.data.count,
            ),
            detail=res.detail,
        )

    def create_user(self, user: dict[str, Any]) -> ServiceResponse[MessageData]:
        res = self.users_repo.create_user(user)
        return ServiceResponse(code=res.code, data=None, detail=res.detail)

    def update_user(self, userid: str, user_data: dict[str, Any]) -> ServiceResponse[MessageData]:
        res = self.users_repo.update_user(userid, user_data)
        return ServiceResponse(code=res.code, data=None, detail=res.detail)

    def update_user_partial(self, userid: str, update_data: dict[str, Any]) -> ServiceResponse[MessageData]:
        res = self.users_repo.update_user_partial(userid, update_data)
        return ServiceResponse(code=res.code, data=None, detail=res.detail)

    def delete_user(self, userid: str) -> ServiceResponse[MessageData]:
        res = self.users_repo.delete_user(userid)
        return ServiceResponse(code=res.code, data=None, detail=res.detail)
