# AWS デプロイマニュアル

prototype-app の AWS Lambda へのデプロイ手順。

## 前提条件

- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [Docker](https://docs.docker.com/get-docker/) (Backend ビルド用)
- AWS CLI (認証情報設定済み)

## アーキテクチャ

```
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway                            │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────┐
│    PublicFunction       │     │    SecureFunction       │
│    (認証なし)            │     │    (Cognito認証)        │
└─────────────────────────┘     └─────────────────────────┘
              │                               │
              └───────────────┬───────────────┘
                              ▼
              ┌─────────────────────────────┐
              │      Lambda Layer           │
              │  (Python Dependencies)      │
              └─────────────────────────────┘
```

## スタック一覧

| スタック | 説明 | 命名規則 |
|----------|------|----------|
| Lambda Layer | Python依存パッケージ | `prototype-app-lambda-layer-stack-{env}` |
| Backend | API Gateway + Lambda | `prototype-app-backend-stack-{env}` |

## デプロイ手順

### 1. Lambda Layer のデプロイ

Python 依存パッケージを Lambda Layer としてデプロイします。
**初回デプロイ時、または `pyproject.toml` の依存関係を更新した場合に実行してください。**

```bash
cd infrastructure/aws/lambda-layer

# 依存パッケージをビルド
./build.sh

# SAM ビルド & デプロイ
sam build --config-env devel
sam deploy --config-env devel
```

#### build.sh オプション

| オプション | 説明 | デフォルト |
|------------|------|------------|
| `--python VERSION` | Python バージョン | 3.13 |
| `--arch ARCH` | アーキテクチャ (x86_64/arm64) | x86_64 |
| `--clean` | ビルド成果物を削除 | - |

```bash
# arm64 (Graviton) 向けビルド
./build.sh --arch arm64

# クリーンアップ
./build.sh --clean
```

### 2. Backend のデプロイ

API Gateway と Lambda 関数をデプロイします。

```bash
cd infrastructure/aws/backend

# SAM ビルド (Docker コンテナ使用)
sam build --config-env devel --use-container

# デプロイ
sam deploy --config-env devel
```

## 環境別デプロイ

### Development (devel)

```bash
# Lambda Layer
cd infrastructure/aws/lambda-layer
./build.sh
sam build --config-env devel && sam deploy --config-env devel

# Backend
cd infrastructure/aws/backend
sam build --config-env devel --use-container && sam deploy --config-env devel
```

### Staging

```bash
# Lambda Layer
cd infrastructure/aws/lambda-layer
./build.sh
sam build --config-env staging && sam deploy --config-env staging

# Backend
cd infrastructure/aws/backend
sam build --config-env staging --use-container && sam deploy --config-env staging
```

### Production

```bash
# Lambda Layer
cd infrastructure/aws/lambda-layer
./build.sh
sam build --config-env prod && sam deploy --config-env prod

# Backend
cd infrastructure/aws/backend
sam build --config-env prod --use-container && sam deploy --config-env prod
```

## デプロイ結果の確認

### Lambda Layer

```bash
cd infrastructure/aws/lambda-layer
./show-outputs.sh devel
```

出力例:
```
=============================================
Stack: prototype-app-lambda-layer-stack-devel
=============================================
+-----------------+----------------------------------------------------------------------------------------+
|  LayerVersionArn|  arn:aws:lambda:ap-northeast-1:123456789:layer:prototype-app-dependencies-devel:1     |
|  LayerArn       |  arn:aws:lambda:ap-northeast-1:123456789:layer:prototype-app-dependencies-devel:1     |
+-----------------+----------------------------------------------------------------------------------------+

Export Name: prototype-app-layer-devel
```

### Backend

```bash
cd infrastructure/aws/backend
./show-outputs.sh devel
```

出力例:
```
=============================================
Stack: prototype-app-backend-stack-devel
=============================================
+------------------------+-----------------------------------------------------------------------------------+
|  ApiUrl                |  https://xxxxxxxxxx.execute-api.ap-northeast-1.amazonaws.com/v1                   |
|  SecureFunctionArn     |  arn:aws:lambda:ap-northeast-1:123456789:function:prototype-app-secure-devel      |
|  LambdaExecutionRoleArn|  arn:aws:iam::123456789:role/prototype-app-lambda-role-devel                      |
|  PublicFunctionArn     |  arn:aws:lambda:ap-northeast-1:123456789:function:prototype-app-public-devel      |
|  ApiGatewayId          |  xxxxxxxxxx                                                                       |
+------------------------+-----------------------------------------------------------------------------------+

Exports:
  API URL: prototype-app-api-url-devel
  API ID:  prototype-app-api-id-devel
```

## スタック削除

```bash
# Backend を先に削除 (Layer の Export を参照しているため)
sam delete --stack-name prototype-app-backend-stack-devel --no-prompts

# Lambda Layer を削除
sam delete --stack-name prototype-app-lambda-layer-stack-devel --no-prompts
```

## Lambda Layer 更新時の注意

Lambda Layer を更新する際、Backend スタックが Layer の Export を参照しているため、以下の順序で更新してください:

### 方法 1: Backend を一時削除して更新

```bash
# 1. Backend を削除
sam delete --stack-name prototype-app-backend-stack-devel --no-prompts

# 2. Lambda Layer を更新
cd infrastructure/aws/lambda-layer
./build.sh
sam build --config-env devel && sam deploy --config-env devel

# 3. Backend を再デプロイ
cd infrastructure/aws/backend
sam build --config-env devel --use-container && sam deploy --config-env devel
```

### 方法 2: Layer ARN を直接指定して更新

```bash
# 1. 新しい Layer をビルド・デプロイ (新しいバージョンが作成される)
cd infrastructure/aws/lambda-layer
./build.sh
sam build --config-env devel && sam deploy --config-env devel

# 2. 新しい Layer ARN を確認
./show-outputs.sh devel

# 3. Backend を新しい Layer ARN で更新
cd infrastructure/aws/backend
sam deploy --config-env devel \
  --parameter-overrides "DependenciesLayerArn=arn:aws:lambda:ap-northeast-1:123456789:layer:prototype-app-dependencies-devel:NEW_VERSION"
```

## トラブルシューティング

### Python 3.13 が見つからないエラー

```
Error: PythonPipBuilder:Validation - Binary validation failed for python
```

**解決策:** `--use-container` オプションを使用してビルド

```bash
sam build --config-env devel --use-container
```

### Layer サイズが大きすぎるエラー

Lambda Layer の最大サイズは解凍後 250MB です。

**解決策:** 不要な依存関係を `pyproject.toml` から削除

### Import エラー (ModuleNotFoundError)

Layer のパッケージが正しくインストールされていない可能性があります。

**解決策:** Layer を再ビルド

```bash
cd infrastructure/aws/lambda-layer
./build.sh --clean
./build.sh
sam build --config-env devel && sam deploy --config-env devel
```

## 環境変数の設定

### Cognito User Pool ID

Backend スタックでは Cognito User Pool による認証を使用します。デプロイ前に実際の User Pool ID を設定してください。

#### 設定方法

`infrastructure/aws/backend/samconfig.toml` にはプレースホルダーが設定されています：

```toml
[devel.deploy.parameters]
parameter_overrides = "ProjectName=prototype-app Env=devel CognitoUserPoolId=DEVEL_USER_POOL_ID"

[staging.deploy.parameters]
parameter_overrides = "ProjectName=prototype-app Env=staging CognitoUserPoolId=STAGING_USER_POOL_ID"

[prod.deploy.parameters]
parameter_overrides = "ProjectName=prototype-app Env=prod CognitoUserPoolId=PROD_USER_POOL_ID"
```

#### オプション 1: samconfig.toml を直接編集（推奨）

`samconfig.toml` を編集して、プレースホルダーを実際の User Pool ID に置き換えます。

```toml
[devel.deploy.parameters]
parameter_overrides = "ProjectName=prototype-app Env=devel CognitoUserPoolId=ap-northeast-1_xxxxxxxxx"
```

#### オプション 2: デプロイ時にパラメータで上書き

`samconfig.toml` は変更せず、デプロイ時にコマンドラインで指定します。

```bash
cd infrastructure/aws/backend

sam deploy --config-env devel \
  --parameter-overrides "ProjectName=prototype-app Env=devel CognitoUserPoolId=ap-northeast-1_xxxxxxxxx"
```

#### Cognito User Pool ID の確認方法

```bash
# Cognito User Pool の一覧を表示
aws cognito-idp list-user-pools --max-results 10 --region ap-northeast-1

# 特定の User Pool の詳細を確認
aws cognito-idp describe-user-pool \
  --user-pool-id ap-northeast-1_xxxxxxxxx \
  --region ap-northeast-1
```
