# Backend API Infrastructure

FastAPI Backend を AWS Lambda + API Gateway としてデプロイするための SAM テンプレート。

## 前提条件

- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
- AWS CLI (認証情報設定済み)
- **Lambda Layer がデプロイ済みであること** (`infrastructure/aws/lambda-layer`)

## ディレクトリ構造

```
backend/
├── template.yaml      # SAM テンプレート
├── samconfig.toml     # 環境別設定
├── show-outputs.sh    # デプロイ済みスタックのOutput確認
├── README.md          # このファイル
└── .gitignore
```

## デプロイ順序

Lambda Layer を先にデプロイしてから Backend をデプロイしてください。

```bash
# 1. Lambda Layer をデプロイ (初回または依存関係更新時)
cd infrastructure/aws/lambda-layer
./build.sh
sam build --config-env devel && sam deploy --config-env devel

# 2. Backend をデプロイ
cd infrastructure/aws/backend
sam build --config-env devel && sam deploy --config-env devel
```

## 使用方法

### SAM ビルド & デプロイ

```bash
cd infrastructure/aws/backend

# Development 環境
sam build --config-env devel
sam deploy --config-env devel

# Staging 環境
sam build --config-env staging
sam deploy --config-env staging

# Production 環境
sam build --config-env prod
sam deploy --config-env prod
```

### デプロイ済みスタックのOutput確認

```bash
# devel 環境 (デフォルト)
./show-outputs.sh

# 環境を指定
./show-outputs.sh devel
./show-outputs.sh staging
./show-outputs.sh prod
```

## スタック命名規則

```
{ProjectName}-backend-stack-{Env}
```

例:
- `prototype-app-backend-stack-devel`
- `prototype-app-backend-stack-staging`
- `prototype-app-backend-stack-prod`

## Lambda Layer の参照

デフォルトでは CloudFormation Export を使用して Lambda Layer を参照します:

```yaml
Layers:
  - !ImportValue prototype-app-layer-devel
```

Layer ARN を直接指定する場合は `DependenciesLayerArn` パラメータを使用:

```bash
sam deploy --config-env devel \
  --parameter-overrides "DependenciesLayerArn=arn:aws:lambda:ap-northeast-1:123456789:layer:my-layer:1"
```

## Outputs

| Output | Description | Export Name |
|--------|-------------|-------------|
| ApiUrl | API Gateway endpoint URL | `{ProjectName}-api-url-{Env}` |
| ApiGatewayId | API Gateway ID | `{ProjectName}-api-id-{Env}` |
| PublicFunctionArn | Public Lambda Function ARN | - |
| SecureFunctionArn | Secure Lambda Function ARN | - |
| LambdaExecutionRoleArn | Lambda Execution Role ARN | - |

## API エンドポイント

| Path | Method | Auth | Description |
|------|--------|------|-------------|
| `/` | GET | None | ヘルスチェック |
| `/users` | ANY | Cognito | ユーザー一覧/作成 |
| `/users/{userid}` | ANY | Cognito | ユーザー詳細/更新/削除 |
| `/groups` | ANY | Cognito | グループ一覧/作成 |
| `/groups/{groupid}` | ANY | Cognito | グループ詳細/更新/削除 |
| `/groups/{groupid}/users` | ANY | Cognito | グループユーザー一覧/追加 |
| `/groups/{groupid}/users/{userid}` | ANY | Cognito | グループユーザー詳細/削除 |
| `/groups/{groupid}/logs` | ANY | Cognito | グループログ一覧/作成 |

## 環境変数

| 変数名 | 説明 |
|--------|------|
| ENVIRONMENT | デプロイ環境 (devel/staging/prod) |

## 注意事項

- Cognito User Pool ID は環境ごとに `samconfig.toml` で設定してください
- staging/prod 環境の `CognitoUserPoolId` はプレースホルダーです。実際の値に置き換えてください
- Lambda Layer の更新後は Backend の再デプロイが必要です
