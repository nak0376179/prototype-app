import uuid
from datetime import UTC, datetime

import boto3
import pytest
from app.repositories.groups import GroupsTable

DYNAMODB_ENDPOINT = "http://localhost:4566"
GROUPS_TABLE_NAME = "samplefastapi-groups-devel"


@pytest.fixture(scope="module")
def dynamodb_resource():
    """DynamoDBのboto3リソース（LocalStack経由）を返す"""
    return boto3.resource("dynamodb", endpoint_url=DYNAMODB_ENDPOINT, region_name="ap-northeast-1")


@pytest.fixture(scope="module")
def groups_table(dynamodb_resource):
    """DynamoDB groups テーブルオブジェクトを返す"""
    return dynamodb_resource.Table(GROUPS_TABLE_NAME)


@pytest.fixture
def make_sample_groups(groups_table):
    """テストごとに新規グループデータを作成してLocalStackに登録するファクトリ"""

    def _make(user_count: int = 3):
        groupid = f"grp{uuid.uuid4().hex[:28]}"
        users = [f"user{i}@example.com" for i in range(1, user_count + 1)]

        group_item = {
            "groupid": groupid,
            "groupname": f"Test Group {groupid[-6:]}",
            "description": "This is a sample group for testing.",
            "created_at": datetime.now(UTC).isoformat(),
            "users": users,
        }

        groups_table.put_item(Item=group_item)
        return group_item

    return _make


def test_get_group_by_id(make_sample_groups):
    """正常に group を取得できる"""
    sample = make_sample_groups()
    group_table = GroupsTable()
    result = group_table.get_group_by_id(sample["groupid"])
    assert result is not None
    assert result["groupid"] == sample["groupid"]


def test_get_group_by_id_not_found():
    """グループが存在しない場合は None を返す"""
    group_table = GroupsTable()
    result = group_table.get_group_by_id("grp-does-not-exist")
    assert result is None
