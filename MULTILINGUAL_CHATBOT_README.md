# 🤖 MedReserve Multilingual Chatbot Service

A comprehensive multilingual Dialogflow webhook handler integrated with the MedReserve healthcare platform, supporting English, Hindi, and Telugu languages.

## 🌟 Features

### 🌐 Multilingual Support
- **English (en)**: Primary language with full feature support
- **Hindi (hi)**: Complete Hindi language support with Devanagari script
- **Telugu (te)**: Full Telugu language support with Telugu script
- **Auto-detection**: Automatic language detection from Dialogflow requests
- **Fallback**: Graceful fallback to English for unsupported languages

### 🎯 Supported Intents
1. **BookAppointment** - Appointment booking assistance
2. **CancelAppointment** - Appointment cancellation support
3. **ListMedicines** - Medicine information and consultation guidance
4. **ConditionExplainer** - Medical condition explanations
5. **FAQ** - Frequently asked questions and help

### 🔧 Integration Points
- **Dialogflow CX/ES**: Webhook fulfillment for Google's conversational AI
- **Spring Boot Backend**: Integrated with main MedReserve backend
- **React Frontend**: Language selector and chat widget
- **RESTful APIs**: Standard REST endpoints for testing and integration

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Dialogflow    │    │  Spring Boot     │    │  React Frontend │
│   CX/ES Agent   │◄──►│  Webhook Handler │◄──►│  Language       │
│                 │    │  (Port 8080)     │    │  Selector       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Google Cloud   │    │  MedReserve      │    │  User Interface │
│  Platform       │    │  Database        │    │  Components     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### 1. Backend Setup (Spring Boot)

The chatbot webhook is integrated into the main MedReserve backend:

```bash
# Navigate to backend directory
cd backend

# Run the Spring Boot application
mvn spring-boot:run

# Webhook will be available at:
# http://localhost:8080/chatbot/webhook
```

### 2. Frontend Integration

The React frontend includes automatic language detection and switching:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Language selector will appear in bottom-right corner
```

### 3. Dialogflow Configuration

#### Create Dialogflow Agent
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project or select existing
3. Enable Dialogflow API
4. Create new Dialogflow CX or ES agent

#### Configure Languages
```yaml
Primary Language: English (en)
Additional Languages:
  - Hindi (hi)
  - Telugu (te)
```

#### Setup Webhook
```
Webhook URL: https://your-domain.com/chatbot/webhook
Method: POST
Headers: Content-Type: application/json
```

## 📡 API Endpoints

### Webhook Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chatbot/webhook` | Main Dialogflow webhook |
| POST | `/chatbot/webhook/test` | Test endpoint for manual testing |
| GET | `/chatbot/health` | Health check |

### Request/Response Examples

#### Dialogflow Webhook Request
```json
{
  "queryResult": {
    "languageCode": "hi",
    "intent": {
      "displayName": "BookAppointment"
    },
    "queryText": "मुझे डॉक्टर से मिलना है"
  }
}
```

#### Webhook Response
```json
{
  "fulfillmentText": "आपकी अपॉइंटमेंट बुक हो गई है! डॉक्टर आपसे जल्द ही मिलेंगे।"
}
```

#### Test Endpoint
```bash
# Test English response
curl -X POST "http://localhost:8080/chatbot/webhook/test?intent=BookAppointment&language=en"

# Test Hindi response  
curl -X POST "http://localhost:8080/chatbot/webhook/test?intent=BookAppointment&language=hi"

# Test Telugu response
curl -X POST "http://localhost:8080/chatbot/webhook/test?intent=BookAppointment&language=te"
```

## 🎨 Frontend Integration

### Language Selector Component

The `ChatbotLanguageSelector` component provides:
- Visual language switching interface
- Automatic preference saving
- Real-time language updates
- Native script display

```jsx
import ChatbotLanguageSelector from './components/ChatbotLanguageSelector';

// Usage in App.jsx
<ChatbotLanguageSelector />
```

### Programmatic Language Control

```javascript
import { changeChatbotLanguage, getCurrentChatbotLanguage } from './components/ChatbotLanguageSelector';

// Change language programmatically
changeChatbotLanguage('hi'); // Switch to Hindi

// Get current language
const currentLang = getCurrentChatbotLanguage(); // Returns 'en', 'hi', or 'te'
```

## 🔧 Configuration

### Backend Configuration (application.yml)

```yaml
chatbot:
  supported-languages:
    - en
    - hi  
    - te
  default-language: en
  debug-mode: false
```

### Frontend Configuration

Update `index.html` with your Dialogflow agent ID:

```html
<df-messenger
  chat-title="MedReserve AI Assistant"
  agent-id="YOUR_ACTUAL_AGENT_ID"
  language-code="en"
></df-messenger>
```

## 🧪 Testing

### Manual Testing

```bash
# Test all languages for each intent
curl -X POST "localhost:8080/chatbot/webhook/test?intent=BookAppointment&language=en"
curl -X POST "localhost:8080/chatbot/webhook/test?intent=BookAppointment&language=hi"  
curl -X POST "localhost:8080/chatbot/webhook/test?intent=BookAppointment&language=te"
```

### Health Monitoring

```bash
# Check backend health
curl http://localhost:8080/chatbot/health

# Expected response:
{
  "chatbot_service_healthy": true,
  "status": "UP",
  "timestamp": "2024-01-15T10:30:00"
}
```

## 🚀 Deployment

### Render Deployment

Update Dialogflow webhook URL to production:
```
https://your-app-name.onrender.com/chatbot/webhook
```

## 🔍 Troubleshooting

### Common Issues

1. **Language Not Switching:**
   - Check if Dialogflow messenger is loaded
   - Verify agent ID in index.html
   - Check browser console for errors

2. **Webhook Not Responding:**
   - Verify webhook URL in Dialogflow console
   - Check backend logs for errors
   - Test webhook endpoint directly

3. **Incorrect Language Responses:**
   - Verify language code format (en, hi, te)
   - Check supported languages configuration
   - Test with webhook test endpoint

### Debug Mode

Enable debug mode for detailed logging:

```yaml
chatbot:
  debug-mode: true
```

## 📞 Support

For issues and questions:
- Backend: Check Spring Boot logs and health endpoints
- Frontend: Check browser console and network requests
- Dialogflow: Use Dialogflow simulator and logs
- Integration: Test webhook endpoints directly

This multilingual chatbot service is part of the MedReserve AI healthcare platform.
