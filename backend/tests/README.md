# Backend テストマニュアル

backend のユニットテスト・統合テストの実行方法。

## 前提条件

- Python 3.13+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [LocalStack](https://docs.localstack.cloud/getting-started/installation/) (デフォルト)
- Docker (LocalStack 実行用)

## テスト環境

テストはデフォルトで **LocalStack** を使用して実行されます。
設定により **AWS DynamoDB** に切り替えることも可能です。

### 環境変数

| 変数 | デフォルト | 説明 |
|------|-----------|------|
| `TEST_USE_LOCALSTACK` | `true` | `true`: LocalStack, `false`: AWS DynamoDB |
| `LOCALSTACK_ENDPOINT` | `http://localhost:4566` | LocalStack エンドポイント |
| `AWS_DEFAULT_REGION` | `ap-northeast-1` | AWS リージョン |

## テスト構造

```
backend/tests/
├── conftest.py                    # メイン設定（DynamoDB接続、共通フィクスチャ）
├── fixtures/
│   ├── __init__.py
│   └── dynamodb.py               # DynamoDB テストフィクスチャ
├── unit/
│   ├── conftest.py               # Unit テスト共通設定
│   └── services/
│       ├── conftest.py           # Service テスト用フィクスチャ
│       ├── test_user_service.py  # UsersService テスト (12件)
│       ├── test_group_service.py # GroupService テスト (6件)
│       └── test_log_service.py   # LogsService テスト (6件)
└── integration/
    ├── conftest.py               # Integration テスト共通設定
    ├── api/                      # API エンドポイントテスト
    └── repositories/             # リポジトリテスト
```

## LocalStack の起動

テスト実行前に LocalStack を起動してください。

```bash
# Docker Compose で起動 (推奨)
docker-compose up -d localstack

# または直接起動
docker run -d \
  --name localstack \
  -p 4566:4566 \
  -e SERVICES=dynamodb,s3 \
  localstack/localstack
```

### テーブルの作成

LocalStack 起動後、テスト用テーブルを作成します。

```bash
# init-aws.sh を実行
cd infrastructure/localstack
./init-aws.sh
```

## テスト実行

### 全テスト実行

```bash
# プロジェクトルートから
uv run pytest backend/tests/

# または backend ディレクトリから
cd backend
uv run pytest tests/
```

### Unit テストのみ実行

```bash
# 全 Unit テスト
uv run pytest backend/tests/unit/

# Service テストのみ
uv run pytest backend/tests/unit/services/
```

### 特定のサービステスト実行

```bash
# UsersService テスト
uv run pytest backend/tests/unit/services/test_user_service.py

# GroupService テスト
uv run pytest backend/tests/unit/services/test_group_service.py

# LogsService テスト
uv run pytest backend/tests/unit/services/test_log_service.py
```

### 特定のテストクラス/メソッド実行

```bash
# 特定のテストクラス
uv run pytest backend/tests/unit/services/test_user_service.py::TestGetUserById

# 特定のテストメソッド
uv run pytest backend/tests/unit/services/test_user_service.py::TestGetUserById::test_returns_user_when_exists
```

### Integration テスト実行

```bash
uv run pytest backend/tests/integration/
```

## AWS DynamoDB を使用したテスト

本番環境の DynamoDB を使用してテストする場合:

```bash
# 環境変数を設定してテスト実行
TEST_USE_LOCALSTACK=false uv run pytest backend/tests/unit/services/

# または .env ファイルで設定
echo "TEST_USE_LOCALSTACK=false" >> .env
uv run pytest backend/tests/unit/services/
```

> **注意**: AWS DynamoDB を使用する場合は、適切な AWS 認証情報が設定されている必要があります。

## テストオプション

### 詳細出力

```bash
# 詳細表示 (-v)
uv run pytest backend/tests/ -v

# さらに詳細 (-vv)
uv run pytest backend/tests/ -vv
```

### カバレッジレポート

```bash
# カバレッジ付きで実行
uv run pytest backend/tests/ --cov=backend/app --cov-report=html

# レポートを表示
open htmlcov/index.html
```

### 失敗時のみ再実行

```bash
# 前回失敗したテストのみ再実行
uv run pytest backend/tests/ --lf

# 失敗したテストを最初に実行
uv run pytest backend/tests/ --ff
```

### 並列実行

```bash
# pytest-xdist を使用 (要インストール)
uv run pytest backend/tests/ -n auto
```

## テストフィクスチャ

### 自動クリーンアップ

テストフィクスチャは自動的にテストデータをクリーンアップします。

```python
def test_example(create_test_user, sample_user):
    # テストユーザーを作成（テスト終了後に自動削除）
    create_test_user(sample_user)

    # テスト実行
    ...
```

### 利用可能なフィクスチャ

| フィクスチャ | 説明 |
|-------------|------|
| `create_test_user` | 単一ユーザー作成 |
| `create_test_users` | 複数ユーザー一括作成 |
| `create_test_group` | 単一グループ作成 |
| `create_test_groups` | 複数グループ一括作成 |
| `create_test_log` | 単一ログ作成 |
| `create_test_logs` | 複数ログ一括作成 |
| `cleanup_test_user` | ユーザー手動削除 |
| `cleanup_test_group` | グループ手動削除 |
| `sample_user` | サンプルユーザーデータ |
| `sample_users` | 複数サンプルユーザーデータ |
| `sample_group` | サンプルグループデータ |
| `sample_groups` | 複数サンプルグループデータ |
| `sample_logs` | サンプルログデータ |

## トラブルシューティング

### LocalStack に接続できない

```
ResourceNotFoundException: Requested resource not found
```

**解決策:**
1. LocalStack が起動しているか確認
   ```bash
   curl http://localhost:4566/_localstack/health
   ```
2. テーブルが存在するか確認
   ```bash
   aws --endpoint-url=http://localhost:4566 dynamodb list-tables
   ```
3. テーブルが存在しない場合は作成
   ```bash
   cd infrastructure/localstack && ./init-aws.sh
   ```

### テストがスキップされる

```
SKIPPED: Table samplefastapi-users-devel does not exist
```

**解決策:** LocalStack のテーブルを作成してください。

### AWS 認証エラー

```
NoCredentialsError: Unable to locate credentials
```

**解決策:**
- LocalStack 使用時: `TEST_USE_LOCALSTACK=true` を確認
- AWS 使用時: AWS 認証情報を設定
  ```bash
  aws configure
  ```

## CI/CD での実行

GitHub Actions での実行例:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      localstack:
        image: localstack/localstack
        ports:
          - 4566:4566
        env:
          SERVICES: dynamodb
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'
      - name: Install uv
        run: pip install uv
      - name: Install dependencies
        run: uv sync
      - name: Setup DynamoDB tables
        run: |
          cd infrastructure/localstack
          ./init-aws.sh
      - name: Run tests
        run: uv run pytest backend/tests/ -v
```
