FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install wheel for better package compilation
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements and install Python dependencies
COPY requirements.txt .

# Install dependencies with verbose output for debugging
RUN pip install --no-cache-dir --verbose -r requirements.txt

# Verify critical packages are installed
RUN python -c "import jwt; print('✅ PyJWT installed successfully')" && \
    python -c "import jose; print('✅ python-jose installed successfully')" && \
    python -c "import fastapi; print('✅ FastAPI installed successfully')"

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs uploads data models

# Create non-root user for security
RUN useradd -m -u 1000 chatbot && chown -R chatbot:chatbot /app
USER chatbot

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Run the application
CMD ["python", "main.py"]
