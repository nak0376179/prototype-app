import logging
from typing import Any

from app.models.common import ListItemData, MessageData, RepositoryResponse, SingleItemData
from app.repositories.dynamodb import (
    batch_get_items,
    delete_item,
    get_item,
    put_item,
    scan_items,
    update_item,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class UsersTable:
    def __init__(self, table_name: str = "users") -> None:
        self.table_name = table_name

    def get_user_by_id(self, userid: str) -> RepositoryResponse[SingleItemData]:
        logger.info(f"Fetching user by ID: {userid}")
        return get_item(self.table_name, {"userid": userid})

    def batch_get_users_by_ids(self, userids: list[str]) -> RepositoryResponse[ListItemData]:
        logger.info(f"Batch fetching users by IDs: {len(userids)}")
        keys = [{"userid": userid} for userid in userids]
        return batch_get_items(self.table_name, keys)

    def list_users(
        self,
        limit: int = 25,
        startkey: dict[str, Any] | None = None,
        expr_attr_names: dict[str, Any] | None = None,
        expr_attr_values: dict[str, Any] | None = None,
        filter_expr: Any = None,
    ) -> RepositoryResponse[ListItemData]:
        if limit < 1 or limit > 1000:
            raise ValueError("limit must be between 1 and 1000")
        logger.info(f"Listing users with limit={limit} startkey={startkey}")

        return scan_items(
            table_name=self.table_name,
            limit=limit,
            expr_attr_names=expr_attr_names,
            expr_attr_values=expr_attr_values,
            filter_expr=filter_expr,
            exclusive_start_key=startkey,
        )

    def create_user(self, user: dict[str, Any]) -> RepositoryResponse[MessageData]:
        logger.info(f"Creating user: {user.get('userid')}")
        res = put_item(self.table_name, item=user)
        return res

    def update_user(self, userid: str, user_data: dict[str, Any]) -> RepositoryResponse[MessageData]:
        logger.info(f"Updating user fully: {userid}")
        updated_user = {"userid": userid, **user_data}
        res = put_item(self.table_name, item=updated_user)
        return res

    def update_user_partial(self, userid: str, update_data: dict[str, Any]) -> RepositoryResponse[MessageData]:
        logger.info(f"Partially updating user: {userid} with data: {update_data}")
        update_expr = []
        expr_attrs = {}
        expr_names = {}

        if "username" in update_data:
            update_expr.append("#username = :username")
            expr_attrs[":username"] = update_data["username"]
            expr_names["#username"] = "username"
        if "email" in update_data:
            update_expr.append("#email = :email")
            expr_attrs[":email"] = update_data["email"]
            expr_names["#email"] = "email"  # 予約語回避のため明示

        if not update_expr:
            raise ValueError("No fields provided for update")

        res = update_item(
            table_name=self.table_name,
            key={"userid": userid},
            update_expr="SET " + ", ".join(update_expr),
            expr_attr_values=expr_attrs,
            expr_attr_names=expr_names if expr_names else None,
        )
        return res

    def delete_user(self, userid: str) -> RepositoryResponse[MessageData]:
        res = delete_item(self.table_name, key={"userid": userid})
        logger.info(f"Deleting user: {userid}")
        return res
