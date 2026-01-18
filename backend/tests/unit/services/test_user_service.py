# tests/unit/services/test_user_service.py
"""
UsersService のテスト

LocalStack (デフォルト) または AWS DynamoDB を使用してテストを実行します。
"""

from typing import Any

import pytest
from app.services.user_service import UsersService


class TestGetUserById:
    """get_user_by_id メソッドのテスト"""

    def test_returns_user_when_exists(
        self,
        users_service: UsersService,
        create_test_user: Any,
        sample_user: dict[str, Any],
    ) -> None:
        """存在するユーザーを取得できる"""
        create_test_user(sample_user)

        result = users_service.get_user_by_id(sample_user["userid"])

        assert result.is_success
        assert result.data is not None
        assert result.data.item["userid"] == sample_user["userid"]
        assert result.data.item["username"] == sample_user["username"]

    def test_returns_none_when_not_exists(self, users_service: UsersService) -> None:
        """存在しないユーザーの場合は item が None"""
        result = users_service.get_user_by_id("nonexistent@example.com")

        assert result.is_success
        assert result.data is not None
        assert result.data.item is None


class TestListUsers:
    """list_users メソッドのテスト"""

    def test_returns_empty_list_when_no_users(
        self,
        users_service: UsersService,
    ) -> None:
        """ユーザーがいない場合は空のリストを返す"""
        result = users_service.list_users(limit=10)

        assert result.is_success
        assert result.data is not None
        assert isinstance(result.data.items, list)

    def test_returns_users_with_limit(
        self,
        users_service: UsersService,
        create_test_users: Any,
        sample_users: list[dict[str, Any]],
    ) -> None:
        """limit を指定した場合、指定件数以下のユーザーを返す"""
        create_test_users(sample_users)

        result = users_service.list_users(limit=3)

        assert result.is_success
        assert result.data is not None
        assert len(result.data.items) <= 3


class TestCreateUser:
    """create_user メソッドのテスト"""

    def test_creates_user_successfully(
        self,
        users_service: UsersService,
        cleanup_test_user: Any,
    ) -> None:
        """ユーザーを作成できる"""
        new_user = {
            "userid": "new-user@example.com",
            "username": "New User",
            "email": "new-user@example.com",
        }

        result = users_service.create_user(new_user)

        assert result.is_success

        # 作成されたユーザーを確認
        get_result = users_service.get_user_by_id(new_user["userid"])
        assert get_result.data is not None
        assert get_result.data.item["userid"] == new_user["userid"]

        # クリーンアップ
        cleanup_test_user(new_user["userid"])


class TestUpdateUser:
    """update_user メソッドのテスト"""

    def test_updates_user_successfully(
        self,
        users_service: UsersService,
        create_test_user: Any,
        sample_user: dict[str, Any],
    ) -> None:
        """ユーザーを更新できる"""
        create_test_user(sample_user)

        updated_data = {
            "username": "Updated User",
            "email": sample_user["email"],
        }
        result = users_service.update_user(sample_user["userid"], updated_data)

        assert result.is_success

        # 更新されたユーザーを確認
        get_result = users_service.get_user_by_id(sample_user["userid"])
        assert get_result.data is not None
        assert get_result.data.item["username"] == "Updated User"


class TestUpdateUserPartial:
    """update_user_partial メソッドのテスト"""

    def test_updates_username_only(
        self,
        users_service: UsersService,
        create_test_user: Any,
        sample_user: dict[str, Any],
    ) -> None:
        """username のみを更新できる"""
        create_test_user(sample_user)

        result = users_service.update_user_partial(
            sample_user["userid"],
            {"username": "Partially Updated"},
        )

        assert result.is_success

        # 更新されたユーザーを確認
        get_result = users_service.get_user_by_id(sample_user["userid"])
        assert get_result.data is not None
        assert get_result.data.item["username"] == "Partially Updated"

    def test_raises_error_when_no_fields(
        self,
        users_service: UsersService,
        create_test_user: Any,
        sample_user: dict[str, Any],
    ) -> None:
        """更新フィールドが空の場合はエラー"""
        create_test_user(sample_user)

        with pytest.raises(ValueError, match="No fields provided"):
            users_service.update_user_partial(sample_user["userid"], {})


class TestDeleteUser:
    """delete_user メソッドのテスト"""

    def test_deletes_user_successfully(
        self,
        users_service: UsersService,
        create_test_user: Any,
        sample_user: dict[str, Any],
    ) -> None:
        """ユーザーを削除できる"""
        create_test_user(sample_user)

        result = users_service.delete_user(sample_user["userid"])

        assert result.is_success

        # 削除されたことを確認
        get_result = users_service.get_user_by_id(sample_user["userid"])
        assert get_result.data is not None
        assert get_result.data.item is None

    def test_delete_nonexistent_user_succeeds(
        self,
        users_service: UsersService,
    ) -> None:
        """存在しないユーザーの削除も成功する (DynamoDB の仕様)"""
        result = users_service.delete_user("nonexistent@example.com")

        assert result.is_success


class TestBatchGetUsersByIds:
    """batch_get_users_by_ids メソッドのテスト"""

    def test_returns_multiple_users(
        self,
        users_service: UsersService,
        create_test_users: Any,
        sample_users: list[dict[str, Any]],
    ) -> None:
        """複数のユーザーを一括取得できる"""
        create_test_users(sample_users)

        user_ids = [user["userid"] for user in sample_users[:3]]
        result = users_service.batch_get_users_by_ids(user_ids)

        assert result.is_success
        assert result.data is not None
        assert len(result.data.items) == 3

    def test_returns_empty_list_for_nonexistent_users(
        self,
        users_service: UsersService,
    ) -> None:
        """存在しないユーザーの場合は空のリスト"""
        result = users_service.batch_get_users_by_ids(["nonexistent1@example.com", "nonexistent2@example.com"])

        assert result.is_success
        assert result.data is not None
        assert len(result.data.items) == 0
