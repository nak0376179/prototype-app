# Lambda Layer for Python Dependencies

Python依存パッケージをLambda Layerとしてデプロイするための SAM テンプレート。

## 前提条件

- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- AWS CLI (認証情報設定済み)

## ディレクトリ構造

```
lambda-layer/
├── template.yaml      # SAM テンプレート
├── samconfig.toml     # 環境別設定
├── build.sh           # 依存パッケージビルドスクリプト
├── show-outputs.sh    # デプロイ済みスタックのOutput確認
├── README.md          # このファイル
└── layer/             # ビルド成果物 (git ignore)
    └── python/        # Lambda Layer用のPythonパッケージ
```

## 使用方法

### 1. 依存パッケージのビルド

```bash
cd infrastructure/aws/lambda-layer

# x86_64 アーキテクチャ (デフォルト)
./build.sh

# arm64 (Graviton) アーキテクチャ
./build.sh --arch arm64

# Python バージョン指定
./build.sh --python 3.12

# クリーンアップ
./build.sh --clean
```

### 2. SAM ビルド & デプロイ

```bash
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

### 3. デプロイ済みスタックのOutput確認

```bash
# devel 環境 (デフォルト)
./show-outputs.sh

# 環境を指定
./show-outputs.sh devel
./show-outputs.sh staging
./show-outputs.sh prod
```

出力例:
```
=============================================
Stack: prototype-app-lambda-layer-stack-devel
=============================================
-----------------------------------------
|           DescribeStacks              |
+------------------+--------------------+
|  LayerArn        |  arn:aws:lambda:...|
|  LayerVersionArn |  arn:aws:lambda:...|
+------------------+--------------------+

Export Name: prototype-app-layer-devel
```

## スタック命名規則

スタック名は以下の形式で作成されます:

```
{ProjectName}-lambda-layer-stack-{Env}
```

例:
- `prototype-app-lambda-layer-stack-devel`
- `prototype-app-lambda-layer-stack-staging`
- `prototype-app-lambda-layer-stack-prod`

## Outputs

デプロイ後、以下の値がエクスポートされます:

| Output | Description | Export Name |
|--------|-------------|-------------|
| LayerArn | Layer ARN | `{ProjectName}-layer-{Env}` |
| LayerVersionArn | Layer Version ARN | - |

## Lambda 関数での使用

デプロイされた Layer を Lambda 関数で使用する場合:

### SAM テンプレートでの参照

```yaml
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      Layers:
        - !ImportValue prototype-app-layer-devel
```

### AWS CLI での参照

```bash
# Layer ARN を取得
aws cloudformation describe-stacks \
  --stack-name prototype-app-lambda-layer-stack-devel \
  --query 'Stacks[0].Outputs[?OutputKey==`LayerVersionArn`].OutputValue' \
  --output text
```

## 注意事項

- Lambda Layer の最大サイズは解凍後 250MB です
- `layer/` ディレクトリは `.gitignore` に追加してください
- Production 環境では `confirm_changeset = false` に設定されています
