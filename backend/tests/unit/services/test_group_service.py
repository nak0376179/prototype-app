# tests/unit/services/test_group_service.py
"""
GroupService のテスト

LocalStack (デフォルト) または AWS DynamoDB を使用してテストを実行します。
"""

from typing import Any

from app.services.group_service import GroupService


class TestGetGroupById:
    """get_group_by_id メソッドのテスト"""

    def test_returns_group_when_exists(
        self,
        group_service: GroupService,
        create_test_group: Any,
        sample_group: dict[str, Any],
    ) -> None:
        """存在するグループを取得できる"""
        create_test_group(sample_group)

        result = group_service.get_group_by_id(sample_group["groupid"])

        assert result.is_success
        assert result.data is not None
        assert result.data.item["groupid"] == sample_group["groupid"]
        assert result.data.item["groupname"] == sample_group["groupname"]

    def test_returns_none_when_not_exists(
        self,
        group_service: GroupService,
    ) -> None:
        """存在しないグループの場合は item が None"""
        result = group_service.get_group_by_id("nonexistent-group")

        assert result.is_success
        assert result.data is not None
        assert result.data.item is None


class TestGetGroupMembers:
    """get_group_members メソッドのテスト"""

    def test_returns_group_with_users(
        self,
        group_service: GroupService,
        create_test_group: Any,
        sample_group: dict[str, Any],
    ) -> None:
        """グループ情報（ユーザーリスト含む）を取得できる"""
        create_test_group(sample_group)

        result = group_service.get_group_members(sample_group["groupid"])

        assert result.is_success
        assert result.data is not None
        assert result.data.item["groupid"] == sample_group["groupid"]
        assert "users" in result.data.item

    def test_returns_none_when_group_not_exists(
        self,
        group_service: GroupService,
    ) -> None:
        """存在しないグループの場合は item が None"""
        result = group_service.get_group_members("nonexistent-group")

        assert result.is_success
        assert result.data is not None
        assert result.data.item is None

    def test_returns_empty_users_when_no_members(
        self,
        group_service: GroupService,
        create_test_group: Any,
    ) -> None:
        """メンバーがいないグループの場合は空のユーザーリスト"""
        empty_group = {
            "groupid": "empty-group",
            "groupname": "Empty Group",
            "users": [],
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }
        create_test_group(empty_group)

        result = group_service.get_group_members("empty-group")

        assert result.is_success
        assert result.data is not None
        assert result.data.item["users"] == []


class TestMultipleGroups:
    """複数グループのテスト"""

    def test_get_different_groups(
        self,
        group_service: GroupService,
        create_test_groups: Any,
        sample_groups: list[dict[str, Any]],
    ) -> None:
        """異なるグループを個別に取得できる"""
        create_test_groups(sample_groups)

        for group in sample_groups:
            result = group_service.get_group_by_id(group["groupid"])
            assert result.is_success
            assert result.data is not None
            assert result.data.item["groupid"] == group["groupid"]
