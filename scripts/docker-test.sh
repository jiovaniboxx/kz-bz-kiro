#!/bin/bash

# Docker Compose動作確認スクリプト

set -e

echo "🚀 English Cafe Docker Compose 動作確認を開始します..."

# 環境をクリーンアップ
echo "📦 既存のコンテナとボリュームをクリーンアップ..."
docker-compose down -v --remove-orphans

# イメージをビルド
echo "🔨 Dockerイメージをビルド中..."
docker-compose build --no-cache

# サービスを起動
echo "🚀 サービスを起動中..."
docker-compose up -d

# サービスの起動を待機
echo "⏳ サービスの起動を待機中..."
sleep 30

# ヘルスチェック
echo "🏥 ヘルスチェックを実行中..."

# PostgreSQLの接続確認
echo "  📊 PostgreSQL接続確認..."
if docker-compose exec -T postgres pg_isready -U postgres; then
    echo "  ✅ PostgreSQL: OK"
else
    echo "  ❌ PostgreSQL: NG"
    exit 1
fi

# バックエンドAPIの確認
echo "  🔧 バックエンドAPI確認..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "  ✅ Backend API: OK"
    curl -s http://localhost:8000/health | jq .
else
    echo "  ❌ Backend API: NG"
    echo "  📋 バックエンドログを確認:"
    docker-compose logs backend | tail -20
    exit 1
fi

# フロントエンドの確認
echo "  🎨 フロントエンド確認..."
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "  ✅ Frontend: OK"
else
    echo "  ❌ Frontend: NG"
    echo "  📋 フロントエンドログを確認:"
    docker-compose logs frontend | tail -20
    exit 1
fi

# API機能テスト
echo "🧪 API機能テストを実行中..."

# 問い合わせ作成テスト
echo "  📝 問い合わせ作成テスト..."
CONTACT_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/contacts/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "テスト太郎",
    "email": "test@example.com",
    "phone": "090-1234-5678",
    "lesson_type": "trial",
    "preferred_contact": "email",
    "message": "Docker動作確認テストです"
  }')

if echo "$CONTACT_RESPONSE" | jq -e '.contact_id' > /dev/null; then
    CONTACT_ID=$(echo "$CONTACT_RESPONSE" | jq -r '.contact_id')
    echo "  ✅ 問い合わせ作成: OK (ID: $CONTACT_ID)"
else
    echo "  ❌ 問い合わせ作成: NG"
    echo "  Response: $CONTACT_RESPONSE"
    exit 1
fi

# 問い合わせ取得テスト
echo "  📖 問い合わせ取得テスト..."
GET_RESPONSE=$(curl -s http://localhost:8000/api/v1/contacts/$CONTACT_ID)

if echo "$GET_RESPONSE" | jq -e '.id' > /dev/null; then
    echo "  ✅ 問い合わせ取得: OK"
    echo "  取得データ: $(echo "$GET_RESPONSE" | jq -c '{name: .name, email: .email, status: .status}')"
else
    echo "  ❌ 問い合わせ取得: NG"
    echo "  Response: $GET_RESPONSE"
    exit 1
fi

# セキュリティヘッダーテスト
echo "🔒 セキュリティヘッダーテスト..."
SECURITY_HEADERS=$(curl -s -I http://localhost:8000/health)

if echo "$SECURITY_HEADERS" | grep -q "x-content-type-options"; then
    echo "  ✅ セキュリティヘッダー: OK"
else
    echo "  ⚠️  セキュリティヘッダー: 一部未設定"
fi

# フロントエンドのセキュリティヘッダーテスト
FRONTEND_HEADERS=$(curl -s -I http://localhost:3000)
if echo "$FRONTEND_HEADERS" | grep -q "x-frame-options"; then
    echo "  ✅ フロントエンドセキュリティヘッダー: OK"
else
    echo "  ⚠️  フロントエンドセキュリティヘッダー: 一部未設定"
fi

# パフォーマンステスト
echo "⚡ 基本パフォーマンステスト..."
RESPONSE_TIME=$(curl -o /dev/null -s -w '%{time_total}' http://localhost:8000/health)
echo "  🕐 API応答時間: ${RESPONSE_TIME}秒"

if (( $(echo "$RESPONSE_TIME < 2.0" | bc -l) )); then
    echo "  ✅ パフォーマンス: OK"
else
    echo "  ⚠️  パフォーマンス: 応答が遅い可能性があります"
fi

# ログ出力
echo "📋 最新のログを確認..."
echo "--- Backend Logs ---"
docker-compose logs --tail=10 backend

echo "--- Frontend Logs ---"
docker-compose logs --tail=10 frontend

echo "--- Database Logs ---"
docker-compose logs --tail=5 postgres

echo ""
echo "🎉 Docker Compose動作確認が完了しました！"
echo ""
echo "📊 サービス状況:"
echo "  - Frontend: http://localhost:3000"
echo "  - Backend API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - Database: localhost:5432"
echo ""
echo "🛑 停止するには: docker-compose down"
echo "📋 ログ確認: docker-compose logs [service-name]"
echo ""