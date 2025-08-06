@echo off
REM MedReserve AI Chatbot Startup Script for Windows

echo 🤖 Starting MedReserve AI Chatbot System...

REM Check if .env file exists
if not exist ".env" (
    echo ❌ .env file not found. Please copy .env.example to .env and configure it.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo 📦 Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Start the application
echo 🚀 Starting FastAPI server...
python main.py

echo 🛑 Chatbot system stopped.
pause
