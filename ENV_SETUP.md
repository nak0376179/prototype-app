# 環境変数セットアップガイド

prototype-app の環境変数を一元管理するためのガイドです。

## 📋 概要

このプロジェクトでは、ルートの `.env` ファイルで環境変数を一元管理し、`make sync-env` コマンドで frontend/.env と backend/samconfig.toml に自動反映します。

### メリット

- ✅ **一元管理**: すべての環境変数をルートの .env で管理
- ✅ **不整合防止**: frontend/backend間の設定ミスを防止
- ✅ **簡単な環境切り替え**: コマンド一つで環境を切り替え
- ✅ **デプロイエラー防止**: 設定漏れによるデプロイ失敗を防止

---

## 🚀 クイックスタート

### 1. 環境変数ファイルの作成

```bash
# プロジェクトルートで実行
cp .env.example .env
```

### 2. 実際の値を設定

`.env` ファイルを編集して、実際の Cognito User Pool ID などを設定します。

```bash
vi .env
```

最低限、以下を設定してください：

```bash
# Development環境
COGNITO_USER_POOL_ID_DEVEL=ap-northeast-1_cweb1dtCm
COGNITO_CLIENT_ID_DEVEL=5jpmvagfingjca4ceekmp552b3
```

### 3. 環境変数を同期

```bash
# Development環境に同期（デフォルト）
make sync-env

# または
python3 scripts/sync-env.py --env devel
```

### 4. 確認

同期後、以下のファイルが更新されます：

- `frontend/.env`: Frontend用の環境変数
- `infrastructure/aws/backend/samconfig.toml`: Backend SAM設定

---

## 📂 ファイル構成

```
prototype-app/
├── .env                          # 環境変数の一元管理（Gitに含めない）
├── .env.example                  # 環境変数テンプレート（Gitに含める）
├── frontend/
│   ├── .env                      # Frontend用（make sync-envで自動生成）
│   └── .env.sample              # Frontend用テンプレート
├── infrastructure/aws/backend/
│   └── samconfig.toml           # Backend SAM設定（make sync-envで自動更新）
└── scripts/
    └── sync-env.py              # 環境変数同期スクリプト
```

---

## 🔄 環境変数同期の仕組み

### ルート .env の設定項目

```bash
# ========================================
# AWS Settings
# ========================================
AWS_REGION=ap-northeast-1
AWS_ACCOUNT_ID=123456789012

# ========================================
# Cognito Settings
# ========================================
# Development環境
COGNITO_USER_POOL_ID_DEVEL=ap-northeast-1_cweb1dtCm
COGNITO_CLIENT_ID_DEVEL=5jpmvagfingjca4ceekmp552b3

# Staging環境
COGNITO_USER_POOL_ID_STAGING=ap-northeast-1_yyyyyyyyy
COGNITO_CLIENT_ID_STAGING=yyyyyyyyyyyyyyyyyy

# Production環境
COGNITO_USER_POOL_ID_PROD=ap-northeast-1_zzzzzzzzz
COGNITO_CLIENT_ID_PROD=zzzzzzzzzzzzzzzzzz

# ========================================
# API Settings
# ========================================
API_URL_LOCAL=http://localhost:8000
API_URL_DEVEL=https://api-devel.example.com
API_URL_STAGING=https://api-staging.example.com
API_URL_PROD=https://api.example.com
```

### Frontend .env への反映

`make sync-env ENV=devel` を実行すると、以下のように生成されます：

```bash
VITE_API_URL=http://localhost:8000
VITE_REGION=ap-northeast-1
VITE_USER_POOL_ID=ap-northeast-1_cweb1dtCm
VITE_USER_POOL_WEB_CLIENT_ID=5jpmvagfingjca4ceekmp552b3
VITE_DEMO_USER_POOL_ID=ap-northeast-1_cweb1dtCm
VITE_DEMO_USER_POOL_WEB_CLIENT_ID=5jpmvagfingjca4ceekmp552b3
```

### Backend samconfig.toml への反映

```toml
[devel.deploy.parameters]
parameter_overrides = "ProjectName=prototype-app Env=devel CognitoUserPoolId=ap-northeast-1_cweb1dtCm"

[staging.deploy.parameters]
parameter_overrides = "ProjectName=prototype-app Env=staging CognitoUserPoolId=ap-northeast-1_yyyyyyyyy"

[prod.deploy.parameters]
parameter_overrides = "ProjectName=prototype-app Env=prod CognitoUserPoolId=ap-northeast-1_zzzzzzzzz"
```

---

## 💡 使用シナリオ

### シナリオ 1: 初期セットアップ

新しいメンバーがプロジェクトに参加した場合：

```bash
# 1. リポジトリをクローン
git clone <repository-url>
cd prototype-app

# 2. 環境変数ファイルを作成
cp .env.example .env

# 3. 実際の値を設定（チームから共有された値）
vi .env

# 4. 環境変数を同期
make sync-env

# 5. 開発サーバー起動
make dev
```

### シナリオ 2: 環境の切り替え

Staging環境でテストする場合：

```bash
# Staging環境用のfrontend/.envを生成
make sync-env ENV=staging

# Frontendを起動
cd frontend && npm run dev
```

元に戻す：

```bash
# Development環境に戻す
make sync-env ENV=devel
```

### シナリオ 3: Cognito設定の更新

新しい Cognito User Pool を作成した場合：

```bash
# 1. ルートの.envを更新
vi .env
# COGNITO_USER_POOL_ID_DEVEL=<new-pool-id> に変更

# 2. frontend/backendに反映
make sync-env

# 3. デプロイ
cd infrastructure/aws/backend
sam deploy --config-env devel
```

### シナリオ 4: 複数環境のデプロイ

```bash
# 1. すべての環境の設定を.envに記入
vi .env

# 2. Development環境にデプロイ
make sync-env ENV=devel
cd infrastructure/aws/backend
sam deploy --config-env devel

# 3. Staging環境にデプロイ
make sync-env ENV=staging
sam deploy --config-env staging

# 4. Production環境にデプロイ
make sync-env ENV=prod
sam deploy --config-env prod
```

---

## ✅ デプロイ前チェックリスト

### Development環境デプロイ前

- [ ] `.env` ファイルが存在する
- [ ] `COGNITO_USER_POOL_ID_DEVEL` が設定されている
- [ ] `COGNITO_CLIENT_ID_DEVEL` が設定されている
- [ ] `make sync-env` を実行済み
- [ ] `frontend/.env` が正しく生成されている
- [ ] `infrastructure/aws/backend/samconfig.toml` の devel セクションに正しいUser Pool IDが設定されている

### Staging/Production環境デプロイ前

- [ ] 該当環境の Cognito User Pool ID が `.env` に設定されている
- [ ] `make sync-env ENV=<環境名>` を実行済み
- [ ] `samconfig.toml` の該当セクションが更新されている

---

## 🔐 セキュリティ

### .env ファイルの取り扱い

- ✅ `.env` は `.gitignore` に含まれており、**Git にコミットされません**
- ✅ `.env.example` はテンプレートとして **Git にコミットします**（実際の値は含めない）
- ⚠️ `.env` ファイルはチーム内で安全に共有してください（Slack DM、1Password等）
- ⚠️ 本番環境の認証情報は特に慎重に扱ってください

### Cognito User Pool ID の確認

```bash
# User Pool一覧を表示
aws cognito-idp list-user-pools --max-results 10 --region ap-northeast-1

# 特定のUser Poolの詳細
aws cognito-idp describe-user-pool \
  --user-pool-id ap-northeast-1_xxxxxxxxx \
  --region ap-northeast-1
```

---

## 🛠️ トラブルシューティング

### .env ファイルが見つからない

```bash
# エラー: .env not found
❌ .env not found
ℹ  Copy .env.example to .env and set your values

# 解決策
cp .env.example .env
vi .env
```

### Cognito User Pool ID が未設定

```bash
# 症状: samconfig.tomlにプレースホルダーが残っている
parameter_overrides = "... CognitoUserPoolId=DEVEL_USER_POOL_ID"

# 解決策
vi .env  # COGNITO_USER_POOL_ID_DEVEL を設定
make sync-env
```

### デプロイ時のエラー

```bash
# エラー: Invalid parameter value for CognitoUserPoolId

# 確認1: .envの設定を確認
cat .env | grep COGNITO

# 確認2: 同期を再実行
make sync-env

# 確認3: samconfig.tomlを確認
cat infrastructure/aws/backend/samconfig.toml | grep CognitoUserPoolId
```

---

## 📚 関連ドキュメント

- [scripts/README.md](scripts/README.md) - スクリプトの詳細説明
- [infrastructure/aws/DEPLOY.md](infrastructure/aws/DEPLOY.md) - デプロイ手順
- [infrastructure/aws/backend/README.md](infrastructure/aws/backend/README.md) - Backend設定
