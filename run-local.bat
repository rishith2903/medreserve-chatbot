@echo off
REM Run MedReserve AI Chatbot Locally (without Docker)

echo 🚀 MedReserve AI Chatbot - Local Development Server
echo ==================================================

echo 🔍 Checking Python and dependencies...

REM Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo 💡 Please install Python 3.11+ and try again
    pause
    exit /b 1
)

echo ✅ Python is available

REM Check critical dependencies
echo 🧪 Testing critical imports...
python -c "import jwt; import fastapi; import uvicorn; print('✅ All critical packages available')" 2>nul
if %ERRORLEVEL% neq 0 (
    echo ❌ Missing dependencies. Installing...
    pip install -r requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
)

echo ✅ Dependencies are ready

REM Set environment variables for local development
set DEBUG=true
set ENVIRONMENT=development
set HOST=0.0.0.0
set PORT=8001
set JWT_SECRET_KEY=local-development-secret-key
set JWT_ALGORITHM=HS256
set JWT_EXPIRATION_HOURS=24

echo 🌟 Starting MedReserve AI Chatbot...
echo 📍 Server will be available at: http://localhost:8001
echo 🛑 Press Ctrl+C to stop the server
echo.

REM Start the application
python main.py

echo.
echo 👋 Server stopped
pause
