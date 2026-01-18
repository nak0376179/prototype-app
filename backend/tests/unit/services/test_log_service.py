# tests/unit/services/test_log_service.py
"""
LogsService のテスト

LocalStack (デフォルト) または AWS DynamoDB を使用してテストを実行します。
"""

from typing import Any

import pytest
from app.repositories.log_repo import LogsTable
from app.services.log_service import LogsService


@pytest.fixture
def logs_repo() -> LogsTable:
    """LogsTable リポジトリ"""
    return LogsTable()


@pytest.fixture
def logs_service(logs_repo: LogsTable) -> LogsService:
    """LogsService インスタンス"""
    return LogsService(logs_repo=logs_repo)


class TestListLogs:
    """list_logs メソッドのテスト"""

    def test_returns_logs_for_group(
        self,
        logs_service: LogsService,
        create_test_logs: Any,
        sample_logs: list[dict[str, Any]],
    ) -> None:
        """グループのログを取得できる"""
        create_test_logs(sample_logs)

        result = logs_service.list_logs(groupid="test-group-1")

        assert result.is_success
        assert result.data is not None
        assert len(result.data.items) > 0
        for log in result.data.items:
            assert log["groupid"] == "test-group-1"

    def test_returns_empty_for_nonexistent_group(
        self,
        logs_service: LogsService,
    ) -> None:
        """存在しないグループの場合は空のリスト"""
        result = logs_service.list_logs(groupid="nonexistent-group")

        assert result.is_success
        assert result.data is not None
        assert len(result.data.items) == 0

    def test_respects_limit(
        self,
        logs_service: LogsService,
        create_test_logs: Any,
        sample_logs: list[dict[str, Any]],
    ) -> None:
        """limit を指定した場合、指定件数以下のログを返す"""
        create_test_logs(sample_logs)

        result = logs_service.list_logs(groupid="test-group-1", limit=3)

        assert result.is_success
        assert result.data is not None
        assert len(result.data.items) <= 3

    def test_filters_by_date_range(
        self,
        logs_service: LogsService,
        create_test_logs: Any,
        sample_logs: list[dict[str, Any]],
    ) -> None:
        """日付範囲でフィルタできる"""
        create_test_logs(sample_logs)

        result = logs_service.list_logs(
            groupid="test-group-1",
            begin="2024-01-01T00:00:03Z",
            end="2024-01-01T00:00:07Z",
        )

        assert result.is_success
        assert result.data is not None
        for log in result.data.items:
            assert log["created_at"] >= "2024-01-01T00:00:03Z"
            assert log["created_at"] <= "2024-01-01T00:00:07Z"


class TestListLogsWithFilters:
    """フィルタ付きの list_logs メソッドのテスト"""

    def test_filters_by_userid(
        self,
        logs_service: LogsService,
        create_test_logs: Any,
    ) -> None:
        """userid でフィルタできる"""
        logs = [
            {
                "groupid": "filter-test-group",
                "created_at": f"2024-01-01T00:00:0{i}Z",
                "groupid#userid": f"filter-test-group#user-{i % 2}@example.com",
                "userid": f"user-{i % 2}@example.com",
                "username": f"User {i % 2}",
                "type": "Login",
                "message": f"Message {i}",
            }
            for i in range(6)
        ]
        create_test_logs(logs)

        result = logs_service.list_logs(
            groupid="filter-test-group",
            userid="user-0@example.com",
        )

        assert result.is_success
        assert result.data is not None
        for log in result.data.items:
            assert log["userid"] == "user-0@example.com"

    def test_filters_by_type(
        self,
        logs_service: LogsService,
        create_test_logs: Any,
    ) -> None:
        """type でフィルタできる"""
        logs = [
            {
                "groupid": "type-test-group",
                "created_at": f"2024-01-01T00:00:0{i}Z",
                "groupid#type": f"type-test-group#{'Login' if i % 2 == 0 else 'Logout'}",
                "userid": "user@example.com",
                "username": "User",
                "type": "Login" if i % 2 == 0 else "Logout",
                "message": f"Message {i}",
            }
            for i in range(6)
        ]
        create_test_logs(logs)

        result = logs_service.list_logs(
            groupid="type-test-group",
            type_="Login",
        )

        assert result.is_success
        assert result.data is not None
        for log in result.data.items:
            assert log["type"] == "Login"
