from typing import Any
from unittest.mock import MagicMock

import pytest
from app.services.group_service import GroupService
from app.services.log_service import LogsService

# === Pytest用フィクスチャとテスト補助クラス ===
# このファイルはユニットテストで共通して利用されるフィクスチャやモック、ダミーデータを定義します。
# GroupService や LogsService のテストにおいて依存するリポジトリ層をモック化し、純粋なサービスの振る舞いのみを検証可能にします。


# === フィクスチャ定義 ===


@pytest.fixture
def mock_group_repo() -> Any:
    """
    GroupService に注入するためのモックグループリポジトリ。
    `FakeGroupsRepo` を使って、特定のグループIDに対して静的なレスポンスを返す。
    """
    return FakeGroupsRepo()


@pytest.fixture
def mock_user_repo() -> Any:
    """
    GroupService に注入するためのモックユーザーリポジトリ。
    `FakeUsersRepo` により、与えられたユーザーIDに対応するダミーユーザー情報を返す。
    """
    return FakeUsersRepo()


@pytest.fixture
def mock_logs_repo(sample_logs: Any) -> Any:
    """
    LogsService に注入するためのモックログリポジトリ。
    list_logs メソッドのみを提供し、group-A のログを固定で返す。
    """
    repo = MagicMock()
    repo.list_logs.return_value = {"Items": sample_logs["group-A"]}
    return repo


@pytest.fixture
def group_service(mock_group_repo: Any, mock_user_repo: Any) -> Any:
    """
    GroupService のインスタンスを、モックリポジトリを注入した状態で生成する。
    このフィクスチャにより、サービスのユニットテストで外部依存を排除できる。
    """
    service = GroupService()
    service.groups_repo = mock_group_repo
    service.users_repo = mock_user_repo
    return service


@pytest.fixture
def logs_service(mock_logs_repo: Any) -> Any:
    """
    LogsService のインスタンスを、モックリポジトリ付きで提供する。
    """
    return LogsService(logs_repo=mock_logs_repo)


# === フェイクリポジトリ定義 ===


class FakeGroupsRepo:
    """
    グループIDに応じた固定レスポンスを返す、簡易なフェイクリポジトリ。
    GroupService のテスト用。
    """

    def get_group_by_id(self, groupid: str) -> Any:
        if groupid == "test-group1":
            return {
                "groupid": "test-group1",
                "groupname": "テストグループ1",
                "users": ["test-user1@example.com", "test-user2@example.com"],
            }
        elif groupid == "test-group2":
            return {
                "groupid": "test-group2",
                "groupname": "テストグループ2",
                "users": [],
            }
        else:
            return None


class FakeUsersRepo:
    """
    ユーザーID（メールアドレス）から、ユーザー情報のリストを生成するフェイクリポジトリ。
    与えられたIDのローカル部分を username として返す。
    """

    def batch_get_users_by_ids(self, userids: list[str]) -> list[dict[str, Any]]:
        return [{"userid": user, "username": user.split("@")[0]} for user in userids]


# === LogsService用のダミーデータ生成 ===


@pytest.fixture
def sample_logs() -> Any:
    """
    LogsService のテスト用に使用されるダミーログデータを生成。
    2つの異なるグループ（group-A, group-B）に対してそれぞれ100件ずつのログを含む。
    各ログは created_at, userid, username, type, message を含み、type は "Login" / "Logout" を交互に切り替える。

    Returns:
        dict: {
            "group-A": [...logs...],
            "group-B": [...logs...],
        }
    """

    def make_group_logs(groupid: str) -> list[dict[str, Any]]:
        return [
            {
                "groupid": groupid,
                "created_at": f"2024-01-01T00:00:0{i}Z",
                "userid": f"user{i}@example.com",
                "username": f"user{i}@example.com",
                "type": "Login" if i % 2 == 0 else "Logout",
                "message": f"message {i}",
            }
            for i in range(100)
        ]

    return {
        "group-A": make_group_logs("group-A"),
        "group-B": make_group_logs("group-B"),
    }
