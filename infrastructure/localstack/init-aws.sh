#!/bin/bash
set -e  # エラーが発生した時点でスクリプトを終了

###############################################################################
# このスクリプトは、LocalStack が自動実行する初期化スクリプトです。
###############################################################################

# 主な処理内容:
#   - infrastructure/localstack/s3/ 以下のディレクトリ名から S3 バケットを作成し、
#     各ディレクトリの中身を再帰的にアップロード。
#   - infrastructure/localstack/dynamodb/create_tables/ の JSON 定義に基づいて、
#     DynamoDB テーブルを作成。
#   - infrastructure/localstack/dynamodb/sample_data/ にある JSONL ファイルをもとに、
#     各 DynamoDB テーブルへデータを一括投入。

echo "🚀 LocalStack セットアップ開始"

# S3 初期化ブロック
S3_ROOT_DIR="/opt/code/localstack/s3"

echo "📦 S3 初期化処理開始..."

for bucket_dir in "$S3_ROOT_DIR"/*; do
  if [ -d "$bucket_dir" ]; then
    bucket_name=$(basename "$bucket_dir")
    echo "🪣 バケット作成: $bucket_name"
    # バケットを作成
    awslocal s3 mb "s3://$bucket_name"

    echo "📤 $bucket_dir 以下のファイルをアップロード中..."
    # バケットにファイルをアップロード（再帰的）
    awslocal s3 cp "$bucket_dir" "s3://$bucket_name" --recursive --quiet
  fi
done

echo "✅ S3 初期化完了"

# DynamoDB テーブル作成ブロック
echo "📂 DynamoDB テーブル作成中..."

# ディレクトリを変数に定義して確実に指定
TABLE_DIR="/opt/code/localstack/dynamodb/create_tables"

for f in "$TABLE_DIR"/*.json; do
  if [ -f "$f" ]; then
    filename=$(basename "$f")
    echo "📄 $filename を作成中..."
    # awslocalを使用
    awslocal dynamodb create-table --cli-input-json "file://$f"
  else
    echo "⚠️ $TABLE_DIR に JSON ファイルが見つかりません"
  fi
done

echo "✅ テーブル作成完了"

# サンプルデータ投入ブロック
echo "📥 サンプルデータ投入開始..."

for file in /opt/code/localstack/dynamodb/sample_data/*.jsonl; do
  if [ -f "$file" ]; then
    table_name=$(basename "$file" .jsonl)

    # テーブルの存在確認（無ければスキップ）
    if ! awslocal dynamodb describe-table --table-name "$table_name" >/dev/null 2>&1; then
      echo "⚠️ テーブル $table_name が存在しません。スキップします。"
      continue
    fi

    echo "📥 $table_name に投入中..."
    # JSONL ファイルを Python スクリプトで投入（1行 = 1アイテム）
    python3 /opt/code/localstack/fast_loader.py "$table_name" "$file"
  else
    echo "⚠️ sample_data/ に JSONL ファイルが見つかりません"
  fi
done

echo "🎉 LocalStack 初期化完了！"
