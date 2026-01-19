"""
AWSに設定するので注意
python3 fast_loader_aws.py prototype-app-groups-devel ../../localstack/data/groups.jsonl
python3 fast_loader_aws.py prototype-app-users-devel ../../localstack/data/users.jsonl
python3 fast_loader_aws.py prototype-app-logs-devel ../../localstack/data/logs.jsonl
"""

import json
import sys
from itertools import islice
from typing import Any

import boto3

TABLE_NAME = sys.argv[1]
FILE_PATH = sys.argv[2]

dynamodb = boto3.client("dynamodb", region_name="ap-northeast-1")


def batch_write_requests(file_path: str) -> Any:
    with open(file_path, encoding="utf-8") as f:
        while True:
            batch = list(islice(f, 25))
            if not batch:
                break
            yield [{"PutRequest": {"Item": json.loads(line)}} for line in batch]


for batch in batch_write_requests(FILE_PATH):
    response = dynamodb.batch_write_item(RequestItems={TABLE_NAME: batch})
    if response.get("UnprocessedItems"):
        print("⚠️ 一部データが未処理です。再試行が必要です。")
