# 🤖 MedReserve AI Chatbot System

A comprehensive dual chatbot system for the MedReserve AI healthcare platform, providing intelligent assistance for both patients and doctors with real-time communication capabilities.

## 🎯 Overview

This FastAPI-based chatbot system provides two specialized AI assistants:

### 🩺 Patient Chatbot
- **Appointment Management**: Book, view, cancel, and reschedule appointments via natural language
- **Medical Information**: Access prescriptions, medical reports, and doctor information
- **Real-time Communication**: Secure chat with assigned doctors
- **Emergency Support**: Immediate assistance for urgent medical situations

### 👨‍⚕️ Doctor Chatbot
- **Schedule Management**: View appointments and manage availability
- **Patient Care**: Access patient lists, medical histories, and treatment records
- **Clinical Documentation**: Add prescriptions and diagnoses via chat interface
- **Real-time Communication**: Secure messaging with patients
- **Emergency Alerts**: Immediate notifications for critical patient situations

## 🏗️ Architecture

```
backend/chatbot/
├── main.py                 # FastAPI application entry point
├── config.py              # Configuration settings
├── utils.py               # JWT handling and API client utilities
├── patient_chatbot.py     # Patient chatbot logic
├── doctor_chatbot.py      # Doctor chatbot logic
├── realtime_chat.py       # WebSocket chat management
├── chat_router.py         # FastAPI routes and WebSocket endpoints
├── requirements.txt       # Python dependencies
├── setup.py              # Setup and installation script
├── .env.example          # Environment configuration template
└── README.md             # This documentation
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL database
- Redis (optional, for caching)
- Spring Boot backend running

### Installation

1. **Clone and Setup**
   ```bash
   cd backend/chatbot
   python setup.py
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the System**
   ```bash
   python main.py
   # or
   ./start.sh
   ```

The chatbot system will be available at:
- **API**: http://localhost:8001
- **Documentation**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health

## 📡 API Endpoints

### REST API Endpoints

#### Patient Chatbot
```http
POST /chat/patient
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "message": "I want to book an appointment with a cardiologist",
  "conversation_id": "optional_conversation_id"
}
```

#### Doctor Chatbot
```http
POST /chat/doctor
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "message": "Show me today's appointments",
  "conversation_id": "optional_conversation_id"
}
```

#### Chat Room Management
```http
POST /chat/rooms/create
{
  "doctor_id": "doctor_123",
  "patient_id": "patient_456"
}

GET /chat/rooms/{room_id}/history?limit=50
GET /chat/rooms/user/{user_id}
```

### WebSocket Connection

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8001/chat/ws/user_123?token=jwt_token');

// Send message
ws.send(JSON.stringify({
  type: 'chat_message',
  room_id: 'chat_doctor123_patient456',
  content: 'Hello, how are you feeling today?'
}));

// Handle incoming messages
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Received:', message);
};
```

## 🤖 Chatbot Capabilities

### Patient Chatbot Features

#### Appointment Booking
```
Patient: "I need to see a cardiologist next week"
Bot: "I can help you book a cardiology appointment. I found 3 cardiologists available..."
```

#### Prescription Inquiry
```
Patient: "What are my current medications?"
Bot: "📋 Your Current Prescriptions:
1. Metformin 500mg - Twice daily
2. Lisinopril 10mg - Once daily"
```

#### Emergency Detection
```
Patient: "I'm having severe chest pain"
Bot: "🚨 EMERGENCY DETECTED 🚨
For immediate medical emergencies:
🆘 Call Emergency Services: 911"
```

### Doctor Chatbot Features

#### Schedule Management
```
Doctor: "Show me today's schedule"
Bot: "📅 Your Appointment Schedule
🔥 Today's Appointments:
⏰ 9:00 AM - John Smith (Routine checkup)"
```

#### Prescription Management
```
Doctor: "Prescribe amoxicillin 500mg twice daily for 7 days for patient John Smith"
Bot: "✅ Prescription Added Successfully
Patient: John Smith
Medication: amoxicillin 500mg"
```

#### Patient Information
```
Doctor: "Show me patients with urgent flags"
Bot: "🚨 Emergency Patients Alert
⚠️ Jane Doe - Severe allergic reaction - Critical"
```

## 💬 Real-time Chat Features

### WebSocket Message Types

#### Chat Messages
```json
{
  "type": "chat_message",
  "room_id": "chat_doctor123_patient456",
  "sender_id": "doctor123",
  "sender_name": "Dr. Smith",
  "sender_role": "DOCTOR",
  "content": "How are you feeling today?",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

#### Typing Indicators
```json
{
  "type": "typing_indicator",
  "room_id": "chat_doctor123_patient456",
  "user_id": "patient456",
  "is_typing": true
}
```

#### File Sharing
```json
{
  "type": "file_share",
  "room_id": "chat_doctor123_patient456",
  "file_info": {
    "name": "lab_results.pdf",
    "size": 1024000,
    "type": "application/pdf",
    "url": "/uploads/files/lab_results.pdf"
  }
}
```

## 🔐 Authentication & Security

### JWT Authentication
All endpoints require JWT authentication with appropriate role permissions:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Role-Based Access Control
- **PATIENT**: Access to patient chatbot and patient-doctor chat rooms
- **DOCTOR**: Access to doctor chatbot and all assigned patient communications
- **ADMIN**: Full system access and management capabilities

### Security Features
- JWT token validation
- Role-based endpoint access
- Input sanitization and validation
- Rate limiting
- CORS protection
- Secure WebSocket connections (WSS in production)

## 🔧 Configuration

### Environment Variables

```bash
# Application
DEBUG=true
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8001

# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/medreserve

# Spring Boot Integration
SPRING_BOOT_BASE_URL=http://localhost:8080/api

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256

# WebSocket
WEBSOCKET_PING_INTERVAL=20
WEBSOCKET_PING_TIMEOUT=10

# File Upload
MAX_FILE_SIZE=10485760  # 10MB
UPLOAD_DIRECTORY=uploads

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:8080"]
```

## 🐳 Docker Deployment

### Using Docker Compose
```bash
docker-compose up -d
```

### Manual Docker Build
```bash
docker build -t medreserve-chatbot .
docker run -p 8001:8001 medreserve-chatbot
```

## 🧪 Testing

### Health Check
```bash
curl http://localhost:8001/health
```

### API Testing
```bash
# Test patient chatbot
curl -X POST http://localhost:8001/chat/patient \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, I need help booking an appointment"}'

# Test doctor chatbot
curl -X POST http://localhost:8001/chat/doctor \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me today'\''s appointments"}'
```

### WebSocket Testing
Use a WebSocket client to test real-time features:
```
ws://localhost:8001/chat/ws/user_123?token=YOUR_JWT_TOKEN
```

## 📊 Monitoring & Logging

### Health Monitoring
- **Health Check Endpoint**: `/health`
- **System Stats**: `/chat/stats` (Admin only)
- **Active Users**: `/chat/active-users`

### Logging
- Structured logging with Loguru
- Request/response logging
- Error tracking and reporting
- WebSocket connection monitoring

### Metrics
- Active WebSocket connections
- Message throughput
- Response times
- Error rates

## 🔗 Integration with Spring Boot

The chatbot system integrates seamlessly with the Spring Boot backend:

### API Communication
- Authenticated requests to Spring Boot REST APIs
- Automatic token forwarding
- Error handling and fallback responses

### Data Synchronization
- Real-time appointment updates
- Prescription synchronization
- Patient record access
- Medical report retrieval

### WebSocket Integration
- Cross-platform real-time messaging
- Notification delivery
- Status updates

## 🚀 Production Deployment

### Prerequisites
- Production database (PostgreSQL)
- Redis for caching and sessions
- Load balancer for multiple instances
- SSL certificates for HTTPS/WSS

### Configuration
```bash
# Production environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# Security
JWT_SECRET_KEY=strong-production-secret
CORS_ORIGINS=["https://medreserve.ai"]

# Performance
WEBSOCKET_PING_INTERVAL=30
RATE_LIMIT_REQUESTS=1000
```

### Scaling
- Horizontal scaling with multiple instances
- Redis for shared session storage
- Load balancing for WebSocket connections
- Database connection pooling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is part of the MedReserve AI healthcare platform.

## 🆘 Support

For issues and questions:
1. Check the health endpoint: `/health`
2. Review logs in the `logs/` directory
3. Check the API documentation: `/docs`
4. Submit an issue on GitHub

---

**Built with ❤️ for better healthcare through AI-powered communication**
