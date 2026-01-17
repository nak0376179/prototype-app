import base64
import json
import logging

from app.api.groups import get_auth_context
from app.main import app  # FastAPI アプリのエントリーポイント
from fastapi import HTTPException, Request
from fastapi.testclient import TestClient

logger = logging.getLogger(__name__)


# 認証用のモック
class MockAuthContext:
    def __init__(self, userid: str):
        self.userid = userid
        self.group_roles = []

    def is_member_of(self, _groupid: str) -> bool:
        return True

    def get_role_in(self, _groupid: str) -> str | None:
        return "admin"


def get_auth_context_from_header(request: Request) -> MockAuthContext:
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=403, detail="Authorization header missing")
    token = auth_header.split(" ")[1]
    payload = token.split(".")[1]
    decoded_payload = base64.urlsafe_b64decode(payload + "==")
    user_info = json.loads(decoded_payload)
    return MockAuthContext(userid=user_info.get("cognito:username"))


app.dependency_overrides[get_auth_context] = get_auth_context_from_header

client = TestClient(app)


def make_dummy_jwt(userid: str = "user1@example.com"):
    header = base64.urlsafe_b64encode(b'{"alg":"none","typ":"JWT"}').decode().rstrip("=")
    payload = base64.urlsafe_b64encode(json.dumps({"cognito:username": userid}).encode()).decode().rstrip("=")
    return f"Bearer {header}.{payload}."


def test_read_group_success():
    """
    正常系: グループの詳細情報が取得できること
    """
    response = client.get("/groups/test-group1", headers={"Authorization": make_dummy_jwt("test-admin@example.com")})
    assert response.status_code == 200
    assert response.json()["groupid"] == "test-group1"
    assert response.json()["groupname"] == "テストグループ test-group1"


def test_read_group_not_found():
    """
    異常系: 存在しないグループIDを指定した場合に403を返すこと(404ではない)
    """
    response = client.get("/groups/nonexistent", headers={"Authorization": make_dummy_jwt("test-admin@example.com")})
    assert response.status_code == 403


def test_get_group_members_success():
    """
    正常系: グループメンバーの一覧が取得できること
    """
    response = client.get("/groups/test-group1/users", headers={"Authorization": make_dummy_jwt("test-admin@example.com")})
    assert response.status_code == 200
    data = response.json()
    logger.info(data)
    assert "Items" in data
    assert len(data["Items"]) == 4


def test_get_group_members_not_found():
    """
    異常系: 存在しないグループIDに対して404を返すこと
    """
    response = client.get("/groups/missing/users", headers={"Authorization": make_dummy_jwt("test-admin@example.com")})
    assert response.status_code == 403
