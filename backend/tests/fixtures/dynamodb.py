# tests/fixtures/dynamodb.py
"""
DynamoDB テスト用フィクスチャ

テストデータの作成・削除を行うヘルパー関数を提供します。
"""

from typing import Any

import pytest


@pytest.fixture
def create_test_user(dynamodb_resource: Any, users_table_name: str) -> Any:
    """
    テストユーザーを作成するフィクスチャファクトリ。
    テスト終了後に自動的に削除されます。
    """
    created_users: list[str] = []
    table = dynamodb_resource.Table(users_table_name)

    def _create_user(user_data: dict[str, Any]) -> dict[str, Any]:
        table.put_item(Item=user_data)
        created_users.append(user_data["userid"])
        return user_data

    yield _create_user

    # クリーンアップ
    for userid in created_users:
        try:
            table.delete_item(Key={"userid": userid})
        except Exception:
            pass


@pytest.fixture
def create_test_users(dynamodb_resource: Any, users_table_name: str) -> Any:
    """
    複数のテストユーザーを一括作成するフィクスチャファクトリ。
    """
    created_users: list[str] = []
    table = dynamodb_resource.Table(users_table_name)

    def _create_users(users: list[dict[str, Any]]) -> list[dict[str, Any]]:
        for user in users:
            table.put_item(Item=user)
            created_users.append(user["userid"])
        return users

    yield _create_users

    # クリーンアップ
    for userid in created_users:
        try:
            table.delete_item(Key={"userid": userid})
        except Exception:
            pass


@pytest.fixture
def create_test_group(dynamodb_resource: Any, groups_table_name: str) -> Any:
    """
    テストグループを作成するフィクスチャファクトリ。
    """
    created_groups: list[str] = []
    table = dynamodb_resource.Table(groups_table_name)

    def _create_group(group_data: dict[str, Any]) -> dict[str, Any]:
        table.put_item(Item=group_data)
        created_groups.append(group_data["groupid"])
        return group_data

    yield _create_group

    # クリーンアップ
    for groupid in created_groups:
        try:
            table.delete_item(Key={"groupid": groupid})
        except Exception:
            pass


@pytest.fixture
def create_test_groups(dynamodb_resource: Any, groups_table_name: str) -> Any:
    """
    複数のテストグループを一括作成するフィクスチャファクトリ。
    """
    created_groups: list[str] = []
    table = dynamodb_resource.Table(groups_table_name)

    def _create_groups(groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
        for group in groups:
            table.put_item(Item=group)
            created_groups.append(group["groupid"])
        return groups

    yield _create_groups

    # クリーンアップ
    for groupid in created_groups:
        try:
            table.delete_item(Key={"groupid": groupid})
        except Exception:
            pass


@pytest.fixture
def create_test_log(dynamodb_resource: Any, logs_table_name: str) -> Any:
    """
    テストログを作成するフィクスチャファクトリ。
    """
    created_logs: list[tuple[str, str]] = []
    table = dynamodb_resource.Table(logs_table_name)

    def _create_log(log_data: dict[str, Any]) -> dict[str, Any]:
        table.put_item(Item=log_data)
        created_logs.append((log_data["groupid"], log_data["created_at"]))
        return log_data

    yield _create_log

    # クリーンアップ
    for groupid, created_at in created_logs:
        try:
            table.delete_item(Key={"groupid": groupid, "created_at": created_at})
        except Exception:
            pass


@pytest.fixture
def create_test_logs(dynamodb_resource: Any, logs_table_name: str) -> Any:
    """
    複数のテストログを一括作成するフィクスチャファクトリ。
    """
    created_logs: list[tuple[str, str]] = []
    table = dynamodb_resource.Table(logs_table_name)

    def _create_logs(logs: list[dict[str, Any]]) -> list[dict[str, Any]]:
        for log in logs:
            table.put_item(Item=log)
            created_logs.append((log["groupid"], log["created_at"]))
        return logs

    yield _create_logs

    # クリーンアップ
    for groupid, created_at in created_logs:
        try:
            table.delete_item(Key={"groupid": groupid, "created_at": created_at})
        except Exception:
            pass


@pytest.fixture
def cleanup_test_user(dynamodb_resource: Any, users_table_name: str) -> Any:
    """
    指定したユーザーを削除するヘルパー。
    テスト中に作成したユーザーを明示的に削除する場合に使用。
    """
    table = dynamodb_resource.Table(users_table_name)

    def _cleanup(userid: str) -> None:
        try:
            table.delete_item(Key={"userid": userid})
        except Exception:
            pass

    return _cleanup


@pytest.fixture
def cleanup_test_group(dynamodb_resource: Any, groups_table_name: str) -> Any:
    """
    指定したグループを削除するヘルパー。
    """
    table = dynamodb_resource.Table(groups_table_name)

    def _cleanup(groupid: str) -> None:
        try:
            table.delete_item(Key={"groupid": groupid})
        except Exception:
            pass

    return _cleanup
