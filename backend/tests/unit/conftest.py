# tests/unit/conftest.py
"""
Unit テスト共通設定

LocalStack (デフォルト) または AWS DynamoDB を使用してテストを実行します。
"""

import pytest

# pytest_plugins で DynamoDB フィクスチャを読み込む
pytest_plugins = ["tests.fixtures.dynamodb"]


@pytest.fixture(autouse=True)
def setup_test_environment(ensure_tables_exist):
    """テスト環境のセットアップ（テーブル存在確認）"""
    yield
