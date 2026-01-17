# FastAPI 　段階移行案

## 目的

非 FastAPI 構成から段階的に **FastAPI** に移行する場合のディレクトリ構成案

**段階的に共存・移行可能**な形で開発・運用できるディレクトリ構成を提案してもらいました。
FastAPI に依存しすぎず、ロジックやデータアクセスを共通化することで、再利用性・保守性を高めます。

---

## ディレクトリ構成

```
app/
├── main.py                   # FastAPIエントリポイント
├── handlers/
│   ├── lambda/               # Lambdaハンドラ
│   │   └── lambda_entry.py   # Lambdaエントリポイント
│   └── api/                  # FastAPIハンドラ
├── services/                 # ビジネスロジック
├── repositories/             # DynamoDB/S3(外部I/O依存)
├── models/                   # Pydanticや内部型定義
└── config/                   # 環境設定、依存注入など
```

---

## 各層の役割

| ディレクトリ       | 役割概要                                                                |
| ------------------ | ----------------------------------------------------------------------- |
| `api/`             | FastAPI ルーティング定義。HTTP エンドポイントの登録。                   |
| `lambda_handlers/` | Lambda イベント（event, context）用のハンドラー関数。                   |
| `services/`        | ビジネスロジック層。業務ルール・処理の中心。API/Lambda 共通で使われる。 |
| `repositories/`    | データアクセス層。DynamoDB, S3 などとのやり取りを管理。                 |
| `models/`          | 入出力スキーマ（Pydantic）。データの構造を表現。                        |
| `config/`          | 設定・環境変数などの読み込み処理。                                      |
| `main.py`          | FastAPI アプリ起動ポイント（開発/デプロイ用）                           |
| `lambda_entry.py`  | Mangum を介した Lambda エントリーポイント。                             |

---

## コード共通化の流れ

### ✅ services/ でロジックを共通化

```python
# services/group_service.py

from app.repositories.group_repository import save_group
from app.models.group_model import Group

def create_group(name: str) -> Group:
    group = Group(name=name)
    save_group(group)
    return group
```

---

### ✅ FastAPI ルーティング例

```python
# api/group.py

from fastapi import APIRouter
from app.models.group_request import CreateGroupRequest
from app.services.group_service import create_group

router = APIRouter()

@router.post("/groups")
def create_group_endpoint(request: CreateGroupRequest):
    return create_group(request.name)
```

---

### ✅ Lambda ハンドラー例

```python
# lambda_handlers/group_handler.py

from app.services.group_service import create_group

def lambda_handler(event, context):
    body = event.get("body", {})
    return create_group(body["name"])
```

---

## 移行戦略と利点

- ✅ Lambda 既存コードを `lambda_handlers/` に置くことで **段階移行**が可能
- ✅ `services/` / `repositories/` による **ビジネスロジックの再利用**
- ✅ 将来的に API 化が進んでも、既存 Lambda コードの共存を妨げない
- ✅ FastAPI 依存を最小限にし、**汎用的な構成**

---

## 起動ポイント

- 開発時・API 用 → `main.py`（FastAPI + Uvicorn）
- Lambda 用 → `lambda_entry.py`（Mangum 経由）

---

## まとめ

この構成では、**FastAPI と Lambda の共存**を実現しつつ、ビジネスロジック・データアクセスを共通利用することで、将来的な API 集中・マイクロサービス展開もスムーズに行えます。

「API か Lambda か」の差を意識せず、**ロジック中心の設計**に集中できる構造になっています。
