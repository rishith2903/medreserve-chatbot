# 🤖 MedReserve AI - Chatbot Service

[![Java](https://img.shields.io/badge/Java-17-orange.svg)](https://openjdk.java.net/projects/jdk/17/)
[![Spring Boot](https://img.shields.io/badge/Spring%20Boot-3.2.0-brightgreen.svg)](https://spring.io/projects/spring-boot)
[![Dialogflow](https://img.shields.io/badge/Dialogflow-CX-blue.svg)](https://cloud.google.com/dialogflow)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com/)

A comprehensive multilingual chatbot service for the MedReserve AI platform, providing intelligent healthcare assistance through natural language processing and integration with Google Dialogflow.

## 🌟 Features

### 🗣️ Multilingual Support
- **English** - Primary language with comprehensive medical vocabulary
- **Hindi** - Native language support with medical terminology
- **Telugu** - Regional language support for local patients
- **Language Detection** - Automatic language identification
- **Dynamic Language Switching** - Real-time language change support

### 🤖 Conversational AI
- **Natural Language Understanding** with Dialogflow CX
- **Intent Recognition** for healthcare-specific queries
- **Entity Extraction** for medical terms and symptoms
- **Context Management** for multi-turn conversations
- **Fallback Handling** for unrecognized queries

### 🏥 Healthcare Features
- **Symptom Assessment** - Initial symptom evaluation and guidance
- **Appointment Booking** - Voice/text-based appointment scheduling
- **Medical Information** - General health information and advice
- **Emergency Detection** - Identification of urgent medical situations
- **Health Tips** - Personalized health recommendations

### 🔗 Integration Capabilities
- **Dialogflow Webhook** - Real-time response processing
- **Backend API Integration** - Seamless data exchange
- **ML Service Integration** - AI-powered health insights
- **User Context Awareness** - Personalized responses based on user data
- **Session Management** - Conversation state persistence

### 📊 Analytics & Monitoring
- **Conversation Analytics** - User interaction insights
- **Intent Performance** - Recognition accuracy metrics
- **Language Usage Statistics** - Multilingual usage patterns
- **Response Time Monitoring** - Performance optimization
- **Error Tracking** - Issue identification and resolution

## 🏗️ Tech Stack

- **Framework**: Spring Boot 3.2.0 with Java 17
- **AI Platform**: Google Dialogflow CX for NLP
- **Web Framework**: Spring WebMVC for REST APIs
- **Configuration**: Spring Boot Configuration Properties
- **Validation**: Spring Validation with custom validators
- **Testing**: JUnit 5, Spring Boot Test, Mockito
- **Build Tool**: Maven 3.9+ for dependency management
- **Deployment**: Docker, Render Platform
- **Monitoring**: Spring Boot Actuator, Micrometer
- **Logging**: SLF4J with Logback for structured logging

## 📋 Prerequisites

- **Java 17+** (OpenJDK recommended)
- **Maven 3.9+** for dependency management
- **Google Cloud Account** for Dialogflow access
- **Dialogflow CX Project** with configured agents
- **Docker** (optional, for containerized deployment)
- **Git** for version control

## 🚀 Quick Start

### 1. Clone and Navigate
```bash
git clone <repository-url>
cd MedReserve/backend/chatbot
```

### 2. Google Cloud Setup

#### Create Dialogflow Project
```bash
# Install Google Cloud CLI
# Visit: https://cloud.google.com/sdk/docs/install

# Authenticate with Google Cloud
gcloud auth login

# Create new project (optional)
gcloud projects create medreserve-chatbot

# Set project
gcloud config set project medreserve-chatbot

# Enable Dialogflow API
gcloud services enable dialogflow.googleapis.com
```

#### Create Service Account
```bash
# Create service account
gcloud iam service-accounts create medreserve-chatbot \
    --description="MedReserve Chatbot Service Account" \
    --display-name="MedReserve Chatbot"

# Grant necessary permissions
gcloud projects add-iam-policy-binding medreserve-chatbot \
    --member="serviceAccount:medreserve-chatbot@medreserve-chatbot.iam.gserviceaccount.com" \
    --role="roles/dialogflow.admin"

# Create and download key
gcloud iam service-accounts keys create credentials.json \
    --iam-account=medreserve-chatbot@medreserve-chatbot.iam.gserviceaccount.com
```

### 3. Environment Configuration
Create environment configuration:
```bash
# Copy example environment file
cp .env.example .env
```

Configure environment variables in `.env`:
```env
# Server Configuration
SERVER_PORT=8002
SERVER_SERVLET_CONTEXT_PATH=/

# Dialogflow Configuration
GOOGLE_APPLICATION_CREDENTIALS=./credentials.json
DIALOGFLOW_PROJECT_ID=medreserve-chatbot
DIALOGFLOW_LOCATION=global
DIALOGFLOW_AGENT_ID=your-agent-id

# Supported Languages
CHATBOT_SUPPORTED_LANGUAGES=en,hi,te
CHATBOT_DEFAULT_LANGUAGE=en

# API Integration
BACKEND_API_URL=http://localhost:8080
ML_SERVICE_URL=http://localhost:8001

# Security Configuration
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
API_KEY_ENABLED=false
API_KEY=your_api_key_here

# Logging Configuration
LOGGING_LEVEL_ROOT=INFO
LOGGING_LEVEL_CHATBOT=DEBUG
LOGGING_FILE=./logs/chatbot.log

# Performance Configuration
SESSION_TIMEOUT=1800
MAX_CONVERSATION_TURNS=50
RESPONSE_TIMEOUT=10000
```

### 4. Dialogflow Agent Setup

#### Create Intents
```bash
# Use Dialogflow Console or CLI to create intents:
# - greeting
# - symptom_check
# - appointment_booking
# - medical_information
# - emergency_help
# - goodbye
```

#### Configure Entities
```bash
# Create entities for:
# - @symptoms (fever, cough, headache, etc.)
# - @body_parts (head, chest, stomach, etc.)
# - @time_periods (today, tomorrow, next week, etc.)
# - @specialties (cardiology, neurology, etc.)
```

### 5. Build and Run
```bash
# Clean and compile
mvn clean compile

# Run tests
mvn test

# Start application (development mode)
mvn spring-boot:run

# Or start with specific profile
mvn spring-boot:run -Dspring-boot.run.profiles=dev

# Build JAR for production
mvn clean package -DskipTests
java -jar target/medreserve-chatbot-1.0.0.jar
```

### 6. Verify Installation
```bash
# Health check
curl http://localhost:8002/actuator/health

# Test webhook endpoint
curl -X POST "http://localhost:8002/webhook" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionInfo": {
      "session": "test-session"
    },
    "text": "Hello",
    "languageCode": "en"
  }'

# Test chat endpoint
curl -X POST "http://localhost:8002/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I have a headache",
    "language": "en",
    "sessionId": "test-session"
  }'
```

## 🔗 API Endpoints

### Chatbot Interaction
```http
POST   /webhook             # Dialogflow webhook endpoint
POST   /chat                # Direct chat interface
POST   /chat/session        # Start new chat session
DELETE /chat/session/{id}   # End chat session
GET    /chat/history/{id}   # Get conversation history
```

### Language Management
```http
GET    /languages           # Get supported languages
POST   /languages/detect    # Detect message language
POST   /languages/translate # Translate message
GET    /languages/current   # Get current session language
PUT    /languages/switch    # Switch session language
```

### Health and Monitoring
```http
GET    /actuator/health     # Service health check
GET    /actuator/info       # Service information
GET    /actuator/metrics    # Performance metrics
GET    /status              # Detailed service status
```

### Analytics
```http
GET    /analytics/conversations  # Conversation statistics
GET    /analytics/intents       # Intent usage analytics
GET    /analytics/languages     # Language usage statistics
GET    /analytics/performance   # Response time metrics
```

## 📊 API Usage Examples

### Direct Chat
```python
import requests

# Send message to chatbot
response = requests.post(
    "http://localhost:8002/chat",
    json={
        "message": "I have been having headaches for 3 days",
        "language": "en",
        "sessionId": "user-123",
        "userId": "patient-456"
    }
)

chat_response = response.json()
print(f"Bot response: {chat_response['response']}")
print(f"Intent: {chat_response['intent']}")
print(f"Confidence: {chat_response['confidence']}")
```

### Multilingual Chat
```python
# Chat in Hindi
response = requests.post(
    "http://localhost:8002/chat",
    json={
        "message": "मुझे सिरदर्द है",
        "language": "hi",
        "sessionId": "user-123"
    }
)

# Chat in Telugu
response = requests.post(
    "http://localhost:8002/chat",
    json={
        "message": "నాకు తలనొప్పి ఉంది",
        "language": "te",
        "sessionId": "user-123"
    }
)
```

### Language Detection
```python
# Detect language of message
response = requests.post(
    "http://localhost:8002/languages/detect",
    json={
        "message": "मुझे डॉक्टर से मिलना है"
    }
)

detection = response.json()
print(f"Detected language: {detection['language']}")
print(f"Confidence: {detection['confidence']}")
```

### Conversation History
```python
# Get conversation history
response = requests.get(
    "http://localhost:8002/chat/history/user-123"
)

history = response.json()
for turn in history['conversation']:
    print(f"User: {turn['user_message']}")
    print(f"Bot: {turn['bot_response']}")
    print(f"Time: {turn['timestamp']}")
```

## 🧪 Testing

### Unit Tests
```bash
# Run all tests
mvn test

# Run specific test class
mvn test -Dtest=ChatbotControllerTest

# Run tests with coverage
mvn test jacoco:report

# Run tests with specific profile
mvn test -Dspring.profiles.active=test
```

### Integration Tests
```bash
# Run integration tests
mvn test -Dtest=*IntegrationTest

# Test Dialogflow integration
mvn test -Dtest=DialogflowIntegrationTest

# Test webhook functionality
mvn test -Dtest=WebhookControllerTest
```

### Manual Testing
```bash
# Test webhook with curl
curl -X POST "http://localhost:8002/webhook" \
  -H "Content-Type: application/json" \
  -d @test-data/sample-webhook-request.json

# Test multilingual support
curl -X POST "http://localhost:8002/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, I need help",
    "language": "en",
    "sessionId": "test-session"
  }'
```

## 🐳 Docker Deployment

### Build Docker Image
```bash
# Build development image
docker build -f Dockerfile.dev -t medreserve-chatbot:dev .

# Build production image
docker build -t medreserve-chatbot:prod .

# Build with specific Java version
docker build --build-arg JAVA_VERSION=17 -t medreserve-chatbot .
```

### Run with Docker
```bash
# Run development container
docker run -d \
  --name medreserve-chatbot-dev \
  -p 8002:8002 \
  -v $(pwd)/credentials.json:/app/credentials.json \
  -v $(pwd)/logs:/app/logs \
  --env-file .env \
  medreserve-chatbot:dev

# Run production container
docker run -d \
  --name medreserve-chatbot-prod \
  -p 8002:8002 \
  --env-file .env.prod \
  medreserve-chatbot:prod
```

### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'
services:
  chatbot:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8002:8002"
    environment:
      - DIALOGFLOW_PROJECT_ID=medreserve-chatbot
      - BACKEND_API_URL=http://backend:8080
      - ML_SERVICE_URL=http://ml-service:8001
    volumes:
      - ./credentials.json:/app/credentials.json:ro
      - ./logs:/app/logs
    depends_on:
      - backend
      - ml-service
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8002/actuator/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f chatbot

# Scale service
docker-compose up -d --scale chatbot=2
```
