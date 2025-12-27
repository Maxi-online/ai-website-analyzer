@echo off
REM Docker launcher for all microservices (Windows)

echo ==========================================
echo Analytics Microservices Docker Startup
echo ==========================================

REM Ensure .env exists
if not exist .env (
    echo WARNING: .env file not found!
    echo Copying env.example to .env...
    copy env.example .env
    echo IMPORTANT: Edit .env and set your OPENAI_API_KEY!
    echo.
)

REM Stop existing containers
echo Stopping existing containers...
docker-compose down

REM Build images
echo.
echo Building Docker images...
docker-compose build --no-cache

REM Start containers
echo.
echo Starting containers...
docker-compose up -d

REM Wait for initialization
echo.
echo Waiting for services to initialize (40 seconds)...
timeout /t 40 /nobreak

REM Status
echo.
echo ==========================================
echo Container status:
echo ==========================================
docker-compose ps

echo.
echo ==========================================
echo Service health checks:
echo ==========================================
curl -s http://localhost:8001/
echo.
curl -s http://localhost:8002/
echo.
curl -s http://localhost:8003/
echo.
curl -s http://localhost:8004/

echo.
echo ==========================================
echo Container logs:
echo ==========================================
echo To follow logs:
echo   docker-compose logs -f [service-name]
echo.
echo Available services:
echo   - seo-service
echo   - text-service
echo   - convenience-service
echo   - senior-service
echo.
echo To stop: docker-compose down
echo ==========================================
pause
