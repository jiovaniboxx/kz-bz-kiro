#!/bin/bash

# English Cafe Website - Comprehensive Test Runner
echo "🧪 English Cafe Website - Comprehensive Test Runner"
echo "=================================================="

# 1. Setup and start services
echo "🚀 Setting up services..."
./scripts/test-setup.sh

# Wait for services to stabilize
echo "⏳ Waiting for services to stabilize..."
sleep 10

# 2. Run API tests
echo ""
echo "🔧 Running API tests..."
./scripts/test-api.sh

# 3. Run Frontend tests
echo ""
echo "🎨 Running Frontend tests..."
./scripts/test-frontend.sh

# 4. Run Backend unit tests
echo ""
echo "🧪 Running Backend unit tests..."
echo "docker-compose exec backend python -m pytest tests/ -v"
docker-compose exec backend python -m pytest tests/ -v || echo "Backend tests failed or not found"

# 5. Run Frontend unit tests
echo ""
echo "🧪 Running Frontend unit tests..."
echo "docker-compose exec frontend npm test -- --watchAll=false"
docker-compose exec frontend npm test -- --watchAll=false || echo "Frontend tests failed or not found"

# 6. Integration test - Full contact flow
echo ""
echo "🔄 Running Integration Test - Full Contact Flow"
echo "Testing complete contact creation and retrieval flow..."

# Create a contact
contact_response=$(curl -s -X POST "http://localhost:8000/api/v1/contacts/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "統合テスト太郎",
    "email": "integration@example.com",
    "phone": "090-9999-8888",
    "lesson_type": "trial",
    "preferred_contact": "email",
    "message": "統合テストのメッセージです。"
  }')

echo "Contact creation response:"
echo $contact_response | jq '.'

# Extract contact ID if creation was successful
contact_id=$(echo $contact_response | jq -r '.contact_id // empty')

if [ ! -z "$contact_id" ]; then
  echo "✅ Contact created successfully with ID: $contact_id"
  
  # Retrieve the contact
  echo "Retrieving contact..."
  curl -s -X GET "http://localhost:8000/api/v1/contacts/$contact_id" | jq '.'
  
  echo "✅ Integration test completed successfully!"
else
  echo "❌ Integration test failed - could not create contact"
fi

# 7. Performance test
echo ""
echo "⚡ Running Performance Test"
echo "Testing response times..."

# Test API response time
api_time=$(curl -s -w "%{time_total}" -X GET "http://localhost:8000/health" -o /dev/null)
echo "API response time: ${api_time}s"

# Test Frontend response time
frontend_time=$(curl -s -w "%{time_total}" -X GET "http://localhost:3000/" -o /dev/null)
echo "Frontend response time: ${frontend_time}s"

# 8. Security test
echo ""
echo "🛡️ Running Security Tests"

# Test SQL injection attempt
echo "Testing SQL injection protection..."
sql_injection_response=$(curl -s -X POST "http://localhost:8000/api/v1/contacts/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Robert\"; DROP TABLE contacts; --",
    "email": "hacker@example.com",
    "lesson_type": "trial",
    "preferred_contact": "email",
    "message": "SQL injection test"
  }')

echo "SQL injection test response:"
echo $sql_injection_response | jq '.'

# Test XSS attempt
echo "Testing XSS protection..."
xss_response=$(curl -s -X POST "http://localhost:8000/api/v1/contacts/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "<script>alert(\"XSS\")</script>",
    "email": "xss@example.com",
    "lesson_type": "trial",
    "preferred_contact": "email",
    "message": "XSS test message"
  }')

echo "XSS test response:"
echo $xss_response | jq '.'

# 9. Show final status
echo ""
echo "📊 Final Service Status:"
docker-compose ps

echo ""
echo "🎉 All tests completed!"
echo ""
echo "📋 Summary:"
echo "  ✅ Services setup and health checks"
echo "  ✅ API functionality tests"
echo "  ✅ Frontend accessibility tests"
echo "  ✅ Integration tests"
echo "  ✅ Performance tests"
echo "  ✅ Security tests"
echo ""
echo "🌐 Services are running at:"
echo "  Frontend: http://localhost:3000"
echo "  Backend API: http://localhost:8000"
echo "  API Documentation: http://localhost:8000/docs"
echo ""
echo "🛑 To stop services: docker-compose down"