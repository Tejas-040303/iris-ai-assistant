@echo off
echo 🚀 Starting IRIS Production Environment...

:: Pull latest images and start
docker-compose up -d --build

:: Wait for services
echo ⏳ Waiting for services to initialize...
timeout /t 15

:: Show status
docker-compose ps

echo ✅ IRIS Production Environment is running!
echo 🌐 Application: http://localhost
echo 🔒 Admin Panel: http://localhost/admin
pause
