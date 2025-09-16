#!/bin/bash

# English Cafe Website - Docker Compose Test Setup
echo "🚀 English Cafe Website - Docker Compose Test Setup"
echo "=================================================="

# 1. Clean up any existing containers
echo "📦 Cleaning up existing containers..."
docker-compose down -v
docker system prune -f

# 2. Build and start services
echo "🔨 Building and starting services..."
docker-compose up --build -d

# 3. Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# 4. Check service health
echo "🏥 Checking service health..."

# Check PostgreSQL
echo "Checking PostgreSQL..."
docker-compose exec postgres pg_isready -U postgres

# Check Backend
echo "Checking Backend API..."
curl -f http://localhost:8000/health || echo "Backend health check failed"

# Check Frontend
echo "Checking Frontend..."
curl -f http://localhost:3000 || echo "Frontend health check failed"

# 5. Run database migrations
echo "🗄️ Running database migrations..."
docker-compose exec backend alembic upgrade head

# 6. Show service status
echo "📊 Service Status:"
docker-compose ps

# 7. Show logs
echo "📝 Recent logs:"
echo "Backend logs:"
docker-compose logs --tail=10 backend

echo "Frontend logs:"
docker-compose logs --tail=10 frontend

echo "✅ Setup complete!"
echo ""
echo "🌐 Services are available at:"
echo "  Frontend: http://localhost:3000"
echo "  Backend API: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo "  PostgreSQL: localhost:5432"
echo ""
echo "🔧 Useful commands:"
echo "  View logs: docker-compose logs -f [service]"
echo "  Stop services: docker-compose down"
echo "  Restart service: docker-compose restart [service]"