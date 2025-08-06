#!/bin/bash
# MedReserve AI Chatbot Startup Script

echo "🤖 Starting MedReserve AI Chatbot System..."

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please copy .env.example to .env and configure it."
    exit 1
fi

# Start the application
echo "🚀 Starting FastAPI server..."
python main.py

echo "🛑 Chatbot system stopped."
