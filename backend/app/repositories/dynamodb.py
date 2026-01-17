"""
DynamoDBユーティリティモジュール

このモジュールは、FastAPIなどのアプリケーション層と疎結合に保った形で、
DynamoDBとの安全かつ共通化された操作を提供します。

ポリシー:
- FastAPIのHTTP例外 (HTTPException) はこの層では発生させず、戻り値やログで管理する。
- DynamoDBのキーやレスポンスをPython辞書で扱いやすい形に保つ。
- エラーはログに出力し、上位層で制御可能にする（例: 404の判定など）。
- エラーコード 429 / 500 に対しては適切なログメッセージを明示。
- boto3 の例外はそのまま伝播する（必要に応じて上位で try-catch）。

利用例:
```python
item = get_item("users", {"userid": "user1@example.com"})
if item is None:
    raise HTTPException(status_code=404, detail="User not found")
```
"""

import logging
from typing import Any

import boto3
from app.config import settings
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
serializer = TypeSerializer()
deserializer = TypeDeserializer()

# ====================
# グローバル設定
# ====================

MAX_LIMIT = 1000  # 1000件を超えないように応答を返す。
MAX_RESPONSE_SIZE = 5 * 1024 * 1024  # 5MBを超えないように応答を返す。

# ====================
# リソース／テーブル操作
# ====================


def get_dynamodb_resource():
    """DynamoDBリソースを取得する。ローカル環境ではエンドポイントを明示。"""
    if settings.ENV == "local":
        logger.debug("[get_dynamodb_resource] ENV=local")
        return boto3.resource(
            "dynamodb",
            endpoint_url=settings.DYNAMODB_ENDPOINT,
            region_name=settings.REGION_NAME,
            # aws_access_key_id="dummy",
            # aws_secret_access_key="dummy",
        )
    logger.debug("f[get_dynamodb_resource] ENV={settings.ENV}")
    return boto3.resource("dynamodb", region_name=settings.REGION_NAME)


def get_full_table_name(table_name: str) -> str:
    """
    環境とアプリ名に応じて DynamoDB テーブル名を構築する。
    local 環境では "devel" ステージに固定。
    """
    stage = "devel" if settings.ENV == "local" else settings.ENV
    return f"{settings.APP_NAME}-{table_name}-{stage}"


def get_table(table_name: str):
    """指定されたテーブルを取得する。"""
    return get_dynamodb_resource().Table(get_full_table_name(table_name))


# ====================
# 共通エラーハンドリング
# ====================


def _log_dynamodb_error(context: str, table_name: str, key: Any, e: ClientError):
    code = e.response.get("ResponseMetadata", {}).get("HTTPStatusCode")
    full_table_name = get_full_table_name(table_name)
    if code == 429:
        logger.error(f"[{context}] ⚠️{code} Throttled on table '{full_table_name}' with key {key}: {e}")
    elif code == 500:
        logger.error(f"[{context}] 🚨{code} Internal Server Error on table '{full_table_name}' with key {key}: {e}")
    else:
        logger.error(f"[{context}] 🔥{code} Error on table={full_table_name}, key={key}: {e}")


# ====================
# データ操作関数群
# ====================


def get_item(table_name: str, key: dict[str, Any]) -> dict[str, Any] | None:
    """
    指定されたキーのアイテムを1件取得します。見つからなければ None を返します。

    利用例:
        item = get_item("users", {"userid": "user1@example.com"})
    """

    table = get_table(table_name)
    try:
        response = table.get_item(Key=key)

        item = response.get("Item")
        if item is None:
            logger.warning(f"[get_item] 見つかりませんでした: table={table_name}, key={key}")
        return item
    except ClientError as e:
        _log_dynamodb_error("get_item", table_name, key, e)
        raise


def put_item(table_name: str, item: dict[str, Any]) -> None:
    """
    アイテムを挿入または上書きします。

    利用例:
        put_item("users", {"userid": "user1@example.com", "name": "Alice"})
    """
    table = get_table(table_name)
    try:
        table.put_item(Item=item)
    except ClientError as e:
        _log_dynamodb_error("put_item", table_name, item, e)
        raise


def update_item(
    table_name: str, key: dict[str, Any], update_expr: str, expr_attr_values: dict[str, Any], expr_attr_names: dict[str, str] | None = None
) -> dict[str, Any]:
    """
    指定したキーのアイテムに対して、属性を更新します。

    利用例:
        update_item("users", {"userid": "user1@example.com"},
                    "SET #n = :name",
                    {":name": "Bob"},
                    {"#n": "name"})
    """
    table = get_table(table_name)

    kwargs = {"Key": key, "UpdateExpression": update_expr, "ExpressionAttributeValues": expr_attr_values, "ReturnValues": "ALL_NEW"}
    if expr_attr_names:
        kwargs["ExpressionAttributeNames"] = expr_attr_names

    try:
        response = table.update_item(**kwargs)
        return response.get("Attributes", {})
    except ClientError as e:
        _log_dynamodb_error("update_item", table_name, key, e)
        raise


def delete_item(table_name: str, key: dict[str, Any]) -> None:
    """
    指定したキーのアイテムを削除します。

    利用例:
        delete_item("users", {"userid": "user1@example.com"})
    """
    table = get_table(table_name)
    try:
        table.delete_item(Key=key)
    except ClientError as e:
        _log_dynamodb_error("delete_item", table_name, key, e)
        raise


def batch_get_items(table_name: str, keys: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    複数のキーでまとめてアイテムを取得します（最大100件ずつ）。未取得キーは警告ログ表示

    利用例:
        items = batch_get_items("users", [{"userid": "user1@example.com"}, {"userid": "user2@example.com"}])
    """
    full_table_name = get_full_table_name(table_name)
    dynamodb = get_dynamodb_resource()
    client = dynamodb.meta.client
    BATCH_SIZE = 100
    results = []

    for i in range(0, len(keys), BATCH_SIZE):
        batch_keys = keys[i : i + BATCH_SIZE]
        request_items = {full_table_name: {"Keys": batch_keys}}

        found_items = []
        while request_items:
            response = client.batch_get_item(RequestItems=request_items)
            items = response.get("Responses", {}).get(full_table_name, [])
            found_items.extend(items)
            request_items = response.get("UnprocessedKeys", {})

        found_keys = [{k: item[k] for k in keys[0].keys() if k in item} for item in found_items]
        missing_keys = [k for k in batch_keys if k not in found_keys]
        if missing_keys:
            logger.error(f"[batch_get_items] 🔥見つからないキー: {missing_keys}")

        results.extend(found_items)

    return results


def query_items(
    table_name: str,
    key_condition_expr,
    expr_attr_values: dict[str, Any] | None = None,
    index_name: str | None = None,
    expr_attr_names: dict[str, str] | None = None,
    limit: int = 1000,
    exclusive_start_key: dict[str, Any] | None = None,
    filter_expr: Any | None = None,
) -> dict[str, Any]:
    """
    キー条件に基づいてクエリを実行し、該当するアイテムを取得します。
    結果の件数とレスポンスサイズに制限を設けています。

    Args:
        table_name: テーブル名
        key_condition_expr: KeyConditionExpression (e.g. Key("groupid").eq("group1"))
        expr_attr_values: ExpressionAttributeValues（必要に応じて）
        index_name: GSI名（必要に応じて）
        expr_attr_names: ExpressionAttributeNames（必要に応じて）
        limit: 最大取得件数（デフォルト1000）
        exclusive_start_key: ページネーション用の開始キー
        filter_expr: FilterExpression（必要に応じて）

    Returns:
        dict: {
            "Items": List[Dict[str, Any]],
            "LastEvaluatedKey": Optional[Dict[str, Any]]
        }
    """
    table = get_table(table_name)
    items = []
    total_size = 0
    last_evaluated = exclusive_start_key

    while True:
        query_kwargs = {"KeyConditionExpression": key_condition_expr, "Limit": min(MAX_LIMIT, limit - len(items))}
        if expr_attr_values:
            query_kwargs["ExpressionAttributeValues"] = expr_attr_values
        if index_name:
            query_kwargs["IndexName"] = index_name
        if expr_attr_names:
            query_kwargs["ExpressionAttributeNames"] = expr_attr_names
        if last_evaluated:
            query_kwargs["ExclusiveStartKey"] = last_evaluated
        if filter_expr:
            query_kwargs["FilterExpression"] = filter_expr

        try:
            response = table.query(**query_kwargs)
        except ClientError as e:
            _log_dynamodb_error("query_items", table_name, key_condition_expr, e)
            raise

        chunk = response.get("Items", [])
        items.extend(chunk)
        size_str = response.get("ResponseMetadata", {}).get("HTTPHeaders", {}).get("content-length", "0")
        try:
            total_size += int(size_str)
        except (TypeError, ValueError):
            pass
        last_evaluated = response.get("LastEvaluatedKey")

        if len(items) >= limit or not last_evaluated or total_size >= MAX_RESPONSE_SIZE:
            break

    return {"Items": items, "LastEvaluatedKey": last_evaluated}


def scan_items(
    table_name: str,
    filter_expr: Any | None = None,
    expr_attr_values: dict[str, Any] | None = None,
    expr_attr_names: dict[str, str] | None = None,
    limit: int = 100,
    exclusive_start_key: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    🔥特別な場合を除いて利用しないでください。
    """
    table = get_table(table_name)
    items = []
    last_evaluated = exclusive_start_key
    total_size = 0

    while True:
        scan_kwargs = {"Limit": min(MAX_LIMIT, limit - len(items))}
        if filter_expr:
            scan_kwargs["FilterExpression"] = filter_expr
        if expr_attr_values:
            scan_kwargs["ExpressionAttributeValues"] = expr_attr_values
        if expr_attr_names:
            scan_kwargs["ExpressionAttributeNames"] = expr_attr_names
        if last_evaluated:
            scan_kwargs["ExclusiveStartKey"] = last_evaluated

        try:
            response = table.scan(**scan_kwargs)
        except ClientError as e:
            _log_dynamodb_error("scan_items", table_name, filter_expr, e)
            raise

        chunk = response.get("Items", [])
        items.extend(chunk)
        size_str = response.get("ResponseMetadata", {}).get("HTTPHeaders", {}).get("content-length", "0")
        try:
            total_size += int(size_str)
        except (TypeError, ValueError):
            pass
        last_evaluated = response.get("LastEvaluatedKey")

        if len(items) >= limit or not last_evaluated or total_size >= MAX_RESPONSE_SIZE:
            break

    return {"Items": items, "LastEvaluatedKey": last_evaluated}
