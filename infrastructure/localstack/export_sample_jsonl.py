import json
import os
import subprocess
from typing import Any

AWS_REGION = "ap-northeast-1"
MAX_ITEMS = 50  # 各テーブルから取得する最大アイテム数

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DESCRIBE_DIR = os.path.join(BASE_DIR, "dynamodb", "describe_tables")
OUTPUT_DIR = os.path.join(BASE_DIR, "dynamodb", "sample_data")

os.makedirs(OUTPUT_DIR, exist_ok=True)


def scan_table_sample(table_name: str, max_items: int) -> Any:
    print(f"📥 テーブル「{table_name}」から最大 {max_items} 件のデータを取得中 (Scan)...")
    result = subprocess.run(
        [
            "aws",
            "dynamodb",
            "scan",
            "--table-name",
            table_name,
            "--region",
            AWS_REGION,
            "--limit",
            str(max_items),
        ],
        stdout=subprocess.PIPE,
        text=True,
        check=True,
    )
    return json.loads(result.stdout).get("Items", [])


def query_table_sample(table_name: str, pk_name: str, pk_value: str, max_items: int) -> Any:
    print(f"📥 テーブル「{table_name}」から最大 {max_items} 件のデータを取得中 (Query)...")
    result = subprocess.run(
        [
            "aws",
            "dynamodb",
            "query",
            "--table-name",
            table_name,
            "--region",
            AWS_REGION,
            "--limit",
            str(max_items),
            "--key-condition-expression",
            f"{pk_name} = :pkval",
            "--expression-attribute-values",
            json.dumps({":pkval": pk_value}),
        ],
        stdout=subprocess.PIPE,
        text=True,
        check=True,
    )
    return json.loads(result.stdout).get("Items", [])


def load_existing_jsonl(path: str) -> list[Any]:
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def merge_items(
    existing_items: Any, new_items: Any, pk_name: str, sk_name: str | None = None
) -> tuple[Any, int, int, int]:
    item_map = {}
    overwrite_count = 0
    new_count = 0
    unchanged_count = 0

    def make_key(item: Any) -> tuple[str, str | None]:
        pk_val = json.dumps(item[pk_name])
        sk_val = json.dumps(item[sk_name]) if sk_name and sk_name in item else None
        return (pk_val, sk_val)

    for item in existing_items:
        item_map[make_key(item)] = item

    for item in new_items:
        key = make_key(item)
        new_item_serialized = json.dumps(item, sort_keys=True)

        if key in item_map:
            existing_item_serialized = json.dumps(item_map[key], sort_keys=True)
            if new_item_serialized != existing_item_serialized:
                print(f"🔁 上書き: {pk_name}={key[0]}" + (f", {sk_name}={key[1]}" if sk_name else ""))
                item_map[key] = item
                overwrite_count += 1
            else:
                unchanged_count += 1
        else:
            print(f"➕ 新規追加: {pk_name}={key[0]}" + (f", {sk_name}={key[1]}" if sk_name else ""))
            item_map[key] = item
            new_count += 1

    merged = list(item_map.values())
    return merged, new_count, overwrite_count, unchanged_count


# メイン処理
for filename in os.listdir(DESCRIBE_DIR):
    if not filename.endswith(".json"):
        continue

    table_name = filename.replace(".json", "")
    describe_path = os.path.join(DESCRIBE_DIR, filename)

    try:
        with open(describe_path) as f:
            desc = json.load(f)

        key_schema = desc["Table"]["KeySchema"]
        pk_name = key_schema[0]["AttributeName"]
        sk_name = key_schema[1]["AttributeName"] if len(key_schema) > 1 else None

        # ユーザーに PK 入力を求める
        pk_input = input(
            f"🔑 テーブル「{table_name}」のパーティションキー「{pk_name}」の値を指定しますか？(空で scan): "
        ).strip()
        if pk_input:
            pk_value: Any = {desc["Table"]["AttributeDefinitions"][0]["AttributeType"]: pk_input}
            items = query_table_sample(table_name, pk_name, pk_value, MAX_ITEMS)
        else:
            items = scan_table_sample(table_name, MAX_ITEMS)

        if not items:
            print("⚠️ データが見つかりませんでした。")
            continue

        output_path = os.path.join(OUTPUT_DIR, f"{table_name}.jsonl")
        existing_items = load_existing_jsonl(output_path)

        merged_items, new_count, overwrite_count, unchanged_count = merge_items(existing_items, items, pk_name, sk_name)

        with open(output_path, "w") as f:
            for item in merged_items:
                f.write(json.dumps(item) + "\n")

        print(
            f"✅ 保存しました。🧾 登録済み: {len(merged_items)} 件 "
            f"（新規 {new_count} 件、上書き {overwrite_count} 件、未更新 {unchanged_count} 件）\n"
        )

    except subprocess.CalledProcessError as e:
        print(f"❌ テーブル「{table_name}」の取得中にエラーが発生しました: {e}")
    except Exception as e:
        print(f"❌ 想定外のエラー: {e}")
