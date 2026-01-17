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
# 開発環境
# ----------------------------------------

# 事前に localstack コンテナを起動しておく必要があります。
# 事前に Cogintoも設定しておく必要があります。
#   不明な場合
#   aws cloudformation describe-stacks --query 'Stacks[].{Name:StackName, Outputs:Outputs}' --output json | jq -r '.[] | select(.Outputs != null) | "== Stack: \(.Name) ==", (.Outputs[] | "  \(.OutputKey): \(.OutputValue)")'


install: ## 🔧 フロントエンドとバックエンドのセットアップ
	@echo "🔧 Backend (uv) 環境をセットアップ中..."
	# uv sync は自動的に .venv を作成し、pyproject.toml/uv.lock の内容を同期します
	uv sync

	@echo "🌐 Frontend の依存関係をインストール中..."
	cd frontend && npm install

	@echo "✅ install 完了"

check-localstack: ## ⏳ LocalStackの起動待ち
	@echo "⏳ LocalStack の準備完了を待機中..."
	@until docker exec localstack_main aws dynamodb list-tables --endpoint-url=http://localhost:4566 --region ap-northeast-1 >/dev/null 2>&1; do \
		echo "...waiting for LocalStack"; \
		sleep 2; \
	done
	@echo "✅ LocalStack is Ready!"

dev: check-localstack
	@echo "================================================================"
	@echo "🚀  Development environment is starting up..."
	@echo ""
	@echo "🔗  Frontend:    http://localhost:5173"
	@echo "🔗  Backend API: http://localhost:8000"
	@echo "📖  Swagger UI:  http://localhost:8000/docs"
	@echo "📕  ReDoc:       http://localhost:8000/redoc"
	@echo "📄  OpenAPI:     http://localhost:8000/openapi.json"
	@echo "================================================================"
	@echo ""
	@npx concurrently -n "frontend,backend" -c "cyan,magenta" \
		"cd frontend && npm run dev" \
		"uv run --directory backend uvicorn app.main:app --reload --port 8000"

# ----------------------------------------
# LocalStack操作
# ----------------------------------------

up-localstack: ## 🚀 LocalStackだけ起動
	docker compose up -d

down-localstack: ## 🛑 LocalStackだけ停止
	docker compose down-v

logs-localstack: ## 📜 LocalStackのログ（簡易）
	docker compose logs -f localstack | grep -v -E 'DEBUG|INFO.*request.aws|INFO.*reactor'

rebuild-localstack: ## 🏗️ イメージを最新にしてから再構築（latestを使いたい時）
	docker compose pull
	docker compose down-v
	docker compose up -d --build
	docker compose logs -f localstack

# 確認方法
# docker exec -it localstack_main awslocal dynamodb list-tables
# docker exec -it localstack_main awslocal dynamodb scan --table-name samplefastapi-users-devel

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
