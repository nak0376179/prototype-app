# ----------------------------------------
# このMakefileはLocalStackベースの開発に特化しています。
# 切り替え方法:
#   make -f Makefile.localstack <target>
#   例: make -f Makefile.localstack up
# ----------------------------------------

# 設定変数
ENV ?= devel
REGION = ap-northeast-1

.DEFAULT_GOAL := help

.PHONY: up install ps clean \
        up-localstack down-localstack restart-localstack logs-localstack logs-localstack-v logs \
        generate-test-data init-dynamodb \
        sam-build sam-deploy sam-start-api \
        help

# ----------------------------------------
# 開発環境全体
# ----------------------------------------

dev: ## 🟢 開発環境の起動（frontend/backend/LocalStack）


install: ## 🔧 frontend/backend の依存関係をインストール
	@echo "🔧 Backend Python 環境をセットアップ中..."
	@if [ ! -d backend/.venv ]; then \
		echo "📦 .venv が見つかりません。仮想環境を作成します..."; \
		python3 -m venv backend/.venv; \
	fi
	@. backend/.venv/bin/activate && pip install --upgrade pip && pip install -r backend/requirements-dev.txt

	@echo "🌐 Frontend の依存関係をインストール中..."
	cd frontend && npm install

	@echo "✅ install 完了"

# ----------------------------------------
# LocalStack操作
# ----------------------------------------

up-localstack: ## 🚀 LocalStackだけ起動
	docker compose up -d

down-localstack: ## 🛑 LocalStackだけ停止
	docker compose down

restart-localstack: ## ♻️ LocalStack再起動
	docker compose restart localstack

logs-localstack: ## 📜 LocalStackのログ（簡易）
	docker compose logs -f localstack | grep -v -E 'DEBUG|INFO.*request.aws|INFO.*reactor'

logs-localstack-v: ## 📜 LocalStackのログ（詳細）
	docker compose logs -f localstack

logs: logs-localstack ## 📜 default: localstackのみ表示

ps: ## 📦 LocalStackコンテナ状態確認
	docker compose ps

down: down-localstack ## 🛑 停止

# ----------------------------------------
# サンプルデータ操作
# ----------------------------------------

generate-test-data: ## 🧪 初期データを生成
	python3 infrastructure/localstack/generate_test_data.py

init-dynamodb: ## 🗄️ DynamoDB構造とサンプルを本番から取得
	python3 infrastructure/localstack/export_tables.py
	python3 infrastructure/localstack/export_sample_jsonl.py

# ----------------------------------------
# SAM操作（Lambdaビルド・デプロイ・ローカルAPI起動）
# ----------------------------------------

sam-build: ## 🏗️ SAM用Lambdaビルド
	sam build --use-container

sam-deploy: ## 🚀 SAMスタックデプロイ
	sam deploy --config-env $(ENV)

sam-invoke: ## 🧪 任意のLambdaをローカルで実行（例: make invoke FUNCTION=MyFunction EVENT=event.json）
	@if [ -z "$(FUNCTION)" ]; then echo "❌ FUNCTION を指定してください（例: make invoke FUNCTION=MyFunction）"; exit 1; fi
	@echo "🚀 Invoking $(FUNCTION) ..."
	sam local invoke $(FUNCTION) --event $(if $(EVENT),$(EVENT),event.json)

sam-start-api: ## 🌐 SAMローカルAPI起動（warm container有効）
	sam local start-api --warm-containers EAGER

test-backend: ## ✅ backend のユニットテストを実行（pytest）
	PYTHONPATH=./backend . backend/.venv/bin/activate && pytest backend/tests

test-backend-v: ## ✅ backend のユニットテストを実行（pytest）
	PYTHONPATH=./backend . backend/.venv/bin/activate && pytest backend/tests -s -v

# ----------------------------------------
# Utility
# ----------------------------------------

clean: ## 🧹 dockerの未使用リソースをクリーンアップ（安全）
	docker container prune -f
	docker image prune -f
	docker volume prune -f
	docker network prune -f

help: ## 🆘 このヘルプを表示
	@grep -E '^[a-zA-Z0-9_-]+:.*?## ' $(MAKEFILE_LIST) \
	| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
