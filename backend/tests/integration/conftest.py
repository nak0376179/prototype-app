# tests/integration/conftest.py

from typing import Any

import boto3
import pytest
from app.config import settings
from app.main import app
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def dynamodb_resource() -> Any:
    return boto3.resource(
        "dynamodb",
        endpoint_url=settings.DYNAMODB_ENDPOINT,
        region_name=settings.REGION_NAME,
        aws_access_key_id="dummy",
        aws_secret_access_key="dummy",
    )


@pytest.fixture(scope="session")
def client() -> TestClient:
    return TestClient(app)
