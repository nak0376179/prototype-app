# 必要な標準ライブラリ・外部ライブラリをインポート
import logging
from datetime import UTC, datetime, timedelta

import boto3
import pytest

# DynamoDB のエンドポイントとリージョン設定（LocalStackを前提とした構成）
DYNAMODB_ENDPOINT = "http://localhost:4566"
REGION = "ap-northeast-1"

# 使用する DynamoDB テーブル名（環境名などの prefix を含む）
TABLE_LOGS = "prototype-app-logs-devel"
TABLE_USERS = "prototype-app-users-devel"
TABLE_GROUPS = "prototype-app-groups-devel"

# ロガーの初期設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# DynamoDB リソース（boto3）を module スコープで共有
@pytest.fixture(scope="module")
def dynamodb_resource():
    return boto3.resource("dynamodb", endpoint_url=DYNAMODB_ENDPOINT, region_name=REGION)


# logs テーブルを返す fixture（module スコープ）
@pytest.fixture(scope="module")
def logs_table(dynamodb_resource):
    return dynamodb_resource.Table(TABLE_LOGS)


# users テーブルを返す fixture（module スコープ）
@pytest.fixture(scope="module")
def users_table(dynamodb_resource):
    return dynamodb_resource.Table(TABLE_USERS)


# groups テーブルを返す fixture（module スコープ）
@pytest.fixture(scope="module")
def groups_table(dynamodb_resource):
    return dynamodb_resource.Table(TABLE_GROUPS)


# サンプルユーザーを DynamoDB に投入する fixture
@pytest.fixture
def make_sample_users(users_table):
    def _make():
        items = []

        # 管理者ユーザー（全グループに所属）
        uid = "test-admin@example.com"
        admin_item = {
            "userid": uid,
            "email": uid,
            "username": uid.split("@")[0],
            "groups": [
                {"groupid": "test-group1", "role": "admin"},
                {"groupid": "test-group2", "role": "admin"},
                {"groupid": "test-group3", "role": "admin"},
            ],
        }
        items.append(admin_item)

        # 10人のユーザーを作成
        for i in range(1, 11):
            uid = f"test-user{i}@example.com"
            user_item = {"userid": uid, "email": uid, "username": f"test-user{i}", "groups": [{"groupid": f"test-group{i % 3 + 1}", "role": "member"}]}
            items.append(user_item)

        # バッチでデータ投入
        with users_table.batch_writer() as batch:
            for item in items:
                batch.put_item(Item=item)

        logger.info(f"[users] Inserted {len(items)} users: {[item['userid'] for item in items]}")
        return items

    return _make


# サンプルグループを DynamoDB に投入する fixture
@pytest.fixture
def make_sample_groups(groups_table):
    def _make(group_ids=None):
        group_ids = group_ids or [f"test-group{i}" for i in range(1, 4)]
        group_members = {
            "test-group1": ["test-admin@example.com", "test-user1@example.com", "test-user4@example.com", "test-user7@example.com", "test-user10@example.com"],
            "test-group2": ["test-admin@example.com", "test-user2@example.com", "test-user5@example.com", "test-user8@example.com"],
            "test-group3": ["test-admin@example.com", "test-user3@example.com", "test-user6@example.com", "test-user9@example.com"],
        }

        items = []
        for group_id in group_ids:
            item = {
                "groupid": group_id,
                "groupname": f"テストグループ {group_id}",
                "permissions": ["list_logs", "view_logs", "read_group", "get_members"],
                "users": group_members[group_id],
            }
            items.append(item)

        # バッチでデータ投入
        with groups_table.batch_writer() as batch:
            for item in items:
                batch.put_item(Item=item)

        logger.info(f"[groups] Inserted {len(items)} groups: {[item['groupid'] for item in items]}")
        return items

    return _make


# サンプルログを DynamoDB に投入する fixture
@pytest.fixture
def make_sample_logs(logs_table):
    def _make(groups=None, count=10):
        """
        指定されたグループごとに、その所属ユーザーに対応するログを生成。
        :param groups: dict[groupid -> list[userid]]
        :param count: 各グループごとのログ件数
        :return: dict[groupid -> list of inserted items]
        """
        now = datetime.now(UTC)
        types = ["Login", "Logout"]

        # デフォルトのグループとユーザー（make_sample_groups の内容と一致させる）
        groups = groups or {
            "test-group1": ["test-admin@example.com", "test-user1@example.com", "test-user4@example.com", "test-user7@example.com", "test-user10@example.com"],
            "test-group2": ["test-admin@example.com", "test-user2@example.com", "test-user5@example.com", "test-user8@example.com"],
            "test-group3": ["test-admin@example.com", "test-user3@example.com", "test-user6@example.com", "test-user9@example.com"],
        }

        all_inserted = {}

        for groupid, user_ids in groups.items():
            items = []
            for i in range(count):
                user = user_ids[i % len(user_ids)]
                log_type = types[i % len(types)]
                items.append(
                    {
                        "groupid": groupid,
                        "created_at": (now - timedelta(minutes=i)).isoformat().replace("+00:00", "Z"),
                        "groupid#userid": f"{groupid}#{user}",
                        "groupid#type": f"{groupid}#{log_type}",
                        "userid": user,
                        "username": user.split("@")[0],
                        "type": log_type,
                        "message": f"{log_type} message {i}",
                    }
                )

            with logs_table.batch_writer() as batch:
                for item in items:
                    batch.put_item(Item=item)

            logger.info(f"[logs] Inserted {len(items)} logs for group '{groupid}' and users: {user_ids}")
            all_inserted[groupid] = items

        return all_inserted

    return _make
