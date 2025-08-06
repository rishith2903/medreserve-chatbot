@echo off
REM MedReserve AI Chatbot Docker Deployment Script for Windows

echo 🐳 MedReserve AI Chatbot Docker Deployment
echo ==========================================

REM Check if Docker is running
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed or not running
    echo Please install Docker Desktop and make sure it's running
    pause
    exit /b 1
)

echo ✅ Docker is available

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  .env file not found. Creating from template...
    copy .env.example .env
    echo ✅ Created .env file from template
    echo ⚠️  Please edit .env file with your configuration before continuing
    echo Press any key to open .env file for editing...
    pause
    notepad .env
)

echo 📋 Current directory contents:
dir /b

REM Verify required files exist
if not exist "Dockerfile" (
    echo ❌ Dockerfile not found
    exit /b 1
)

if not exist "docker-compose.yml" (
    echo ❌ docker-compose.yml not found
    exit /b 1
)

if not exist "requirements.txt" (
    echo ❌ requirements.txt not found
    exit /b 1
)

echo ✅ All required files found

REM Stop any existing containers
echo 🛑 Stopping existing containers...
docker-compose down

REM Build and start services
echo 🔨 Building Docker image...
docker-compose build --no-cache

if errorlevel 1 (
    echo ❌ Docker build failed
    pause
    exit /b 1
)

echo 🚀 Starting services...
docker-compose up -d

if errorlevel 1 (
    echo ❌ Failed to start services
    pause
    exit /b 1
)

echo ✅ Services started successfully!

REM Wait a moment for services to initialize
echo ⏳ Waiting for services to initialize...
timeout /t 10 /nobreak >nul

REM Check service health
echo 🔍 Checking service health...
curl -f http://localhost:8001/health 2>nul
if errorlevel 1 (
    echo ⚠️  Health check failed, but service might still be starting...
    echo 📋 Check logs with: docker-compose logs -f chatbot
) else (
    echo ✅ Health check passed!
)

echo.
echo 🎉 Deployment completed!
echo.
echo 📊 Service URLs:
echo   - API Documentation: http://localhost:8001/docs
echo   - Health Check: http://localhost:8001/health
echo   - WebSocket: ws://localhost:8001/chat/ws/{user_id}
echo.
echo 📋 Useful commands:
echo   - View logs: docker-compose logs -f chatbot
echo   - Stop services: docker-compose down
echo   - Restart: docker-compose restart
echo.

pause
