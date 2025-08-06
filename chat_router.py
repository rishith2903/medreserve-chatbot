"""
FastAPI Router for MedReserve AI Chatbot System
Handles REST API endpoints and WebSocket connections
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends, Query, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from loguru import logger

from patient_chatbot import PatientChatbot
from doctor_chatbot import DoctorChatbot
from realtime_chat import connection_manager, ChatMessageHandler
from utils import JWTHandler
from config import settings


# Pydantic models for request/response
class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    response: str
    type: str
    actions: List[Dict[str, Any]] = []
    data: Optional[Dict[str, Any]] = None
    conversation_id: Optional[str] = None
    timestamp: str


class RoomCreationRequest(BaseModel):
    doctor_id: str
    patient_id: str


class FileUploadInfo(BaseModel):
    name: str
    size: int
    type: str
    url: str
    thumbnail: Optional[str] = None


# Security
security = HTTPBearer()

# Initialize chatbots
patient_chatbot = PatientChatbot()
doctor_chatbot = DoctorChatbot()

# Create router
router = APIRouter(prefix="/chat", tags=["Chatbot"])


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Extract user information from JWT token"""
    return JWTHandler.get_user_from_token(credentials.credentials)


@router.post("/patient", response_model=ChatResponse)
async def patient_chat(
    message: ChatMessage,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Patient chatbot endpoint"""
    try:
        # Verify user is a patient
        if user.get('role') != 'PATIENT':
            raise HTTPException(status_code=403, detail="Access denied. Patient role required.")
        
        # Get token from request (this would need to be passed properly)
        token = "dummy_token"  # In real implementation, extract from request
        
        # Process message
        response = await patient_chatbot.process_message(
            message.message,
            token,
            user['user_id'],
            message.conversation_id or f"patient_{user['user_id']}_{datetime.now().timestamp()}"
        )
        
        return ChatResponse(
            response=response['response'],
            type=response['type'],
            actions=response.get('actions', []),
            data=response.get('data'),
            conversation_id=message.conversation_id,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error in patient chat: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/doctor", response_model=ChatResponse)
async def doctor_chat(
    message: ChatMessage,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Doctor chatbot endpoint"""
    try:
        # Verify user is a doctor
        if user.get('role') != 'DOCTOR':
            raise HTTPException(status_code=403, detail="Access denied. Doctor role required.")
        
        # Get token from request
        token = "dummy_token"  # In real implementation, extract from request
        
        # Process message
        response = await doctor_chatbot.process_message(
            message.message,
            token,
            user['user_id'],
            message.conversation_id or f"doctor_{user['user_id']}_{datetime.now().timestamp()}"
        )
        
        return ChatResponse(
            response=response['response'],
            type=response['type'],
            actions=response.get('actions', []),
            data=response.get('data'),
            conversation_id=message.conversation_id,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error in doctor chat: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str, token: str = Query(...)):
    """WebSocket endpoint for real-time chat"""
    try:
        # Connect user
        user_info = await connection_manager.connect(websocket, user_id, token)
        
        try:
            while True:
                # Receive message
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # Handle message
                await ChatMessageHandler.handle_websocket_message(websocket, user_id, message_data)
                
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for user {user_id}")
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received from user {user_id}")
            await connection_manager.send_personal_message({
                'type': 'error',
                'message': 'Invalid message format'
            }, user_id)
        except Exception as e:
            logger.error(f"Error in WebSocket for user {user_id}: {str(e)}")
            await connection_manager.send_personal_message({
                'type': 'error',
                'message': 'Internal server error'
            }, user_id)
    
    except Exception as e:
        logger.error(f"Failed to establish WebSocket connection for user {user_id}: {str(e)}")
        await websocket.close(code=1008, reason="Authentication failed")
    
    finally:
        connection_manager.disconnect(user_id)


@router.post("/rooms/create")
async def create_chat_room(
    room_request: RoomCreationRequest,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a chat room between doctor and patient"""
    try:
        # Verify user has permission to create room
        user_role = user.get('role')
        if user_role not in ['DOCTOR', 'PATIENT', 'ADMIN']:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Create room
        room_id = connection_manager.create_chat_room(
            room_request.doctor_id,
            room_request.patient_id
        )
        
        return {
            'room_id': room_id,
            'doctor_id': room_request.doctor_id,
            'patient_id': room_request.patient_id,
            'created_at': datetime.now().isoformat(),
            'status': 'active'
        }
        
    except Exception as e:
        logger.error(f"Error creating chat room: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create chat room")


@router.get("/rooms/{room_id}/history")
async def get_chat_history(
    room_id: str,
    limit: int = Query(50, ge=1, le=100),
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Get chat history for a room"""
    try:
        # Get chat history
        history = await connection_manager.get_chat_history(room_id, user['user_id'], limit)
        
        return {
            'room_id': room_id,
            'messages': history,
            'total_messages': len(history),
            'retrieved_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting chat history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chat history")


@router.get("/rooms/user/{user_id}")
async def get_user_rooms(
    user_id: str,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Get all chat rooms for a user"""
    try:
        # Verify user can access this information
        if user['user_id'] != user_id and user.get('role') != 'ADMIN':
            raise HTTPException(status_code=403, detail="Access denied")
        
        rooms = connection_manager.get_user_rooms(user_id)
        
        return {
            'user_id': user_id,
            'rooms': rooms,
            'total_rooms': len(rooms),
            'retrieved_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting user rooms: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve user rooms")


@router.get("/active-users")
async def get_active_users(user: Dict[str, Any] = Depends(get_current_user)):
    """Get list of currently active users"""
    try:
        # Only doctors and admins can see active users
        if user.get('role') not in ['DOCTOR', 'ADMIN']:
            raise HTTPException(status_code=403, detail="Access denied")
        
        active_users = connection_manager.get_active_users()
        
        return {
            'active_users': active_users,
            'total_active': len(active_users),
            'retrieved_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting active users: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve active users")


@router.post("/broadcast")
async def broadcast_message(
    message: str = Body(..., embed=True),
    message_type: str = Body("system", embed=True),
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Broadcast system message to all connected users (Admin only)"""
    try:
        # Verify admin access
        if user.get('role') != 'ADMIN':
            raise HTTPException(status_code=403, detail="Admin access required")
        
        await connection_manager.broadcast_system_message(message, message_type)
        
        return {
            'message': 'Broadcast sent successfully',
            'recipients': len(connection_manager.active_connections),
            'sent_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error broadcasting message: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to broadcast message")


@router.post("/notify/{user_id}")
async def send_notification(
    user_id: str,
    notification: Dict[str, Any] = Body(...),
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Send notification to specific user"""
    try:
        # Verify permission to send notification
        user_role = user.get('role')
        if user_role not in ['DOCTOR', 'ADMIN'] and user['user_id'] != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        await connection_manager.send_notification(user_id, notification)
        
        return {
            'message': 'Notification sent successfully',
            'recipient': user_id,
            'sent_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error sending notification: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send notification")


@router.post("/upload-file")
async def handle_file_upload(
    file_info: FileUploadInfo,
    room_id: str = Body(...),
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Handle file upload for chat"""
    try:
        # Verify user is in the room
        user_rooms = connection_manager.get_user_rooms(user['user_id'])
        if room_id not in user_rooms:
            raise HTTPException(status_code=403, detail="Access denied to this room")
        
        # Handle file share
        await connection_manager.handle_file_share({
            'room_id': room_id,
            'file_info': file_info.dict()
        }, user['user_id'])
        
        return {
            'message': 'File shared successfully',
            'room_id': room_id,
            'file_name': file_info.name,
            'shared_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error handling file upload: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to share file")


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'service': 'MedReserve AI Chatbot',
        'version': '1.0.0',
        'active_connections': len(connection_manager.active_connections),
        'active_rooms': len(connection_manager.chat_rooms),
        'timestamp': datetime.now().isoformat()
    }


@router.get("/stats")
async def get_chat_stats(user: Dict[str, Any] = Depends(get_current_user)):
    """Get chat system statistics (Admin only)"""
    try:
        if user.get('role') != 'ADMIN':
            raise HTTPException(status_code=403, detail="Admin access required")
        
        stats = {
            'active_connections': len(connection_manager.active_connections),
            'total_rooms': len(connection_manager.chat_rooms),
            'total_messages': sum(len(messages) for messages in connection_manager.message_history.values()),
            'users_by_role': {},
            'rooms_by_participants': {},
            'timestamp': datetime.now().isoformat()
        }
        
        # Count users by role
        for user_info in connection_manager.user_info.values():
            role = user_info.get('role', 'UNKNOWN')
            stats['users_by_role'][role] = stats['users_by_role'].get(role, 0) + 1
        
        # Count rooms by participant count
        for participants in connection_manager.chat_rooms.values():
            count = len(participants)
            stats['rooms_by_participants'][str(count)] = stats['rooms_by_participants'].get(str(count), 0) + 1
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting chat stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics")


# Error handlers will be added to the main app, not the router
# This is handled in main.py
