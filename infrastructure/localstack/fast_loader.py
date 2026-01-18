"""
###############################################################################
# このスクリプトは、LocalStack が自動実行する初期化スクリプトです。
###############################################################################

JSONL ファイルから指定された DynamoDB テーブルへ一括でデータを投入します。

使用方法:
    python3 fast_loader.py <table_name> <file_path>

引数:
    table_name: 投入先の DynamoDB テーブル名
    file_path : JSON Lines 形式のファイルパス

主な処理:
    - 指定された JSONL ファイルを 25件ずつ読み取り
    - batch_write_item を使って DynamoDB に一括登録
    - UnprocessedItems がある場合には警告を表示
"""

import json
import sys
from itertools import islice
from typing import Any

import boto3

# 引数からテーブル名とファイルパスを取得
TABLE_NAME = sys.argv[1]
FILE_PATH = sys.argv[2]

# LocalStack 用の DynamoDB クライアントを作成
dynamodb = boto3.client("dynamodb", endpoint_url="http://localhost:4566", region_name="ap-northeast-1")


def batch_write_requests(file_path: str) -> Any:
    """
    指定された JSONL ファイルを 25 件ずつ読み取り、DynamoDB の
    batch_write_item に渡せる形式のリクエストを生成するジェネレータ。
    """
    with open(file_path, encoding="utf-8") as f:
        while True:
            batch = list(islice(f, 25))  # 最大25行ずつ取得
            if not batch:
                break
            yield [{"PutRequest": {"Item": json.loads(line)}} for line in batch]


# 25件ずつバッチ投入
for batch in batch_write_requests(FILE_PATH):
    response = dynamodb.batch_write_item(RequestItems={TABLE_NAME: batch})
    if response.get("UnprocessedItems"):
        print("⚠️ 一部データが未処理です。再試行が必要です。")
