import base64
import json
import logging

import boto3
import pytest
from app.api.logs import get_auth_context
from app.main import app
from fastapi import HTTPException, Request
from fastapi.testclient import TestClient

logger = logging.getLogger(__name__)


DYNAMODB_ENDPOINT = "http://localhost:4566"
TABLE_NAME = "prototype-app-logs-devel"


class MockAuthContext:
    def __init__(self, userid: str, group_roles: list):
        self.userid = userid
        self.group_roles = group_roles

    def is_member_of(self, _groupid: str) -> bool:
        # ここでグループメンバーの確認を行う
        return True

    def get_role_in(self, _groupid: str) -> str | None:
        # 役割情報を返す
        return ["view_logs", "list_logs"]


def get_auth_context_from_header(request: Request) -> MockAuthContext:
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=403, detail="Authorization header missing")

    # Authorization: Bearer <token>
    token = auth_header.split(" ")[1] if len(auth_header.split()) > 1 else None
    if not token:
        raise HTTPException(status_code=403, detail="Token missing in Authorization header")

    # JWTのペイロード部分をデコード
    try:
        payload = token.split(".")[1]
        decoded_payload = base64.urlsafe_b64decode(payload + "==")  # パディングを補正
        user_info = json.loads(decoded_payload)
        # ユーザーIDを取得
        userid = user_info.get("cognito:username", None)
        if not userid:
            raise HTTPException(status_code=403, detail="Invalid token")

        # ここでユーザーの権限等も返せる
        return MockAuthContext(userid=userid, group_roles=["view_logs"])

    except Exception:
        raise HTTPException(status_code=403, detail="Invalid token")


# FastAPIの依存関係を更新
app.dependency_overrides[get_auth_context] = get_auth_context_from_header
client = TestClient(app)


@pytest.fixture(scope="module")
def dynamodb_resource():
    """DynamoDBのboto3リソース（LocalStack経由）を返す"""
    return boto3.resource("dynamodb", endpoint_url=DYNAMODB_ENDPOINT, region_name="ap-northeast-1")


@pytest.fixture(scope="module")
def logs_table(dynamodb_resource):
    """テスト用のDynamoDBテーブル（logs）を返す"""
    table = dynamodb_resource.Table(TABLE_NAME)
    yield table


def make_dummy_jwt(userid: str = "user1@example.com"):
    header = base64.urlsafe_b64encode(b'{"alg":"none","typ":"JWT"}').decode().rstrip("=")
    payload = base64.urlsafe_b64encode(json.dumps({"cognito:username": userid}).encode()).decode().rstrip("=")
    token = f"{header}.{payload}."  # 署名なしでOK（ダミー）
    return f"Bearer {token}"


def test_log_with_user_and_group(make_sample_logs, make_sample_groups):
    groups = make_sample_groups()
    groupid = groups[0]["groupid"]
    make_sample_logs(count=6)

    response = client.get("/groups/test-group1/logs", headers={"Authorization": make_dummy_jwt("test-admin@example.com")})
    assert response.status_code == 200
    body = response.json()
    assert "Items" in body
    assert len(body["Items"]) == 25
    assert body["Items"][0]["groupid"] == groupid


def test_list_logs_with_filter_userid():
    """
    useridフィルター付きでも取得できる
    """

    response = client.get(
        "/groups/test-group1/logs",
        params={"userid": "test-admin@example.com"},
        headers={"Authorization": make_dummy_jwt("test-admin@example.com")},
    )

    assert response.status_code == 200
    items = response.json()["Items"]
    for item in items:
        assert item["userid"] == "test-admin@example.com"


def test_list_logs_with_filter_type():
    """
    typeフィルター付きでも取得できる
    """

    response = client.get(
        "/groups/test-group1/logs",
        params={"type": "Login"},
        headers={"Authorization": make_dummy_jwt("test-admin@example.com")},
    )

    assert response.status_code == 200
    items = response.json()["Items"]
    for item in items:
        assert item["type"] == "Login"


def test_list_logs_invalid_startkey(make_sample_logs, make_sample_groups):
    """
    startkeyが不正な形式（JSONでない）場合、400を返す
    """
    groups = make_sample_groups()
    groupid = groups[0]["groupid"]
    make_sample_logs(count=6)

    response = client.get(
        f"/groups/{groupid}/logs",
        params={"startkey": "not-a-json"},
        headers={"Authorization": make_dummy_jwt("test-admin@example.com")},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid startkey format"
