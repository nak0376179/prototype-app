from typing import Any

import boto3


def infer_python_type(dynamo_value: Any) -> str:
    """DynamoDBの型からPythonの型（文字列）を推論する"""
    if isinstance(dynamo_value, str):
        return "str"
    elif isinstance(dynamo_value, (int, float)):
        # DynamoDBの数字はDecimalで返ることが多いため、実態に合わせる
        return "float" if "." in str(dynamo_value) else "int"
    elif isinstance(dynamo_value, bool):
        return "bool"
    elif isinstance(dynamo_value, list):
        return "List[Any]"
    elif isinstance(dynamo_value, dict):
        return "Dict[str, Any]"
    elif dynamo_value is None:
        return "Optional[Any]"
    return "Any"


def generate_dataclass_code(table_name: str, sample_items: list[dict[str, Any]]) -> str:
    # 全アイテムからキーと型のセットを抽出
    schema: dict[str, set[str]] = {}
    for item in sample_items:
        for key, value in item.items():
            py_type = infer_python_type(value)
            if key not in schema:
                schema[key] = {py_type}
            else:
                schema[key].add(py_type)

    # クラス定義の構築
    class_name = "".join(x.capitalize() for x in table_name.split("_")) + "Model"
    lines = [
        "from dataclasses import dataclass, field",
        "from typing import Any, List, Dict, Optional",
        "",
        "@dataclass(frozen=True)",
        f"class {class_name}:",
    ]

    for key, types in schema.items():
        # 複数の型が混在する場合は一旦Anyとするか、Unionにする
        type_hint = list(types)[0] if len(types) == 1 else "Any"
        # 全アイテムにそのキーがあるかチェックし、なければOptionalにする
        is_optional = any(key not in item for item in sample_items)
        if is_optional:
            type_hint = f"Optional[{type_hint}] = None"

        lines.append(f"    {key}: {type_hint}")

    return "\n".join(lines)


def main() -> None:
    # 設定
    TABLE_NAME = "FullstackAppItemsTableDevel"  # ここを対象テーブル名に変更
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(TABLE_NAME)

    # スキャン（データ量が多い場合はLimitを推奨）
    print(f"Scanning table: {TABLE_NAME}...")
    response = table.scan(Limit=100)  # 最初の100件で推論
    items = response.get("Items", [])

    if not items:
        print("No data found.")
        return

    # コード生成
    code = generate_dataclass_code(TABLE_NAME, items)

    # ファイル書き出し
    filename = f"{TABLE_NAME.lower()}_model.py"
    with open(filename, "w") as f:
        f.write(code)

    print(f"Successfully generated: {filename}")


if __name__ == "__main__":
    main()
