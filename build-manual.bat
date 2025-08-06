@echo off
REM Simple manual Docker build for MedReserve AI Chatbot

echo 🚀 MedReserve AI Chatbot - Manual Docker Build
echo ===============================================

REM Check if Docker is running
echo 🔍 Checking Docker status...
docker info >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Docker is not running!
    echo 💡 Please start Docker Desktop and try again.
    echo.
    echo Steps to start Docker Desktop:
    echo 1. Press Windows + R
    echo 2. Type "Docker Desktop" and press Enter
    echo 3. Wait for Docker to fully start ^(whale icon stable in system tray^)
    echo 4. Run this script again
    pause
    exit /b 1
)

echo ✅ Docker is running!

REM Build the image
echo 🔨 Building Docker image...
docker build -t medreserve-chatbot:latest .

if %ERRORLEVEL% neq 0 (
    echo ❌ Docker build failed!
    echo.
    echo 🔍 Common issues and solutions:
    echo 1. Missing dependencies - check requirements.txt
    echo 2. Network issues - check internet connection
    echo 3. Dockerfile syntax errors - review Dockerfile
    echo.
    pause
    exit /b 1
)

echo ✅ Docker image built successfully!

REM Test the critical imports
echo 🧪 Testing PyJWT import...
docker run --rm medreserve-chatbot:latest python -c "import jwt; print('✅ PyJWT working!')"

if %ERRORLEVEL% neq 0 (
    echo ❌ PyJWT import test failed!
    pause
    exit /b 1
)

echo ✅ PyJWT import test passed!

REM Quick container test
echo 🚀 Testing container startup...
docker run -d --name test-chatbot -p 8001:8001 medreserve-chatbot:latest

REM Wait a moment
timeout /t 5 /nobreak >nul

REM Check if container is running
docker ps | findstr test-chatbot >nul
if %ERRORLEVEL% equ 0 (
    echo ✅ Container started successfully!
    docker logs test-chatbot
    docker stop test-chatbot
    docker rm test-chatbot
) else (
    echo ❌ Container failed to start!
    docker logs test-chatbot
    docker rm test-chatbot
    exit /b 1
)

echo.
echo 🎉 Build and test completed successfully!
echo 📦 Image ready: medreserve-chatbot:latest
echo.
echo 💡 To run the container:
echo    docker run -p 8001:8001 medreserve-chatbot:latest
echo.
pause
