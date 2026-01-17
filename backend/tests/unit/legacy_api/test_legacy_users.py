import logging
from unittest.mock import patch

from app.legacy_api import users

logger = logging.getLogger(__name__)


def test_get_users_calls_list_users_and_returns_data():
    """GET /legacy/users の正常系テスト：ユーザー一覧が返ること"""
    event = {
        "path": "/legacy/users",
        "httpMethod": "GET",
        "queryStringParameters": {
            "limit": "2",
            "startkey": None,
        },
        "body": None,
        "headers": {},
    }

    expected_users = [
        {"userid": "user1", "username": "Alice"},
        {"userid": "user2", "username": "Bob"},
    ]

    with patch.object(users, "users_service") as mock_service:
        mock_service.list_users.return_value = expected_users

        response = users.lambda_handler(event, None)

        assert response["statusCode"] == 200
        assert "user1" in response["body"]
        assert "user2" in response["body"]


def test_post_users_calls_create_user_and_returns_created_user():
    """POST /legacy/users の正常系テスト：ユーザー作成が行われること"""
    event = {
        "path": "/legacy/users",
        "httpMethod": "POST",
        "queryStringParameters": None,
        "body": '{"userid": "user3@example.com", "username": "Charlie"}',
        "headers": {"Content-Type": "application/json"},
    }

    expected_user = {"userid": "user3@example.com", "username": "Charlie"}

    with patch.object(users, "users_service") as mock_service:
        mock_service.create_user.return_value = expected_user

        response = users.lambda_handler(event, None)

        assert response["statusCode"] == 200
        assert "user3" in response["body"]
        assert "Charlie" in response["body"]


def test_put_users_calls_update_user_and_returns_updated_user():
    """PUT /legacy/users/{userid} の正常系テスト：ユーザー情報が更新されること"""
    event = {
        "path": "/legacy/users/user1",
        "httpMethod": "PUT",
        "queryStringParameters": None,
        "body": '{"username": "AliceUpdated"}',
        "headers": {"Content-Type": "application/json"},
    }

    updated_user = {"userid": "user1", "username": "AliceUpdated"}

    with patch.object(users, "users_service") as mock_service:
        mock_service.update_user.return_value = updated_user

        response = users.lambda_handler(event, None)

        assert response["statusCode"] == 200
        assert "AliceUpdated" in response["body"]


def test_delete_users_calls_delete_user_and_returns_success_message():
    """DELETE /legacy/users の正常系テスト：ユーザー削除が行われること"""
    event = {
        "path": "/legacy/users/user1",
        "httpMethod": "DELETE",
        "queryStringParameters": {"userid": "user1"},
        "body": None,
        "headers": {},
    }

    with patch.object(users, "users_service") as mock_service:
        mock_service.delete_user.return_value = {"message": "User deleted"}

        response = users.lambda_handler(event, None)

        assert response["statusCode"] == 200
        assert "User deleted" in response["body"]
