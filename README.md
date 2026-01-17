# Sample FastAPI Fullstack App

このプロジェクトは、以下の技術スタックを用いたフルスタックアプリの開発環境です：

- **バックエンド**: FastAPI + AWS Lambda (SAM デプロイ対応)
- **フロントエンド**: Vite + React + SWC + MUI
- **インフラ**: Docker Compose + LocalStack(DynamoDB/S3)

フロントエンド・バックエンドの開発環境に加え、DynamoDB や S3 も含めたすべてのコンポーネントをコンテナで構成しており、ローカルでの開発・評価が可能です。また、バックエンドは AWS SAM を使ってデプロイすることで、実際の AWS 上で Lambda、DynamoDB、S3 を利用した検証も行えます。

フロントエンドとバックエンドの両方がホットリロードに対応しており、ローカル環境に Python や Node.js をインストールしなくても動作します。VS Code 用の各種設定も含まれており、Docker と Makefile を使って簡単に起動・開発・デプロイが可能です。

---

## 📦 ディレクトリ構成

```
$ tree -I 'node_modules|.venv|__pycache__|volume|scripts|memo'
.
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── groups.py
│   │   │   ├── logs.py
│   │   │   ├── root.py
│   │   │   ├── users.py
│   │   │   └── utils
│   │   │       ├── auth.py
│   │   │       ├── authorization.py
│   │   │       └── responses.py
│   │   ├── legacy_api/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── services/
│   │   ├── utils/
│   │   ├── main.py
│   │   └── config.py
│   ├── Dockerfile
│   └── lambda_handler.py
├── frontend/
│   └── src/
│       ├── components
│       ├── hooks
│       ├── layouts
│       ├── pages
│       └── stores
├── infrastructure
│   ├── aws
│   └── localstack
├── Makefile
├── pyproject.toml
├── samconfig.toml
├── samplefastapi-app.code-workspace
├── start-dev.sh
└── template.yaml
```

---

## 🚀 クイックスタート

### 開発環境の起動

```bash
make up           # Docker コンテナ起動
```

フロントエンドとバックエンドと LocalStack を立ち上げ、すべてローカルで動作する状態になります。(Cognito は AWS 上の物を使います。)

- フロントエンド: http://localhost:5173
- フロントエンドとバックエンドはホットリロードが効きます。
- 補足
  - バックエンド: `curl http://localhost:8000/`
  - LocalStack: `aws dynamodb list-tables --endpoint-url=http://localhost:4566`

バックエンドの API テストには、FrontEnd のほか、以下のように curl も使用できます
（sam local start-api の場合は localhost:3000）

```
token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InRlc3R1c2VyIn0.dummysignature

curl http://localhost:8000/users -H "Authorization: Bearer $token"
curl http://localhost:8000/groups/group1 -H "Authorization: Bearer $token"
curl http://localhost:8000/groups/group1/users -H "Authorization: Bearer $token"
```

### 開発環境の構成

- **default（env=local）**
  - frontend: local, backend: local, infra: localstack
- **env=devel**
  - frontend: local, backend: local, infra: AWS
- **sam local start-api**
  - frontend: local, backend: local(Lambda), infra: localstack
  - frontend: local, backend: local(Lambda), infra: AWS
- **sam deploy --config-env devel**
  - frontend: local, backend: AWS, infra: AWS

### 開発環境の終了

```bash
make down           # Docker コンテナ 停止
```

### テスト

バックエンド（pytest）

```bash
make backend-test         # pytest
make backend-test-v       # 詳細ログ付き
```

---

## ⚙️ よく使う Make コマンド

| コマンド名              | 説明                               |
| ----------------------- | ---------------------------------- |
| `make up`               | Docker Compose 起動（全サービス）  |
| `make down`             | Docker Compose 停止                |
| `make restart-backend`  | バックエンドのみ再ビルド＆再起動   |
| `make restart-frontend` | フロントエンドのみ再ビルド＆再起動 |
| `make logs-backend`     | バックエンドログ表示               |
| `make frontend-install` | React の依存インストール           |

すべてのコマンドは `make help` で確認できます。

---

## 構成

Lambda のデプロイは zip 形式

FastAPI を利用する構成ですが、利用しない場合と併用できる構成です。

API 層、サービス層、リポジトリ層

## 🧪 テストについて

- `backend/tests/` 以下に `pytest` ベースのテストを配置。
  - DynamoDB/S3 と連動した単体試験が可能
  - 毎回新規グループを作成して良いのでテストの再現性が容易

- `AWS SAM` で devel 環境での評価も可能

---

## ☁️ デプロイ環境（SAM）

```bash
make sam-build           # Lambda用のビルド
make sam-deploy          # devel環境にデプロイ
make sam-deploy ENV=prod # prod環境にデプロイ
```

---

## 🏗️ 各ディレクトリの説明

### backend/

- FastAPI アプリケーション本体。
- Lambda は通常の zip アップロード形式で `lambda_handler.py` をルートに配置。
- `core/`, `models/`, `routes/`, `utils/` でモジュール分割。
- DynamoDB 操作用の `core/db/dynamodb.py` を含む。

### frontend/

- Vite + React + MUI による SPA 構成。
- 認証は AWS Cognito を利用。
- `pages/`, `components/`, `hooks/` などで構成。

### infrastructure/localstack/

- LocalStack を用いた開発用 AWS 疑似環境。
- 無料版はデータの永続化がないため、コンテナ起動時に初期設定を実施
- コンテナ起動時に`init-aws.sh` で初期設定。初期データは `data/*.jsonl`

### infrastructure/aws/

- AWS 環境に構築されるリソースの SAM テンプレート群。
  - `cognito/` ... 開発用ユーザープール構築
  - `dynamodb/` ... 開発用テーブル定義
  - `s3/` ... 静的ファイル保存用（オプション）

---

## 📝 その他

- Vite + React では `.env` に `VITE_API_BASE_URL` を設定してください。
- Makefile で環境統一されており、複雑な操作は不要です。

---

## 補足

### 🔐 認証・認可の仕組み

本アプリケーションでは、**AWS Cognito** を用いてユーザー認証を行っています。以下のような仕組みで、ログイン状態の管理と API アクセス制御を実現しています。

### 認証

- フロントエンドでユーザーがログインすると、Cognito から **JWT アクセストークン** を取得します。
- このトークンは `Authorization: Bearer <token>` ヘッダーとして API に送信されます。

### 認可

- バックエンドでは、JWT の署名とペイロードを検証し、ユーザー情報を取得します。
- API ハンドラ内では `auth.py` や `authorization.py` を通じて、ユーザーの権限（例：管理者かどうか、特定グループへのアクセス可否など）をチェックします。

### 実装上のポイント

- FastAPI の **Depends** を活用し、共通の認証・認可ロジックをミドルウェア的に適用。
- グループごとのアクセス制御など、より細かな認可要件には `authorization.py` 内のユーティリティ関数を使用。

### テスト方法の例

```bash
# 認証トークンを用いたAPIアクセス
token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InRlc3R1c2VyIn0.dummysignature

curl http://localhost:8000/groups/group1 \
  -H "Authorization: Bearer $token"
```
