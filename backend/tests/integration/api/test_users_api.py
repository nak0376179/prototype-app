import base64
import json

from app.api.users import get_auth_context
from app.main import app  # FastAPI アプリのエントリーポイント
from fastapi import HTTPException, Request
from fastapi.testclient import TestClient

client = TestClient(app)


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


def make_dummy_jwt(userid: str = "user1@example.com"):
    header = base64.urlsafe_b64encode(b'{"alg":"none","typ":"JWT"}').decode().rstrip("=")
    payload = base64.urlsafe_b64encode(json.dumps({"cognito:username": userid}).encode()).decode().rstrip("=")
    return f"Bearer {header}.{payload}."


client = TestClient(app)


def test_list_users():
    response = client.get("/users", headers={"Authorization": make_dummy_jwt("test-admin@example.com")})
    assert response.status_code == 200


def test_get_user_by_id():
    """
    GET /users/{user_id} に対して、正しい1件の情報が返ることを確認する
    """
    user_id = "test-admin@example.com"

    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["userid"] == user_id


def test_get_user_not_found():
    """
    存在しないユーザーIDに対して 404 を返すことを確認する
    """
    response = client.get("/users/doesnotexist@example.com")
    assert response.status_code == 404
