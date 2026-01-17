import logging
from unittest.mock import patch

from app.legacy_api import users

logger = logging.getLogger(__name__)


def test_get_users_calls_list_users_and_returns_data():
    # Lambda に渡すイベント（API Gateway のリクエストを模倣）
    event = {
        "path": "/legacy/users",
        "httpMethod": "GET",
        "queryStringParameters": {"limit": "2", "startkey": None},
        "body": None,
        "headers": {},
    }

    # モックとして返されるユーザーデータ
    expected_users = [{"userid": "user1", "username": "Alice"}, {"userid": "user2", "username": "Bob"}]

    # users_service をモック化して、list_users の戻り値を固定
    with patch.object(users, "users_service") as mock_service:
        mock_service.list_users.return_value = expected_users

        # Lambda ハンドラーを実行（通常 AWS Lambda 上で呼び出される関数）
        response = users.lambda_handler(event, None)

        # レスポンス形式は {"statusCode": ..., "body": "..."} を想定して検証
        assert response["statusCode"] == 200

        # ボディ部は JSON 文字列として返ってくるので、文字列内に期待値が含まれることを確認
        assert "user1" in response["body"]
        assert "user2" in response["body"]
