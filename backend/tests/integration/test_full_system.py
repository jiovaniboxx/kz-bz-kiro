"""
全システム統合テスト
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestFullSystemIntegration:
    """全システム統合テスト"""
    
    def test_health_endpoints_integration(self):
        """ヘルスチェックエンドポイント統合テスト"""
        # 基本ヘルスチェック
        response = client.get("/health")
        assert response.status_code == 200
        health_data = response.json()
        assert health_data["status"] == "healthy"
        
        # API ヘルスチェック
        response = client.get("/api/health")
        assert response.status_code == 200
        api_health_data = response.json()
        assert api_health_data["status"] == "healthy"
        
        # 監視ヘルスチェック
        response = client.get("/api/monitoring/health")
        assert response.status_code == 200
        monitoring_data = response.json()
        assert monitoring_data["status"] == "healthy"
    
    def test_contact_form_integration(self):
        """問い合わせフォーム統合テスト"""
        # 有効な問い合わせデータ
        valid_contact = {
            "name": "統合テスト太郎",
            "email": "integration@test.com",
            "phone": "090-1234-5678",
            "message": "統合テストメッセージです",
            "lesson_type": "trial",
            "preferred_contact": "email"
        }
        
        response = client.post("/api/contacts", json=valid_contact)
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "問い合わせを受け付けました"
        assert "contact_id" in data
        assert data["status"] == "received"
    
    def test_monitoring_integration(self):
        """監視機能統合テスト"""
        # 統計情報取得
        response = client.get("/api/monitoring/stats")
        assert response.status_code == 200
        
        stats_data = response.json()
        assert "contacts" in stats_data
        assert "system" in stats_data
        
        # 問い合わせ統計確認
        contacts_stats = stats_data["contacts"]
        assert "total" in contacts_stats
        assert "today" in contacts_stats
        assert "pending" in contacts_stats
        
        # システム統計確認
        system_stats = stats_data["system"]
        assert "cpu_usage" in system_stats
        assert "memory_usage" in system_stats
        assert "disk_usage" in system_stats
    
    def test_error_handling_integration(self):
        """エラーハンドリング統合テスト"""
        # 存在しないエンドポイント
        response = client.get("/api/nonexistent")
        assert response.status_code == 404
        
        # 無効なメソッド
        response = client.delete("/api/contacts")
        assert response.status_code == 405
    
    def test_cors_integration(self):
        """CORS統合テスト"""
        # プリフライトリクエスト
        response = client.options(
            "/api/contacts",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        # FastAPIのCORSミドルウェアが適切に処理することを確認
        assert response.status_code in [200, 204]
    
    def test_api_response_format_consistency(self):
        """APIレスポンス形式一貫性テスト"""
        endpoints = [
            "/health",
            "/api/health", 
            "/api/monitoring/health",
            "/api/monitoring/stats"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200
            
            # JSONレスポンスであることを確認
            data = response.json()
            assert isinstance(data, dict)
            
            # 基本的なステータス情報が含まれていることを確認
            if "health" in endpoint:
                assert "status" in data or "message" in data