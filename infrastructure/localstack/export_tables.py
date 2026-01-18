"""
このスクリプトは、AWS 上の DynamoDB テーブル定義をローカルにバックアップし、
LocalStack や他環境で再構築できるように、以下の2種類の JSON ファイルを出力します：

1. describe_tables/: describe-table のレスポンスをそのまま保存
2. create_tables/: create-table コマンドに使える JSON を整形して保存

前提条件:
- AWS CLI がインストールされていること
- `aws configure` によって認証情報とリージョンが設定されていること
"""

import json
import os
import subprocess
from typing import Any

AWS_REGION = "ap-northeast-1"

# このスクリプトのあるディレクトリを基準にパスを構築
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DESCRIBE_DIR = os.path.join(BASE_DIR, "dynamodb", "describe_tables")
CREATE_DIR = os.path.join(BASE_DIR, "dynamodb", "create_tables")

# 出力ディレクトリを作成（存在する場合は何もしない）
os.makedirs(DESCRIBE_DIR, exist_ok=True)
os.makedirs(CREATE_DIR, exist_ok=True)


def filter_provisioned_throughput(pt: Any) -> dict[str, int]:
    """
    ProvisionedThroughput フィールドから不要なデータを除き、最低限の構造で返す。

    Args:
        pt (dict): describe-table または GSI 内の ProvisionedThroughput 情報。

    Returns:
        dict: ReadCapacityUnits と WriteCapacityUnits のみを含む辞書。
    """
    return {
        "ReadCapacityUnits": pt.get("ReadCapacityUnits", 5),
        "WriteCapacityUnits": pt.get("WriteCapacityUnits", 5),
    }


print("📋 AWS からテーブル一覧を取得しています...")

# AWS CLI を使って DynamoDB テーブル名一覧を取得
result = subprocess.run(
    ["aws", "dynamodb", "list-tables", "--region", AWS_REGION],
    stdout=subprocess.PIPE,
    text=True,
    check=True,
)

tables = json.loads(result.stdout).get("TableNames", [])
print(f"✅ {len(tables)} 件のテーブルを検出しました: {tables}")

# 各テーブルに対して describe + create JSON を生成
for table_name in tables:
    print(f"🔍 テーブルの詳細情報を取得中: {table_name}")

    describe_path = os.path.join(DESCRIBE_DIR, f"{table_name}.json")
    create_path = os.path.join(CREATE_DIR, f"{table_name}.json")

    # describe-table を取得
    result = subprocess.run(
        [
            "aws",
            "dynamodb",
            "describe-table",
            "--table-name",
            table_name,
            "--region",
            AWS_REGION,
        ],
        stdout=subprocess.PIPE,
        text=True,
        check=True,
    )

    describe_json = json.loads(result.stdout)

    # describe JSON を保存
    with open(describe_path, "w") as f:
        json.dump(describe_json, f, indent=2)
    print("📁 describe_tablesに保存しました")

    # create-table 用に整形
    table_def = describe_json["Table"]
    create_json = {
        "TableName": table_def["TableName"],
        "AttributeDefinitions": table_def["AttributeDefinitions"],
        "KeySchema": table_def["KeySchema"],
        "BillingMode": table_def.get("BillingMode", "PAY_PER_REQUEST"),
    }

    # GSI (Global Secondary Indexes) があれば整形して追加
    if "GlobalSecondaryIndexes" in table_def:
        create_json["GlobalSecondaryIndexes"] = [
            {
                "IndexName": gsi["IndexName"],
                "KeySchema": gsi["KeySchema"],
                "Projection": gsi["Projection"],
                "ProvisionedThroughput": filter_provisioned_throughput(gsi.get("ProvisionedThroughput", {})),
            }
            for gsi in table_def["GlobalSecondaryIndexes"]
        ]

    # create JSON を保存（常に上書き）
    with open(create_path, "w") as f:
        json.dump(create_json, f, indent=2)
    print("✅ create-tables に保存しました")
