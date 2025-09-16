#!/bin/bash

# English Cafe Website - API Test Script
echo "🧪 English Cafe Website - API Test Script"
echo "=========================================="

BASE_URL="http://localhost:8000"

# 1. Health Check
echo "1. 🏥 Health Check"
echo "GET $BASE_URL/health"
curl -s -X GET "$BASE_URL/health" | jq '.' || echo "Health check failed"
echo ""

# 2. Root Endpoint
echo "2. 🏠 Root Endpoint"
echo "GET $BASE_URL/"
curl -s -X GET "$BASE_URL/" | jq '.' || echo "Root endpoint failed"
echo ""

# 3. Create Contact (Valid Data)
echo "3. ✅ Create Contact - Valid Data"
echo "POST $BASE_URL/api/v1/contacts/"
curl -s -X POST "$BASE_URL/api/v1/contacts/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "テスト太郎",
    "email": "test@example.com",
    "phone": "090-1234-5678",
    "lesson_type": "trial",
    "preferred_contact": "email",
    "message": "体験レッスンを希望します。"
  }' | jq '.' || echo "Contact creation failed"
echo ""

# 4. Create Contact (Invalid Data)
echo "4. ❌ Create Contact - Invalid Data"
echo "POST $BASE_URL/api/v1/contacts/ (Invalid email)"
curl -s -X POST "$BASE_URL/api/v1/contacts/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "テスト花子",
    "email": "invalid-email",
    "lesson_type": "group",
    "preferred_contact": "email",
    "message": "グループレッスンに参加したいです。"
  }' | jq '.' || echo "Expected validation error"
echo ""

# 5. Create Contact (XSS Attempt)
echo "5. 🛡️ Create Contact - XSS Attempt (Should be blocked)"
echo "POST $BASE_URL/api/v1/contacts/ (XSS attempt)"
curl -s -X POST "$BASE_URL/api/v1/contacts/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "<script>alert(\"xss\")</script>",
    "email": "xss@example.com",
    "lesson_type": "trial",
    "preferred_contact": "email",
    "message": "XSS test message"
  }' | jq '.' || echo "XSS attempt blocked (expected)"
echo ""

# 6. Rate Limit Test
echo "6. 🚦 Rate Limit Test"
echo "Making multiple requests to test rate limiting..."
for i in {1..5}; do
  echo "Request $i:"
  curl -s -w "Status: %{http_code}\n" -X GET "$BASE_URL/health" > /dev/null
  sleep 0.1
done
echo ""

# 7. Security Headers Check
echo "7. 🔒 Security Headers Check"
echo "Checking security headers..."
curl -s -I "$BASE_URL/health" | grep -E "(X-|Content-Security|Strict-Transport)"
echo ""

# 8. API Documentation
echo "8. 📚 API Documentation"
echo "GET $BASE_URL/docs"
curl -s -w "Status: %{http_code}\n" -X GET "$BASE_URL/docs" > /dev/null
echo ""

echo "✅ API tests completed!"
echo ""
echo "💡 Tips:"
echo "  - Check logs: docker-compose logs backend"
echo "  - View API docs: http://localhost:8000/docs"
echo "  - Monitor database: docker-compose exec postgres psql -U postgres -d english_cafe_db"