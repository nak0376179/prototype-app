# prototype-app DynamoDB Tables

このスタックは、prototype-app アプリケーションで使用する DynamoDB テーブルを AWS SAM を使って構築するためのものです。

---

## 📦 作成される DynamoDB テーブル

### 👤 `prototype-app-users-{Stage}`

- **主キー**: `userid (HASH)`
- **用途**: ユーザー情報の保存
- **課金モード**: プロビジョンド（RCU/WCU = 1）

---

### 👥 `prototype-app-groups-{Stage}`

- **主キー**: `groupid (HASH)`
- **用途**: グループ情報の保存
- **課金モード**: プロビジョンド（RCU/WCU = 1）

---

### 📝 `prototype-app-logs-{Stage}`

- **主キー**:
  - `groupid (HASH)`
  - `created_at (RANGE)`

- **用途**: グループ内のアクティビティログの保存
- **課金モード**: プロビジョンド（RCU/WCU = 1）

- **グローバルセカンダリインデックス（GSI）**:
  - `groupid-type-created_at-index`
    - パーティションキー: `groupid#type`
    - ソートキー: `created_at`
    - RCU/WCU: 1/1
  - `groupid-userid-created_at-index`
    - パーティションキー: `groupid#userid`
    - ソートキー: `created_at`
    - RCU/WCU: 1/1

---

## 📋 前提条件

### 必要なツール

1. **AWS CLI** (v2 推奨)
   ```bash
   # インストール確認
   aws --version

   # インストールされていない場合
   # macOS/Linux: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
   ```

2. **AWS SAM CLI** (v1.0+ 推奨)
   ```bash
   # インストール確認
   sam --version

   # インストールされていない場合
   # https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html
   ```

### AWS 認証情報の設定

デプロイ前に AWS 認証情報を設定してください。

```bash
# AWS CLI で認証情報を設定
aws configure

# または環境変数で設定
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="ap-northeast-1"
```

### 必要な IAM 権限

以下の権限が必要です：
- `dynamodb:CreateTable`
- `dynamodb:DescribeTable`
- `dynamodb:DeleteTable`
- `cloudformation:CreateStack`
- `cloudformation:UpdateStack`
- `cloudformation:DescribeStacks`

---

## 🚀 デプロイ手順

### 1. ディレクトリ移動

```bash
cd infrastructure/aws/dynamodb
```

### 2. デプロイ実行

#### 開発環境 (devel) へデプロイ

```bash
sam deploy \
  --stack-name prototype-app-dynamodb-stack-devel \
  --parameter-overrides Stage=devel \
  --region ap-northeast-1 \
  --capabilities CAPABILITY_IAM \
  --resolve-s3
```

#### ステージング環境 (staging) へデプロイ

```bash
sam deploy \
  --stack-name prototype-app-dynamodb-stack-staging \
  --parameter-overrides Stage=staging \
  --region ap-northeast-1 \
  --capabilities CAPABILITY_IAM \
  --resolve-s3
```

#### 本番環境 (prod) へデプロイ

```bash
sam deploy \
  --stack-name prototype-app-dynamodb-stack-prod \
  --parameter-overrides Stage=prod \
  --region ap-northeast-1 \
  --capabilities CAPABILITY_IAM \
  --resolve-s3 \
  --confirm-changeset  # 本番環境では変更セットを確認
```

### デプロイオプションの説明

| オプション | 説明 |
|----------|------|
| `--stack-name` | CloudFormation スタック名 |
| `--parameter-overrides` | テンプレートパラメータの上書き（Stage=devel など） |
| `--region` | デプロイ先のリージョン |
| `--capabilities` | IAM リソース作成の許可 |
| `--resolve-s3` | SAM がアーティファクト用の S3 バケットを自動作成 |
| `--confirm-changeset` | 変更セットを確認してからデプロイ（本番推奨） |

---

## ✅ デプロイ後の確認

### 1. スタックの状態を確認

```bash
# CloudFormation スタックの状態を確認
aws cloudformation describe-stacks \
  --stack-name prototype-app-dynamodb-stack-devel \
  --region ap-northeast-1 \
  --query 'Stacks[0].StackStatus'
```

期待される出力: `"CREATE_COMPLETE"` または `"UPDATE_COMPLETE"`

### 2. 作成されたテーブルを確認

```bash
# テーブル一覧を取得
aws dynamodb list-tables --region ap-northeast-1

# 特定のテーブルの詳細を確認
aws dynamodb describe-table \
  --table-name prototype-app-users-devel \
  --region ap-northeast-1
```

### 3. テーブルのアイテム数を確認

```bash
# users テーブルのアイテム数
aws dynamodb scan \
  --table-name prototype-app-users-devel \
  --select COUNT \
  --region ap-northeast-1

# groups テーブルのアイテム数
aws dynamodb scan \
  --table-name prototype-app-groups-devel \
  --select COUNT \
  --region ap-northeast-1

# logs テーブルのアイテム数
aws dynamodb scan \
  --table-name prototype-app-logs-devel \
  --select COUNT \
  --region ap-northeast-1
```

---

## 📊 テストデータの投入

テーブル作成後、テストデータを投入する場合は `fast_loader_aws.py` を使用します。

```bash
# データファイルを準備（localstack/sample_data から取得）
# ※事前にテストデータを生成しておく必要があります

# users テーブルにデータ投入
python3 fast_loader_aws.py \
  prototype-app-users-devel \
  ../../localstack/dynamodb/sample_data/prototype-app-users-devel.jsonl

# groups テーブルにデータ投入
python3 fast_loader_aws.py \
  prototype-app-groups-devel \
  ../../localstack/dynamodb/sample_data/prototype-app-groups-devel.jsonl

# logs テーブルにデータ投入
python3 fast_loader_aws.py \
  prototype-app-logs-devel \
  ../../localstack/dynamodb/sample_data/prototype-app-logs-devel.jsonl
```

---

## 🔄 スタックの更新

テンプレートを変更した後、同じデプロイコマンドを実行すると更新されます。

```bash
sam deploy \
  --stack-name prototype-app-dynamodb-stack-devel \
  --parameter-overrides Stage=devel \
  --region ap-northeast-1 \
  --capabilities CAPABILITY_IAM \
  --resolve-s3
```

CloudFormation が変更を検出し、差分のみを適用します。

---

## 🗑️ スタックの削除

テーブルを削除する場合は、CloudFormation スタックを削除します。

```bash
# 削除コマンド
aws cloudformation delete-stack \
  --stack-name prototype-app-dynamodb-stack-devel \
  --region ap-northeast-1

# 削除状態を監視
aws cloudformation wait stack-delete-complete \
  --stack-name prototype-app-dynamodb-stack-devel \
  --region ap-northeast-1

# 削除完了を確認
aws cloudformation describe-stacks \
  --stack-name prototype-app-dynamodb-stack-devel \
  --region ap-northeast-1
```

**警告**: テーブルを削除すると、すべてのデータが失われます。本番環境では慎重に実行してください。

---

## 🛠️ トラブルシューティング

### スタック作成が失敗する

**エラー**: `User is not authorized to perform: cloudformation:CreateStack`

**解決策**: IAM ユーザーに適切な権限が付与されているか確認してください。

```bash
# 現在のユーザーの権限を確認
aws iam get-user
aws iam list-attached-user-policies --user-name <your-username>
```

### テーブル名が既に存在する

**エラー**: `Table already exists: prototype-app-users-devel`

**解決策**:
1. 既存のテーブルを削除するか、別の Stage 名を使用してください
2. または、CloudFormation スタックを更新モードで実行してください

### S3 バケットのエラー

**エラー**: `Unable to upload artifact ... No bucket named`

**解決策**: `--resolve-s3` オプションを使用するか、手動で S3 バケットを作成してください。

```bash
# 手動で S3 バケットを作成
aws s3 mb s3://sam-deployment-artifacts-<your-account-id> --region ap-northeast-1

# バケット名を指定してデプロイ
sam deploy \
  --stack-name prototype-app-dynamodb-stack-devel \
  --parameter-overrides Stage=devel \
  --region ap-northeast-1 \
  --capabilities CAPABILITY_IAM \
  --s3-bucket sam-deployment-artifacts-<your-account-id>
```

---

## 📝 補足情報

### コスト

- **プロビジョンドモード**: RCU/WCU が 1 ずつ設定されているため、月額コストは最小限です
- **logs テーブルの GSI**: 2つの GSI があるため、追加コストが発生します

### 本番環境での推奨設定

本番環境では以下の変更を検討してください：

1. **課金モードの変更**: PAY_PER_REQUEST（オンデマンド）に変更
2. **バックアップの有効化**: Point-in-time recovery (PITR) を有効化
3. **RCU/WCU の調整**: 予想されるトラフィックに応じて調整

テンプレートを編集して変更：

```yaml
BillingMode: PAY_PER_REQUEST  # プロビジョンドから変更
PointInTimeRecoverySpecification:
  PointInTimeRecoveryEnabled: true  # バックアップ有効化
```

---

## 🔗 関連リンク

- [AWS SAM CLI Documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html)
- [DynamoDB Pricing](https://aws.amazon.com/dynamodb/pricing/)
- [CloudFormation Template Reference](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dynamodb-table.html)
