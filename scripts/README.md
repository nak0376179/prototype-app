# Scripts

prototype-app の運用・管理用スクリプト集です。

---

## 🔄 sync-env.py

ルートの `.env` ファイルから frontend/.env と backend/samconfig.toml を自動生成します。

### 目的

frontend と backend で環境変数を一元管理し、設定の不整合を防ぎます。

### 使用方法

#### 1. ルートの .env ファイルを作成

```bash
# .env.example をコピー
cp .env.example .env

# 実際の値を設定
vi .env
```

#### 2. 環境変数を同期

```bash
# Development環境用に同期（デフォルト）
python3 scripts/sync-env.py

# または make コマンドで
make sync-env

# Staging環境用に同期
make sync-env ENV=staging

# Production環境用に同期
make sync-env ENV=prod
```

### 同期される内容

#### Frontend (.env)
- `VITE_API_URL`: API エンドポイント
- `VITE_REGION`: AWS リージョン
- `VITE_USER_POOL_ID`: Cognito User Pool ID
- `VITE_USER_POOL_WEB_CLIENT_ID`: Cognito Client ID
- `VITE_DEMO_USER_POOL_ID`: デモ用 User Pool ID
- `VITE_DEMO_USER_POOL_WEB_CLIENT_ID`: デモ用 Client ID

#### Backend (samconfig.toml)
- `CognitoUserPoolId`: 各環境の User Pool ID

### ルート .env ファイルの設定項目

```bash
# Development環境
COGNITO_USER_POOL_ID_DEVEL=ap-northeast-1_xxxxxxxxx
COGNITO_CLIENT_ID_DEVEL=xxxxxxxxxxxxxxxxxx
API_URL_LOCAL=http://localhost:8000

# Staging環境
COGNITO_USER_POOL_ID_STAGING=ap-northeast-1_yyyyyyyyy
COGNITO_CLIENT_ID_STAGING=yyyyyyyyyyyyyyyyyy
API_URL_STAGING=https://staging-api.example.com

# Production環境
COGNITO_USER_POOL_ID_PROD=ap-northeast-1_zzzzzzzzz
COGNITO_CLIENT_ID_PROD=zzzzzzzzzzzzzzzzzz
API_URL_PROD=https://api.example.com
```

### ワークフロー

1. **初期セットアップ時**
   ```bash
   cp .env.example .env
   # .env を編集して実際の値を設定
   make sync-env
   ```

2. **環境を切り替える時**
   ```bash
   # Staging環境用のfrontend/.envを生成
   make sync-env ENV=staging
   ```

3. **Cognito設定を更新する時**
   ```bash
   # ルートの.envを編集
   vi .env

   # frontend/backendに反映
   make sync-env
   ```

### メリット

- ✅ frontend/backend間の設定不整合を防止
- ✅ 環境変数の一元管理
- ✅ 環境切り替えが簡単
- ✅ デプロイ前のエラーを防止

---

## 📊 show-env.py

AWS上にデプロイされているprototype-app関連のリソースを確認するスクリプトです。

### 機能

- **Lambda Layer Stack**: Lambda Layerスタックの状態と出力を表示
- **Backend Stack**: Backendスタックのパラメータと出力を表示
- **DynamoDB Tables**: DynamoDBテーブルの状態とアイテム数を表示
- **Cognito User Pool**: Cognito User Poolの詳細を表示

### 使用方法

#### 基本的な使い方

```bash
# すべての情報を表示（デフォルト: devel環境）
python3 scripts/show-env.py

# 環境を指定
python3 scripts/show-env.py --env staging

# リージョンを指定
python3 scripts/show-env.py --env prod --region us-east-1
```

#### 特定のコンポーネントのみ表示

```bash
# Lambda Layerのみ
python3 scripts/show-env.py --component layer

# Backendスタックのみ
python3 scripts/show-env.py --component backend

# DynamoDBテーブルのみ
python3 scripts/show-env.py --component dynamodb

# Cognito User Poolのみ
python3 scripts/show-env.py --component cognito
```

#### Makefileから実行

```bash
# すべての情報を表示
make show-env

# 環境を指定
make show-env ENV=staging

# 特定のコンポーネントのみ
make show-layer      # Lambda Layer
make show-backend    # Backend API
make show-dynamodb   # DynamoDB Tables
make show-cognito    # Cognito User Pool
```

### オプション

| オプション | 説明 | デフォルト値 | 選択肢 |
|-----------|------|------------|--------|
| `--env` | 環境名 | `devel` | `devel`, `staging`, `prod` |
| `--region` | AWSリージョン | `ap-northeast-1` | 任意のAWSリージョン |
| `--component` | 表示するコンポーネント | `all` | `all`, `layer`, `backend`, `dynamodb`, `cognito` |

### 前提条件

1. **AWS CLI**: インストールと認証設定が必要
   ```bash
   aws configure
   ```

2. **Python 3**: Python 3.7以上

3. **適切なIAM権限**:
   - `cloudformation:DescribeStacks`
   - `dynamodb:DescribeTable`
   - `dynamodb:Scan`
   - `cognito-idp:DescribeUserPool`

### 出力例

```
================================================================================
📊  prototype-app AWS Environment Status (ENV=devel, REGION=ap-northeast-1)
================================================================================


🔧 Lambda Layer Stack: prototype-app-lambda-layer-stack-devel
--------------------------------------------------------------------------------
  Status: CREATE_COMPLETE

  Outputs:
    LayerArn: arn:aws:lambda:ap-northeast-1:123456789012:layer:prototype-app-dependencies-devel:1
    LayerVersionArn: arn:aws:lambda:ap-northeast-1:123456789012:layer:prototype-app-dependencies-devel:1


🚀 Backend Stack: prototype-app-backend-stack-devel
--------------------------------------------------------------------------------
  Status: UPDATE_COMPLETE

  Parameters:
    ProjectName: prototype-app
    Env: devel
    CognitoUserPoolId: ap-northeast-1_mEDAZ9b89

  Outputs:
    ApiUrl: https://abcdef1234.execute-api.ap-northeast-1.amazonaws.com/v1
    ApiGatewayId: abcdef1234
    PublicFunctionArn: arn:aws:lambda:ap-northeast-1:123456789012:function:prototype-app-public-devel
    SecureFunctionArn: arn:aws:lambda:ap-northeast-1:123456789012:function:prototype-app-secure-devel


🗄️  DynamoDB Tables
--------------------------------------------------------------------------------
  ✓  prototype-app-users-devel: ACTIVE (30 items)
  ✓  prototype-app-groups-devel: ACTIVE (10 items)
  ✓  prototype-app-logs-devel: ACTIVE (200 items)

================================================================================
```

### 特徴

- **カラフルな出力**: ターミナルで見やすいカラー表示
- **prototype-app強調**: `prototype-app`という文字列を緑色の太字で強調表示
- **ステータスの色分け**: スタックやテーブルのステータスに応じて色を変更
  - 緑: 正常（`COMPLETE`, `ACTIVE`）
  - 黄: 警告（進行中など）
  - 赤: エラー

---

## 🔧 トラブルシューティング

### スクリプトが見つからない

```bash
# 実行権限を付与
chmod +x scripts/show-env.py
```

### AWS認証エラー

```bash
# AWS認証情報を確認
aws sts get-caller-identity

# 認証情報を再設定
aws configure
```

### リソースが見つからない

- 指定した環境にリソースがデプロイされていない可能性があります
- 環境名（`--env`）とリージョン（`--region`）が正しいか確認してください

---

## 📝 今後の拡張予定

- [ ] JSON/YAML形式での出力サポート
- [ ] CloudWatch Logsの確認機能
- [ ] コスト情報の表示
- [ ] デプロイ履歴の表示
