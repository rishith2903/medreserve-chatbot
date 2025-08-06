@echo off
REM MedReserve AI Chatbot - Docker Build and Test Script (Windows)
REM This script builds the Docker image and tests for common deployment issues

echo 🚀 MedReserve AI Chatbot - Docker Build ^& Test
echo ==============================================

REM Configuration
set IMAGE_NAME=medreserve-chatbot
set TAG=latest
set CONTAINER_NAME=medreserve-chatbot-test

echo 📋 Build Configuration:
echo   Image: %IMAGE_NAME%:%TAG%
echo   Container: %CONTAINER_NAME%
echo.

REM Step 1: Clean up any existing containers/images
echo 🧹 Cleaning up existing containers and images...
docker stop %CONTAINER_NAME% 2>nul
docker rm %CONTAINER_NAME% 2>nul
docker rmi %IMAGE_NAME%:%TAG% 2>nul

REM Step 2: Build the Docker image
echo 🔨 Building Docker image...
docker build -t %IMAGE_NAME%:%TAG% . --no-cache

if %ERRORLEVEL% neq 0 (
    echo ❌ Docker build failed!
    exit /b 1
)

echo ✅ Docker image built successfully!

REM Step 3: Test package installations
echo 🧪 Testing package installations...
docker run --rm %IMAGE_NAME%:%TAG% python -c "import sys; print('🐍 Python version:', sys.version); import jwt; print('✅ PyJWT imported successfully'); import jose; print('✅ python-jose imported successfully'); import fastapi; print('✅ FastAPI imported successfully'); import uvicorn; print('✅ Uvicorn imported successfully'); import passlib; print('✅ Passlib imported successfully'); print('🎉 All critical packages imported successfully!')"

if %ERRORLEVEL% neq 0 (
    echo ❌ Package installation test failed!
    exit /b 1
)

echo ✅ Package installation test passed!

REM Step 4: Test application startup (quick test)
echo 🚀 Testing application startup...
docker run -d --name %CONTAINER_NAME% -p 8001:8001 %IMAGE_NAME%:%TAG%

REM Wait for container to start
timeout /t 5 /nobreak >nul

REM Check if container is running
docker ps | findstr %CONTAINER_NAME% >nul
if %ERRORLEVEL% equ 0 (
    echo ✅ Container started successfully!
    
    REM Test health endpoint if available
    echo 🏥 Testing health endpoint...
    curl -f http://localhost:8001/health 2>nul
    if %ERRORLEVEL% equ 0 (
        echo ✅ Health endpoint responding!
    ) else (
        echo ⚠️  Health endpoint not responding ^(this might be normal if not implemented^)
    )
    
    REM Show container logs
    echo 📋 Container logs ^(last 20 lines^):
    docker logs --tail 20 %CONTAINER_NAME%
    
) else (
    echo ❌ Container failed to start!
    echo 📋 Container logs:
    docker logs %CONTAINER_NAME%
    exit /b 1
)

REM Step 5: Cleanup
echo 🧹 Cleaning up test container...
docker stop %CONTAINER_NAME%
docker rm %CONTAINER_NAME%

echo.
echo 🎉 Docker build and test completed successfully!
echo 📦 Image ready: %IMAGE_NAME%:%TAG%
echo.
echo 💡 Next steps:
echo   1. Run: docker run -p 8001:8001 %IMAGE_NAME%:%TAG%
echo   2. Test: curl http://localhost:8001/health
echo   3. Deploy to your preferred platform

pause
