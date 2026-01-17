# app/config.py
import os

from dotenv import load_dotenv

load_dotenv()  # .env ファイルを読み込む


class Settings:
    APP_NAME: str = "samplefastapi"
    ENV: str = os.getenv("ENVIRONMENT", "local")
    REGION_NAME: str = os.getenv("AWS_DEFAULT_REGION", "ap-northeast-1")
    DYNAMODB_ENDPOINT: str = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")


settings = Settings()
