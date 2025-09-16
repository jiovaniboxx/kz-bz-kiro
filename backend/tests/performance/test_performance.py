"""
パフォーマンステスト
"""

import pytest
import time
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestPerformance:
    """パフォーマンステスト"""
    
    def test_health_check_response_time(self):
        """ヘルスチェックエンドポイントの応答時間テスト"""
        # 10回実行して平均応答時間を測定
        response_times = []
        
        for _ in range(10):
            start_time = time.time()
            response = client.get("/health")
            end_time = time.time()
            
            assert response.status_code == 200
            response_times.append(end_time - start_time)
        
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        
        # 平均応答時間が500ms以下であることを確認
        assert avg_response_time < 0.5, f"平均応答時間が遅すぎます: {avg_response_time:.3f}s"
        
        # 最大応答時間が1秒以下であることを確認
        assert max_response_time < 1.0, f"最大応答時間が遅すぎます: {max_response_time:.3f}s"
        
        print(f"ヘルスチェック - 平均応答時間: {avg_response_time:.3f}s, 最大応答時間: {max_response_time:.3f}s")
    
    def test_contact_form_response_time(self):
        """問い合わせフォーム送信の応答時間テスト"""
        contact_data = {
            "name": "パフォーマンステスト太郎",
            "email": "performance@test.com",
            "phone": "090-1234-5678",
            "message": "パフォーマンステスト用メッセージです",
            "lesson_type": "trial",
            "preferred_contact": "email"
        }
        
        response_times = []
        
        for i in range(20):
            # 各リクエストでユニークなデータを使用
            test_data = contact_data.copy()
            test_data["email"] = f"performance{i}@test.com"
            
            start_time = time.time()
            response = client.post("/api/contacts", json=test_data)
            end_time = time.time()
            
            assert response.status_code == 200
            response_times.append(end_time - start_time)
        
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        
        # 平均応答時間が2秒以下であることを確認
        assert avg_response_time < 2.0, f"平均応答時間が遅すぎます: {avg_response_time:.3f}s"
        
        # 最大応答時間が5秒以下であることを確認
        assert max_response_time < 5.0, f"最大応答時間が遅すぎます: {max_response_time:.3f}s"
        
        print(f"問い合わせフォーム - 平均応答時間: {avg_response_time:.3f}s, 最大応答時間: {max_response_time:.3f}s")
    
    def test_concurrent_requests(self):
        """同時リクエストのパフォーマンステスト"""
        def make_request():
            response = client.get("/health")
            return response.status_code == 200
        
        # 50個の同時リクエストを実行
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(make_request) for _ in range(50)]
            results = [future.result() for future in futures]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 全てのリクエストが成功することを確認
        assert all(results), "一部のリクエストが失敗しました"
        
        # 処理時間が10秒以下であることを確認
        assert total_time < 10.0, f"処理時間が遅すぎます: {total_time:.3f}s"
        
        # スループットを計算
        throughput = len(results) / total_time
        
        # スループットが10 req/s以上であることを確認
        assert throughput >= 10.0, f"スループットが低すぎます: {throughput:.2f} req/s"
        
        print(f"同時リクエスト - 処理時間: {total_time:.3f}s, スループット: {throughput:.2f} req/s")
    
    def test_api_endpoint_performance_comparison(self):
        """各APIエンドポイントのパフォーマンス比較"""
        endpoints = [
            ("/health", "ヘルスチェック"),
            ("/api/health", "APIヘルスチェック"),
            ("/api/monitoring/health", "監視ヘルスチェック"),
            ("/api/monitoring/stats", "監視統計")
        ]
        
        results = {}
        
        for endpoint, name in endpoints:
            response_times = []
            
            for _ in range(10):
                start_time = time.time()
                response = client.get(endpoint)
                end_time = time.time()
                
                if response.status_code == 200:
                    response_times.append(end_time - start_time)
            
            if response_times:
                avg_time = sum(response_times) / len(response_times)
                results[name] = avg_time
                
                # 各エンドポイントが3秒以下で応答することを確認
                assert avg_time < 3.0, f"{name}の応答時間が遅すぎます: {avg_time:.3f}s"
        
        # 結果を出力
        print("APIエンドポイント パフォーマンス比較:")
        for name, avg_time in results.items():
            print(f"  {name}: {avg_time:.3f}s")
    
    def test_stress_test_gradual_load(self):
        """段階的負荷増加ストレステスト"""
        load_levels = [10, 25, 50]  # 同時接続数
        
        for load in load_levels:
            print(f"負荷レベル {load} 同時接続でテスト中...")
            
            def make_request():
                response = client.get("/health")
                return response.status_code == 200
            
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=load) as executor:
                futures = [executor.submit(make_request) for _ in range(load)]
                results = [future.result() for future in futures]
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # 成功率を計算
            success_count = sum(1 for success in results if success)
            success_rate = success_count / len(results) * 100
            
            # 50同時接続まで正常動作することを確認
            if load <= 50:
                assert success_rate >= 95, f"負荷レベル {load} で成功率が低すぎます: {success_rate:.1f}%"
            
            # スループットを計算
            throughput = len(results) / total_time
            
            print(f"  負荷レベル {load}: 成功率 {success_rate:.1f}%, スループット {throughput:.2f} req/s")