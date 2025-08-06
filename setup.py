#!/usr/bin/env python3
"""
Setup script for MedReserve AI Chatbot System
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def print_banner():
    """Print setup banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                🤖 MedReserve AI Chatbot System               ║
    ║                        Setup Script                         ║
    ║                                                              ║
    ║  🩺 Dual Chatbot System for Medical Assistance              ║
    ║  💬 Real-time Doctor-Patient Communication                  ║
    ║  🚀 FastAPI + WebSocket + JWT Authentication                ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def check_python_version():
    """Check Python version"""
    print("🐍 Checking Python version...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required, found {version.major}.{version.minor}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
    return True


def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = [
        "logs",
        "uploads",
        "uploads/files",
        "uploads/images",
        "uploads/reports",
        "data",
        "models"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  ✅ Created: {directory}")


def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing dependencies...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def setup_environment():
    """Setup environment configuration"""
    print("⚙️ Setting up environment...")
    
    env_file = ".env"
    env_example = ".env.example"
    
    if not os.path.exists(env_file):
        if os.path.exists(env_example):
            shutil.copy(env_example, env_file)
            print(f"✅ Created {env_file} from {env_example}")
            print("⚠️  Please update the configuration values in .env file")
        else:
            print(f"❌ {env_example} not found")
            return False
    else:
        print(f"✅ {env_file} already exists")
    
    return True


def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    required_modules = [
        "fastapi",
        "uvicorn",
        "websockets",
        "pydantic",
        "loguru",
        "httpx",
        "python_jose",
        "passlib"
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"❌ Failed to import: {', '.join(failed_imports)}")
        return False
    
    print("✅ All imports successful")
    return True


def create_startup_script():
    """Create startup script"""
    print("🚀 Creating startup script...")
    
    startup_script = """#!/bin/bash
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
"""
    
    with open("start.sh", "w") as f:
        f.write(startup_script)
    
    # Make executable on Unix systems
    if os.name != 'nt':
        os.chmod("start.sh", 0o755)
    
    print("✅ Created start.sh script")


def create_docker_files():
    """Create Docker configuration files"""
    print("🐳 Creating Docker files...")
    
    dockerfile = """FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs uploads data models

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8001/health || exit 1

# Run the application
CMD ["python", "main.py"]
"""
    
    docker_compose = """version: '3.8'

services:
  chatbot:
    build: .
    ports:
      - "8001:8001"
    environment:
      - DEBUG=false
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://postgres:password@db:5432/medreserve
      - REDIS_URL=redis://redis:6379/0
      - SPRING_BOOT_BASE_URL=http://backend:8080/api
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs
    depends_on:
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
"""
    
    with open("Dockerfile", "w") as f:
        f.write(dockerfile)
    
    with open("docker-compose.yml", "w") as f:
        f.write(docker_compose)
    
    print("✅ Created Dockerfile and docker-compose.yml")


def print_next_steps():
    """Print next steps for user"""
    next_steps = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                    🎉 Setup Complete! 🎉                    ║
    ╠══════════════════════════════════════════════════════════════╣
    ║                                                              ║
    ║  📋 Next Steps:                                              ║
    ║                                                              ║
    ║  1. Configure environment variables in .env file            ║
    ║     - Update database connection string                     ║
    ║     - Set JWT secret key                                    ║
    ║     - Configure Spring Boot API URL                         ║
    ║                                                              ║
    ║  2. Start the chatbot system:                               ║
    ║     python main.py                                          ║
    ║     or                                                      ║
    ║     ./start.sh                                              ║
    ║                                                              ║
    ║  3. Test the system:                                        ║
    ║     - Health check: http://localhost:8001/health            ║
    ║     - API docs: http://localhost:8001/docs                  ║
    ║     - WebSocket: ws://localhost:8001/chat/ws/{user_id}      ║
    ║                                                              ║
    ║  4. Integration:                                             ║
    ║     - Ensure Spring Boot backend is running                 ║
    ║     - Configure frontend to use chatbot endpoints           ║
    ║     - Test JWT authentication flow                          ║
    ║                                                              ║
    ║  🐳 Docker Alternative:                                      ║
    ║     docker-compose up -d                                    ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(next_steps)


def main():
    """Main setup function"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed during dependency installation")
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        print("❌ Setup failed during environment configuration")
        sys.exit(1)
    
    # Test imports
    if not test_imports():
        print("❌ Setup failed during import testing")
        sys.exit(1)
    
    # Create startup script
    create_startup_script()
    
    # Create Docker files
    create_docker_files()
    
    # Print next steps
    print_next_steps()
    
    print("✅ MedReserve AI Chatbot System setup completed successfully!")


if __name__ == "__main__":
    main()
