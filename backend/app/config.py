# app/config.py
import os

from dotenv import load_dotenv

load_dotenv()  # .env ファイルを読み込む


class Settings:
    APP_NAME: str = "prototype-app"
    ENV: str = os.getenv("ENVIRONMENT", "local")
    REGION_NAME: str = os.getenv("AWS_DEFAULT_REGION", "ap-northeast-1")
    DYNAMODB_ENDPOINT: str | None = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")

    # テスト用設定
    # TEST_USE_LOCALSTACK=true (デフォルト) → LocalStack を使用
    # TEST_USE_LOCALSTACK=false → AWS DynamoDB を使用
    TEST_USE_LOCALSTACK: bool = os.getenv("TEST_USE_LOCALSTACK", "true").lower() == "true"
    LOCALSTACK_ENDPOINT: str = os.getenv("LOCALSTACK_ENDPOINT", "http://localhost:4566")

    @property
    def is_test_mode(self) -> bool:
        """テストモードかどうかを判定"""
        return self.ENV == "test" or self.ENV == "local"

    @property
    def dynamodb_endpoint_url(self) -> str | None:
        """DynamoDB エンドポイント URL を返す (AWS の場合は None)"""
        if self.ENV == "test":
            return self.LOCALSTACK_ENDPOINT if self.TEST_USE_LOCALSTACK else None
        if self.ENV == "local":
            return self.DYNAMODB_ENDPOINT
        return None


settings = Settings()
