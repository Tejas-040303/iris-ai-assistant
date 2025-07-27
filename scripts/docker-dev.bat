@echo off
echo 🐳 Starting IRIS Development Environment with Docker...

:: Build and start development containers
docker-compose -f docker-compose.dev.yml up --build -d

:: Wait for services to be ready
echo ⏳ Waiting for services to start...
timeout /t 10

:: Show container status
docker-compose -f docker-compose.dev.yml ps

echo ✅ IRIS Development Environment is ready!
echo 🌐 Application: http://localhost:8000
echo 🗄️ PostgreSQL: localhost:5432
echo 📦 Redis: localhost:6379
echo.
echo 📋 Available commands:
echo   docker-compose -f docker-compose.dev.yml logs iris-app
echo   docker-compose -f docker-compose.dev.yml exec iris-app bash
echo   docker-compose -f docker-compose.dev.yml down
pause
