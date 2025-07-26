from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import re
import json
import logging
from datetime import datetime
import httpx
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MedReserve AI - Chatbot Service",
    description="Intelligent chatbot for medical appointment assistance",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Models
class ChatRequest(BaseModel):
    message: str = Field(..., description="User message", min_length=1, max_length=500)
    context: Optional[Dict] = Field(None, description="Conversation context")

class ChatResponse(BaseModel):
    response: str
    intent: str
    confidence: float
    suggestions: List[str]
    actions: List[Dict]
    timestamp: datetime

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str

# Intent patterns and responses
INTENT_PATTERNS = {
    "greeting": {
        "patterns": [
            r"hello|hi|hey|good morning|good afternoon|good evening",
            r"start|begin|help me"
        ],
        "responses": [
            "Hello! I'm your MedReserve AI assistant. How can I help you today?",
            "Hi there! I'm here to help you with your medical appointments. What do you need?",
            "Welcome to MedReserve! I can help you book appointments, find doctors, or answer questions."
        ],
        "suggestions": [
            "Book an appointment",
            "Find a doctor",
            "View my appointments",
            "Ask about symptoms"
        ]
    },
    "book_appointment": {
        "patterns": [
            r"book|schedule|make.*appointment",
            r"see.*doctor|visit.*doctor",
            r"appointment.*book|appointment.*schedule"
        ],
        "responses": [
            "I'd be happy to help you book an appointment! To get started, I'll need to know what type of doctor you'd like to see.",
            "Let's book your appointment. What medical specialty or type of doctor are you looking for?",
            "Great! I can help you schedule an appointment. What's the reason for your visit?"
        ],
        "suggestions": [
            "General checkup",
            "Cardiology",
            "Dermatology",
            "Orthopedics"
        ],
        "actions": [
            {"type": "redirect", "url": "/appointments/book"},
            {"type": "form", "fields": ["specialty", "date", "time"]}
        ]
    },
    "find_doctor": {
        "patterns": [
            r"find.*doctor|search.*doctor|doctor.*near",
            r"specialist|cardiologist|dermatologist|neurologist",
            r"recommend.*doctor|best.*doctor"
        ],
        "responses": [
            "I can help you find the right doctor! What specialty are you looking for?",
            "Let me help you find a qualified doctor. What type of medical condition or specialty do you need?",
            "I'll help you find the perfect doctor for your needs. What medical specialty interests you?"
        ],
        "suggestions": [
            "Cardiology",
            "Dermatology", 
            "Neurology",
            "General Medicine"
        ],
        "actions": [
            {"type": "redirect", "url": "/doctors"},
            {"type": "search", "category": "doctors"}
        ]
    },
    "view_appointments": {
        "patterns": [
            r"my.*appointments|view.*appointments|check.*appointments",
            r"upcoming.*appointments|scheduled.*appointments",
            r"appointment.*list|appointment.*history"
        ],
        "responses": [
            "I can show you your appointments. Let me fetch your upcoming and past appointments.",
            "Here's where you can view all your appointments - upcoming, completed, and cancelled.",
            "I'll help you check your appointment schedule. You can see all your medical appointments here."
        ],
        "suggestions": [
            "Upcoming appointments",
            "Past appointments",
            "Reschedule appointment",
            "Cancel appointment"
        ],
        "actions": [
            {"type": "redirect", "url": "/appointments/my-appointments"},
            {"type": "fetch", "data": "user_appointments"}
        ]
    },
    "symptoms": {
        "patterns": [
            r"symptoms|feeling.*sick|not.*well|pain",
            r"headache|fever|cough|stomach.*ache",
            r"what.*doctor.*see|which.*specialist"
        ],
        "responses": [
            "I understand you're experiencing symptoms. While I can't provide medical diagnosis, I can help you find the right type of doctor to see.",
            "For symptom analysis, I recommend using our AI-powered specialty prediction tool or consulting with a healthcare professional.",
            "I can help you determine which type of specialist might be best for your symptoms. Would you like me to analyze your symptoms?"
        ],
        "suggestions": [
            "Analyze symptoms",
            "Find emergency care",
            "Book urgent appointment",
            "General practitioner"
        ],
        "actions": [
            {"type": "redirect", "url": "/ml/predict-specialty"},
            {"type": "form", "fields": ["symptoms", "duration"]}
        ]
    },
    "cancel_appointment": {
        "patterns": [
            r"cancel.*appointment|cancel.*booking",
            r"remove.*appointment|delete.*appointment",
            r"can't.*make.*appointment|unable.*attend"
        ],
        "responses": [
            "I can help you cancel your appointment. Please note that cancellations should be made at least 24 hours in advance when possible.",
            "I'll help you cancel your appointment. You can cancel through your appointment list or let me know which appointment you'd like to cancel.",
            "To cancel an appointment, I'll need to know which specific appointment you want to cancel."
        ],
        "suggestions": [
            "View my appointments",
            "Cancel specific appointment",
            "Reschedule instead",
            "Contact support"
        ],
        "actions": [
            {"type": "redirect", "url": "/appointments/my-appointments"},
            {"type": "form", "fields": ["appointment_id", "reason"]}
        ]
    },
    "medicines": {
        "patterns": [
            r"medicine|medication|prescription|drug",
            r"pills|tablets|dosage|pharmacy",
            r"side.*effects|drug.*interaction"
        ],
        "responses": [
            "For medication information, I recommend consulting with your doctor or pharmacist. I can help you view your prescriptions from your appointments.",
            "I can show you your prescription history from your doctor visits, but for specific medication advice, please consult a healthcare professional.",
            "You can view your prescriptions and medication history in your patient portal. For medical advice about medications, please contact your doctor."
        ],
        "suggestions": [
            "View prescriptions",
            "Contact doctor",
            "Pharmacy information",
            "Drug interactions"
        ],
        "actions": [
            {"type": "redirect", "url": "/prescriptions"},
            {"type": "external", "url": "https://www.drugs.com/drug_interactions.html"}
        ]
    },
    "faq": {
        "patterns": [
            r"how.*cancel|how.*reschedule|how.*book",
            r"what.*cost|what.*price|how.*much",
            r"insurance|payment|billing"
        ],
        "responses": [
            "Here are some frequently asked questions. What specific information are you looking for?",
            "I can help answer common questions about our services. What would you like to know?",
            "Let me help you with that question. Here's what I can tell you about our services."
        ],
        "suggestions": [
            "How to book appointments",
            "Cancellation policy",
            "Payment methods",
            "Insurance coverage"
        ],
        "actions": [
            {"type": "redirect", "url": "/faq"},
            {"type": "info", "category": "general"}
        ]
    },
    "emergency": {
        "patterns": [
            r"emergency|urgent|critical|severe.*pain",
            r"can't.*breathe|chest.*pain|heart.*attack",
            r"bleeding|unconscious|overdose"
        ],
        "responses": [
            "🚨 If this is a medical emergency, please call emergency services immediately (911) or go to the nearest emergency room.",
            "⚠️ For urgent medical situations, please seek immediate medical attention. Call 911 or visit your nearest emergency department.",
            "🏥 This sounds like it may require immediate medical attention. Please contact emergency services or go to the nearest hospital emergency room."
        ],
        "suggestions": [
            "Call 911",
            "Find nearest hospital",
            "Emergency contacts",
            "Urgent care centers"
        ],
        "actions": [
            {"type": "emergency", "action": "call_911"},
            {"type": "redirect", "url": "/emergency-contacts"}
        ]
    },
    "unknown": {
        "patterns": [],
        "responses": [
            "I'm not sure I understand. Could you please rephrase your question?",
            "I didn't quite get that. Can you tell me more about what you need help with?",
            "I'm here to help with medical appointments and health-related questions. Could you be more specific?"
        ],
        "suggestions": [
            "Book appointment",
            "Find doctor",
            "View appointments",
            "Get help"
        ]
    }
}

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token with main backend"""
    try:
        backend_url = os.getenv("BACKEND_URL", "http://localhost:8080")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{backend_url}/api/auth/verify",
                headers={"Authorization": f"Bearer {credentials.credentials}"}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials"
                )
            
            return response.json()
            
    except httpx.RequestError:
        # If backend is not available, allow access for development
        logger.warning("Backend not available, allowing access")
        return {"user": "development", "role": "PATIENT"}
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

def classify_intent(message: str) -> tuple:
    """Classify user intent based on message content"""
    message_lower = message.lower()
    
    # Check for emergency keywords first
    for pattern in INTENT_PATTERNS["emergency"]["patterns"]:
        if re.search(pattern, message_lower):
            return "emergency", 0.95
    
    # Check other intents
    for intent, data in INTENT_PATTERNS.items():
        if intent == "emergency":
            continue
            
        for pattern in data["patterns"]:
            if re.search(pattern, message_lower):
                confidence = 0.8 if intent != "unknown" else 0.3
                return intent, confidence
    
    return "unknown", 0.3

def generate_response(intent: str, confidence: float) -> ChatResponse:
    """Generate response based on classified intent"""
    intent_data = INTENT_PATTERNS.get(intent, INTENT_PATTERNS["unknown"])
    
    # Select response (in a real implementation, this could be more sophisticated)
    response_text = intent_data["responses"][0]
    suggestions = intent_data.get("suggestions", [])
    actions = intent_data.get("actions", [])
    
    return ChatResponse(
        response=response_text,
        intent=intent,
        confidence=confidence,
        suggestions=suggestions,
        actions=actions,
        timestamp=datetime.now()
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="1.0.0"
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user_info: dict = Depends(verify_token)
):
    """Process chat message and return response"""
    
    try:
        # Classify intent
        intent, confidence = classify_intent(request.message)
        
        # Generate response
        response = generate_response(intent, confidence)
        
        logger.info(f"Chat processed: intent={intent}, confidence={confidence:.2f}")
        
        return response
        
    except Exception as e:
        logger.error(f"Chat processing error: {e}")
        raise HTTPException(status_code=500, detail="Chat processing failed")

@app.get("/intents")
async def get_intents(user_info: dict = Depends(verify_token)):
    """Get available intents and their descriptions"""
    intents = {}
    for intent, data in INTENT_PATTERNS.items():
        if intent != "unknown":
            intents[intent] = {
                "description": f"Handle {intent.replace('_', ' ')} related queries",
                "examples": data["patterns"][:2],  # First 2 patterns as examples
                "suggestions": data.get("suggestions", [])
            }
    
    return {"intents": intents}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
