"""
メインアプリケーションのユニットテスト
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """ルートエンドポイントのテスト"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "英会話カフェWebサイト API"
    assert data["version"] == "1.0.0"


def test_health_check():
    """ヘルスチェックエンドポイントのテスト"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "english-cafe-api"


def test_api_health_check():
    """APIヘルスチェックエンドポイントのテスト"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["api"] == "operational"


def test_create_contact():
    """問い合わせ作成エンドポイントのテスト"""
    contact_data = {
        "name": "テスト太郎",
        "email": "test@example.com",
        "message": "テストメッセージ"
    }
    response = client.post("/api/contacts", json=contact_data)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "問い合わせを受け付けました"
    assert "contact_id" in data


def test_monitoring_health():
    """監視ヘルスチェックエンドポイントのテスト"""
    response = client.get("/api/monitoring/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "services" in data


def test_monitoring_stats():
    """監視統計エンドポイントのテスト"""
    response = client.get("/api/monitoring/stats")
    assert response.status_code == 200
    data = response.json()
    assert "contacts" in data
    assert "system" in data