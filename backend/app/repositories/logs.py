# api/repositories/logs.py

from typing import Any

import boto3
from app.repositories.dynamodb import query_items  # ← 共通の query_items を使う前提
from boto3.dynamodb.conditions import Key


class LogsTable:
    def __init__(self, dynamodb=None):
        self.dynamodb = dynamodb or boto3.resource("dynamodb")
        self.table_name = "logs"

    def list_logs(
        self,
        groupid: str,
        limit: int = 25,
        startkey: dict[str, Any] | None = None,
        begin: str | None = None,
        end: str | None = None,
        userid: str | None = None,
        type_: str | None = None,
    ) -> dict[str, Any]:
        # GSI 切り替えと KeyConditionExpression の構築
        if userid:
            key_condition = Key("groupid#userid").eq(f"{groupid}#{userid}")
            index_name = "groupid-userid-created_at-index"
        elif type_:
            key_condition = Key("groupid#type").eq(f"{groupid}#{type_}")
            index_name = "groupid-type-created_at-index"
        else:
            key_condition = Key("groupid").eq(groupid)
            index_name = None  # ベーステーブルを使用

        if begin and end:
            key_condition &= Key("created_at").between(begin, end)
        elif begin:
            key_condition &= Key("created_at").gte(begin)
        elif end:
            key_condition &= Key("created_at").lte(end)

        # 実クエリ
        result = query_items(
            table_name=self.table_name,
            key_condition_expr=key_condition,
            index_name=index_name,
            exclusive_start_key=startkey,
            limit=limit,
        )

        # 結果整形（25件に制限、LastEvaluatedKey の付加）
        response: dict[str, Any] = {"Items": result["Items"][:limit]}
        if result.get("LastEvaluatedKey"):
            response["LastEvaluatedKey"] = result["LastEvaluatedKey"]
        return response
