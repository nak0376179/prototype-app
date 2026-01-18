# tests/unit/services/conftest.py
"""
Service テスト用フィクスチャ
"""

import pytest
from app.repositories.group_repo import GroupsTable
from app.repositories.user_repo import UsersTable
from app.services.group_service import GroupService
from app.services.user_service import UsersService


@pytest.fixture
def users_repo() -> UsersTable:
    """UsersTable リポジトリ"""
    return UsersTable()


@pytest.fixture
def groups_repo() -> GroupsTable:
    """GroupsTable リポジトリ"""
    return GroupsTable()


@pytest.fixture
def users_service(users_repo: UsersTable) -> UsersService:
    """UsersService インスタンス"""
    return UsersService(users_repo=users_repo)


@pytest.fixture
def group_service(groups_repo: GroupsTable, users_repo: UsersTable) -> GroupService:
    """GroupService インスタンス"""
    return GroupService(groups_repo=groups_repo, users_repo=users_repo)
