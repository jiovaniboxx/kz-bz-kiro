#!/bin/bash

# English Cafe Website - Frontend Test Script
echo "🎨 English Cafe Website - Frontend Test Script"
echo "=============================================="

BASE_URL="http://localhost:3000"

# 1. Homepage Check
echo "1. 🏠 Homepage Check"
echo "GET $BASE_URL/"
response=$(curl -s -w "Status: %{http_code}" -X GET "$BASE_URL/")
echo "Response status: $(echo $response | tail -c 4)"
echo ""

# 2. Contact Page Check
echo "2. 📞 Contact Page Check"
echo "GET $BASE_URL/contact"
response=$(curl -s -w "Status: %{http_code}" -X GET "$BASE_URL/contact")
echo "Response status: $(echo $response | tail -c 4)"
echo ""

# 3. Teachers Page Check
echo "3. 👨‍🏫 Teachers Page Check"
echo "GET $BASE_URL/teachers"
response=$(curl -s -w "Status: %{http_code}" -X GET "$BASE_URL/teachers")
echo "Response status: $(echo $response | tail -c 4)"
echo ""

# 4. Lessons Page Check
echo "4. 📚 Lessons Page Check"
echo "GET $BASE_URL/lessons"
response=$(curl -s -w "Status: %{http_code}" -X GET "$BASE_URL/lessons")
echo "Response status: $(echo $response | tail -c 4)"
echo ""

# 5. Security Headers Check
echo "5. 🔒 Security Headers Check"
echo "Checking frontend security headers..."
curl -s -I "$BASE_URL/" | grep -E "(X-|Content-Security|Strict-Transport)"
echo ""

# 6. Static Assets Check
echo "6. 📦 Static Assets Check"
echo "Checking if static assets are served..."
curl -s -w "Status: %{http_code}\n" -X GET "$BASE_URL/_next/static/" > /dev/null
echo ""

# 7. API Proxy Check
echo "7. 🔄 API Proxy Check"
echo "Testing API proxy through frontend..."
curl -s -w "Status: %{http_code}\n" -X GET "$BASE_URL/api/health" > /dev/null
echo ""

echo "✅ Frontend tests completed!"
echo ""
echo "💡 Tips:"
echo "  - Check logs: docker-compose logs frontend"
echo "  - View website: http://localhost:3000"
echo "  - Check build: docker-compose exec frontend npm run build"