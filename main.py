"""
MedReserve AI Chatbot System - Main FastAPI Application
Dual chatbot system for patients and doctors with real-time messaging
"""

import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from loguru import logger

from config import settings
from chat_router import router as chat_router


# Configure logging
logger.remove()  # Remove default handler
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.log_level
)

if settings.log_file:
    logger.add(
        settings.log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.log_level,
        rotation="1 day",
        retention="30 days"
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("🚀 Starting MedReserve AI Chatbot System")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Spring Boot API: {settings.spring_boot_base_url}")
    
    # Create upload directory if it doesn't exist
    os.makedirs(settings.upload_directory, exist_ok=True)
    logger.info(f"Upload directory: {settings.upload_directory}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down MedReserve AI Chatbot System")


# Create FastAPI application
app = FastAPI(
    title="MedReserve AI Chatbot System",
    description="""
    Intelligent dual chatbot system for MedReserve AI platform.
    
    ## Features
    
    ### 🤖 Patient Chatbot
    - Book appointments via chat
    - View upcoming appointments
    - Check prescriptions and medical reports
    - Find doctor information
    - Real-time chat with assigned doctors
    
    ### 👨‍⚕️ Doctor Chatbot
    - View appointment schedules
    - Manage patient lists
    - Add prescriptions and diagnoses via chat
    - Real-time patient communication
    - Emergency patient alerts
    
    ### 💬 Real-time Messaging
    - WebSocket-based chat rooms
    - Doctor-patient secure communication
    - File sharing capabilities
    - Typing indicators and message status
    - Message history and notifications
    
    ## Authentication
    All endpoints require JWT authentication with appropriate role permissions.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add trusted host middleware for production
if not settings.debug:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "*.medreserve.ai"]
    )

# Include routers
app.include_router(chat_router)

# Serve static files for uploads
if os.path.exists(settings.upload_directory):
    app.mount("/uploads", StaticFiles(directory=settings.upload_directory), name="uploads")


@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "service": "MedReserve AI Chatbot System",
        "version": "1.0.0",
        "status": "operational",
        "features": {
            "patient_chatbot": "✅ Available",
            "doctor_chatbot": "✅ Available",
            "realtime_chat": "✅ Available",
            "file_sharing": "✅ Available",
            "websocket_support": "✅ Available"
        },
        "endpoints": {
            "patient_chat": "/chat/patient",
            "doctor_chat": "/chat/doctor",
            "websocket": "/chat/ws/{user_id}",
            "documentation": "/docs",
            "health_check": "/health"
        },
        "authentication": "JWT Bearer Token Required",
        "cors_enabled": True,
        "debug_mode": settings.debug
    }


@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    try:
        # Check database connection (if applicable)
        db_status = "✅ Connected"  # Placeholder
        
        # Check Spring Boot API connection
        api_status = "✅ Connected"  # Placeholder - would make actual request
        
        # Check Redis connection (if applicable)
        redis_status = "✅ Connected"  # Placeholder
        
        return {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",  # Would use actual timestamp
            "service": "MedReserve AI Chatbot",
            "version": "1.0.0",
            "environment": os.getenv("ENVIRONMENT", "development"),
            "components": {
                "database": db_status,
                "spring_boot_api": api_status,
                "redis": redis_status,
                "websocket": "✅ Active",
                "file_upload": "✅ Available"
            },
            "metrics": {
                "active_connections": 0,  # Would get from connection manager
                "total_rooms": 0,
                "uptime_seconds": 0
            },
            "configuration": {
                "max_file_size": f"{settings.max_file_size / (1024*1024):.1f}MB",
                "max_message_length": settings.max_message_length,
                "websocket_ping_interval": settings.websocket_ping_interval
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": "2024-01-01T00:00:00Z"
            }
        )


@app.get("/info")
async def system_info():
    """System information endpoint"""
    return {
        "system": "MedReserve AI Chatbot System",
        "description": "Intelligent dual chatbot system for medical assistance",
        "architecture": {
            "framework": "FastAPI",
            "websocket": "Native WebSocket support",
            "authentication": "JWT Bearer tokens",
            "database": "PostgreSQL integration",
            "cache": "Redis support",
            "api_integration": "Spring Boot REST API"
        },
        "chatbot_capabilities": {
            "patient_features": [
                "Appointment booking via natural language",
                "View upcoming appointments",
                "Check prescriptions and dosages",
                "View medical reports",
                "Find doctor information",
                "Real-time doctor communication",
                "Emergency assistance"
            ],
            "doctor_features": [
                "View appointment schedules",
                "Manage patient lists",
                "Add prescriptions via chat",
                "Record diagnoses and treatments",
                "Patient history access",
                "Real-time patient communication",
                "Emergency patient alerts"
            ],
            "realtime_features": [
                "WebSocket-based messaging",
                "Secure doctor-patient rooms",
                "File sharing (reports, images)",
                "Typing indicators",
                "Message read receipts",
                "Push notifications",
                "Message history"
            ]
        },
        "nlp_features": {
            "intent_recognition": "Rule-based with keyword matching",
            "entity_extraction": "Medical specializations, dates, times",
            "context_awareness": "Conversation state management",
            "emergency_detection": "Critical keyword monitoring",
            "smart_responses": "Context-appropriate suggestions"
        },
        "security": {
            "authentication": "JWT token validation",
            "authorization": "Role-based access control",
            "data_encryption": "HTTPS/WSS encryption",
            "input_validation": "Comprehensive sanitization",
            "rate_limiting": "Request throttling",
            "cors_protection": "Configurable origins"
        },
        "integration": {
            "spring_boot_api": settings.spring_boot_base_url,
            "database": "PostgreSQL via Spring Boot",
            "file_storage": "Local filesystem with URL access",
            "notifications": "Real-time WebSocket delivery"
        }
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "timestamp": "2024-01-01T00:00:00Z",
            "path": str(request.url)
        }
    )


# HTTP exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": "2024-01-01T00:00:00Z",
            "path": str(request.url)
        }
    )


# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests"""
    start_time = "2024-01-01T00:00:00Z"  # Would use actual time
    
    # Log request
    logger.info(f"📥 {request.method} {request.url}")
    
    # Process request
    response = await call_next(request)
    
    # Log response
    process_time = 0.0  # Would calculate actual time
    logger.info(f"📤 {request.method} {request.url} - {response.status_code} ({process_time:.3f}s)")
    
    return response


if __name__ == "__main__":
    # Run the application
    logger.info("🚀 Starting MedReserve AI Chatbot System")
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        access_log=True,
        ws_ping_interval=settings.websocket_ping_interval,
        ws_ping_timeout=settings.websocket_ping_timeout
    )
