#!/bin/bash
# Docker launcher for all microservices

echo "=========================================="
echo "Analytics Microservices Docker Startup"
echo "=========================================="

# Ensure .env exists
if [ ! -f .env ]; then
    echo "WARNING: .env file not found."
    echo "Copying env.example to .env..."
    cp env.example .env
    echo "IMPORTANT: Edit .env and set your OPENAI_API_KEY."
    echo ""
fi

# Stop existing containers
echo "Stopping existing containers..."
docker-compose down

# Build images
echo ""
echo "Building Docker images..."
docker-compose build --no-cache

# Start containers
echo ""
echo "Starting containers..."
docker-compose up -d

# Wait for initialization
echo ""
echo "Waiting for services to initialize (40 seconds)..."
sleep 40

# Status
echo ""
echo "=========================================="
echo "Container status:"
echo "=========================================="
docker-compose ps

echo ""
echo "=========================================="
echo "Service health checks:"
echo "=========================================="
curl -s http://localhost:8001/ | python -m json.tool 2>/dev/null || echo "SEO Service (8001) - unavailable"
echo ""
curl -s http://localhost:8002/ | python -m json.tool 2>/dev/null || echo "Text Service (8002) - unavailable"
echo ""
curl -s http://localhost:8003/ | python -m json.tool 2>/dev/null || echo "Convenience Service (8003) - unavailable"
echo ""
curl -s http://localhost:8004/ | python -m json.tool 2>/dev/null || echo "Senior Service (8004) - unavailable"

echo ""
echo "=========================================="
echo "Container logs:"
echo "=========================================="
echo "To follow logs:"
echo "  docker-compose logs -f [service-name]"
echo ""
echo "Available services:"
echo "  - seo-service"
echo "  - text-service"
echo "  - convenience-service"
echo "  - senior-service"
echo ""
echo "To stop: docker-compose down"
echo "=========================================="
