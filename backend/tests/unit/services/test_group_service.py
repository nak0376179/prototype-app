from typing import Any


def test_get_group_by_id(group_service: Any) -> None:
    """
    get_group_by_id は、指定された groupid に対応するグループ情報を返す。
    """
    group = group_service.get_group_by_id("test-group1")
    assert group["groupid"] == "test-group1"
    assert group["groupname"] == "テストグループ1"


def test_get_group_members(group_service: Any) -> None:
    """
    get_group_members は、指定された groupid に属するユーザー情報を返す。
    users_repo から取得したユーザー名が含まれることを検証する。
    """
    result = group_service.get_group_members("test-group1")
    assert result["Items"][0]["userid"] == "test-user1@example.com"
    assert result["Items"][0]["username"] == "test-user1"


def test_get_group_members_returns_empty_items_when_group_not_found(group_service: Any) -> None:
    """
    存在しない groupid を指定した場合、get_group_members は None を返す。
    """
    result = group_service.get_group_members("unknown-group")
    assert result is None


def test_get_group_members_with_multiple_users(group_service: Any) -> None:
    """
    グループに複数のユーザーが存在する場合、全員が取得されることを検証する。
    """

    result = group_service.get_group_members("test-group1")
    members = result["Items"]
    assert len(members) == 2
    assert {"userid": "test-user1@example.com", "username": "test-user1"} in members
    assert {"userid": "test-user2@example.com", "username": "test-user2"} in members


def test_get_group_members_handles_empty_user_list(group_service: Any) -> None:
    """
    グループにユーザーが1人も登録されていない場合、空の Items を返す。
    """

    result = group_service.get_group_members("test-group2")
    assert result["Items"] == []
