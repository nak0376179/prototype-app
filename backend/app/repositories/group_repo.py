# api/repositories/groups.py
from app.models.common import RepositoryResponse, SingleItemData
from app.repositories.dynamodb import get_item, get_table


class GroupsTable:
    def __init__(self) -> None:
        self.table_name = "groups"
        self.table = get_table(self.table_name)

    def get_group_by_id(self, groupid: str) -> RepositoryResponse[SingleItemData]:
        """指定した groupid のグループ情報を取得します。"""
        return get_item(self.table_name, key={"groupid": groupid})
