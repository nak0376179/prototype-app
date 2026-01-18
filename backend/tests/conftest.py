# tests/conftest.py
"""
テスト共通設定

デフォルトでは LocalStack を使用してテストを実行します。
AWS DynamoDB を使用する場合は環境変数を設定してください:

    TEST_USE_LOCALSTACK=false pytest

環境変数:
    TEST_USE_LOCALSTACK: true (デフォルト) → LocalStack, false → AWS DynamoDB
    LOCALSTACK_ENDPOINT: LocalStack エンドポイント (デフォルト: http://localhost:4566)
    AWS_DEFAULT_REGION: AWS リージョン (デフォルト: ap-northeast-1)
    ENVIRONMENT: 環境名 (テスト時は自動的に "test" に設定)
"""

import os
from collections.abc import Generator
from typing import Any

import boto3
import pytest
from fastapi.testclient import TestClient

# テスト実行前に環境変数を設定
os.environ.setdefault("ENVIRONMENT", "test")

from app.config import settings
from app.main import app


@pytest.fixture(scope="session")
def test_settings() -> Any:
    """テスト用設定を返す"""
    return settings


@pytest.fixture(scope="session")
def dynamodb_resource() -> Any:
    """
    DynamoDB リソースを返す。
    LocalStack または AWS DynamoDB のどちらかを使用。
    """
    endpoint_url = settings.dynamodb_endpoint_url
    if endpoint_url:
        # LocalStack を使用
        return boto3.resource(
            "dynamodb",
            endpoint_url=endpoint_url,
            region_name=settings.REGION_NAME,
            aws_access_key_id="test",
            aws_secret_access_key="test",
        )
    else:
        # AWS DynamoDB を使用
        return boto3.resource(
            "dynamodb",
            region_name=settings.REGION_NAME,
        )


@pytest.fixture(scope="session")
def dynamodb_client() -> Any:
    """DynamoDB クライアントを返す"""
    endpoint_url = settings.dynamodb_endpoint_url
    if endpoint_url:
        return boto3.client(
            "dynamodb",
            endpoint_url=endpoint_url,
            region_name=settings.REGION_NAME,
            aws_access_key_id="test",
            aws_secret_access_key="test",
        )
    else:
        return boto3.client(
            "dynamodb",
            region_name=settings.REGION_NAME,
        )


@pytest.fixture(scope="session")
def test_table_suffix() -> str:
    """テスト用テーブル名のサフィックス (local/test 環境では devel を使用)"""
    return "devel"


@pytest.fixture(scope="session")
def users_table_name(test_table_suffix: str) -> str:
    """Users テーブル名"""
    return f"{settings.APP_NAME}-users-{test_table_suffix}"


@pytest.fixture(scope="session")
def groups_table_name(test_table_suffix: str) -> str:
    """Groups テーブル名"""
    return f"{settings.APP_NAME}-groups-{test_table_suffix}"


@pytest.fixture(scope="session")
def logs_table_name(test_table_suffix: str) -> str:
    """Logs テーブル名"""
    return f"{settings.APP_NAME}-logs-{test_table_suffix}"


@pytest.fixture(scope="session")
def ensure_tables_exist(
    dynamodb_client: Any,
    users_table_name: str,
    groups_table_name: str,
    logs_table_name: str,
) -> Generator[None]:
    """テスト用テーブルが存在することを確認"""
    tables = [users_table_name, groups_table_name, logs_table_name]
    existing_tables = dynamodb_client.list_tables().get("TableNames", [])

    for table_name in tables:
        if table_name not in existing_tables:
            pytest.skip(f"Table {table_name} does not exist. Run LocalStack setup first.")

    yield


@pytest.fixture
def client() -> TestClient:
    """FastAPI テストクライアント"""
    return TestClient(app)


# =============================================================================
# テストデータ用フィクスチャ
# =============================================================================


@pytest.fixture
def sample_user() -> dict[str, Any]:
    """サンプルユーザーデータ"""
    return {
        "userid": "test-user@example.com",
        "username": "Test User",
        "email": "test-user@example.com",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def sample_users() -> list[dict[str, Any]]:
    """複数のサンプルユーザーデータ"""
    return [
        {
            "userid": f"test-user-{i}@example.com",
            "username": f"Test User {i}",
            "email": f"test-user-{i}@example.com",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }
        for i in range(1, 6)
    ]


@pytest.fixture
def sample_group() -> dict[str, Any]:
    """サンプルグループデータ"""
    return {
        "groupid": "test-group-1",
        "groupname": "Test Group 1",
        "description": "A test group",
        "users": ["test-user-1@example.com", "test-user-2@example.com"],
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def sample_groups() -> list[dict[str, Any]]:
    """複数のサンプルグループデータ"""
    return [
        {
            "groupid": f"test-group-{i}",
            "groupname": f"Test Group {i}",
            "description": f"Test group number {i}",
            "users": [],
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }
        for i in range(1, 4)
    ]


@pytest.fixture
def sample_logs() -> list[dict[str, Any]]:
    """サンプルログデータ"""
    return [
        {
            "groupid": "test-group-1",
            "created_at": f"2024-01-01T00:00:{i:02d}Z",
            "userid": f"test-user-{i % 3 + 1}@example.com",
            "username": f"Test User {i % 3 + 1}",
            "type": "Login" if i % 2 == 0 else "Logout",
            "message": f"Test message {i}",
        }
        for i in range(10)
    ]
