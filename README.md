# 🤖 MedReserve — Chatbot Service (FastAPI)

See overall architecture diagram: [../../docs/architecture.mmd](../../docs/architecture.mmd)

Dual AI assistants for Patients and Doctors with real-time chat via WebSocket.

Runs on http://localhost:8001 by default.

## 🚀 Quickstart

OS-specific quick reference: see the root README section “OS-specific instructions”.
```
cd backend/chatbot
pip install -r requirements.txt
python main.py
```

Docs: http://localhost:8001/docs  |  Health: http://localhost:8001/health

## 📡 REST Endpoints
- POST /chat/patient  (Authorization: Bearer <jwt>)
- POST /chat/doctor   (Authorization: Bearer <jwt>)
- POST /chat/rooms/create

Request (example)
```
{
  "message": "I want to book an appointment with a cardiologist",
  "conversation_id": "optional"
}
```

## 🔌 WebSocket
- ws://localhost:8001/chat/ws/{user_id}?token=<jwt>

Example
```
const ws = new WebSocket('ws://localhost:8001/chat/ws/user_123?token=JWT');
ws.onmessage = (e) => console.log(JSON.parse(e.data));
ws.send(JSON.stringify({ type: 'chat_message', room_id: 'room1', content: 'Hello' }));
```

## 🔧 Configuration (.env example — no secrets)
```
PORT=8001
SPRING_BOOT_BASE_URL=http://localhost:8080/api
JWT_SECRET_KEY=<strong-secret>
CORS_ORIGINS=["http://localhost:3000"]
```

## 🧪 Testing
```
# Health
curl http://localhost:8001/health

# Patient chat
curl -X POST http://localhost:8001/chat/patient \
  -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" \
  -d '{"message":"Hello"}'
```

## 🐳 Docker (service-only)
```
docker build -t medreserve-chatbot .
docker run -p 8001:8001 medreserve-chatbot
```

Tip: Prefer running all services with a root docker-compose (ask me to create it).

## 🌐 Production
- Example Chatbot URL: https://medreserve-chatbot.onrender.com (update if different)

## 🔒 Notes
- JWT required; role-based checks enforced
- Use WSS/HTTPS in production
