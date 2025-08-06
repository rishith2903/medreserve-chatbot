@echo off
REM Docker Status Checker for MedReserve AI Chatbot

echo 🐳 Docker Desktop Status Checker
echo ================================

:check_loop
echo 🔍 Checking Docker status...
docker info >nul 2>&1

if %ERRORLEVEL% equ 0 (
    echo ✅ Docker Desktop is running!
    echo.
    echo 🚀 Ready to build! Run one of these commands:
    echo   1. .\build-manual.bat
    echo   2. docker build -t medreserve-chatbot .
    echo   3. docker-compose up --build
    echo.
    goto :end
) else (
    echo ❌ Docker Desktop is not running yet...
    echo.
    echo 💡 If you haven't started Docker Desktop yet:
    echo   1. Press Windows + R
    echo   2. Type "Docker Desktop" and press Enter
    echo   3. Wait for the whale icon to appear in system tray
    echo.
    echo ⏳ Waiting 10 seconds before checking again...
    timeout /t 10 /nobreak >nul
    goto :check_loop
)

:end
echo 🎉 Docker is ready for deployment!
pause
