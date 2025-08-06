"""
Real-time Chat Module for MedReserve AI
Handles WebSocket connections for doctor-patient communication
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, List, Set, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect
from loguru import logger
from utils import JWTHandler
from config import settings


class ConnectionManager:
    """Manages WebSocket connections for real-time chat"""
    
    def __init__(self):
        # Store active connections by user_id
        self.active_connections: Dict[str, WebSocket] = {}
        
        # Store chat rooms (doctor-patient pairs)
        self.chat_rooms: Dict[str, Set[str]] = {}
        
        # Store user information
        self.user_info: Dict[str, Dict[str, Any]] = {}
        
        # Store message history (in production, use database)
        self.message_history: Dict[str, List[Dict[str, Any]]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str, token: str):
        """Accept WebSocket connection and authenticate user"""
        try:
            # Authenticate user
            user_info = JWTHandler.get_user_from_token(token)
            
            # Accept connection
            await websocket.accept()
            
            # Store connection and user info
            self.active_connections[user_id] = websocket
            self.user_info[user_id] = user_info
            
            logger.info(f"User {user_id} ({user_info.get('role')}) connected to chat")
            
            # Send connection confirmation
            await self.send_personal_message({
                'type': 'connection_confirmed',
                'message': 'Connected to MedReserve AI Chat',
                'user_info': {
                    'user_id': user_id,
                    'role': user_info.get('role'),
                    'name': user_info.get('full_name')
                },
                'timestamp': datetime.now().isoformat()
            }, user_id)
            
            return user_info
            
        except Exception as e:
            logger.error(f"Error connecting user {user_id}: {str(e)}")
            await websocket.close(code=1008, reason="Authentication failed")
            raise
    
    def disconnect(self, user_id: str):
        """Remove user from active connections"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        
        if user_id in self.user_info:
            del self.user_info[user_id]
        
        # Remove from chat rooms
        rooms_to_remove = []
        for room_id, participants in self.chat_rooms.items():
            if user_id in participants:
                participants.remove(user_id)
                if len(participants) == 0:
                    rooms_to_remove.append(room_id)
        
        for room_id in rooms_to_remove:
            del self.chat_rooms[room_id]
        
        logger.info(f"User {user_id} disconnected from chat")
    
    async def send_personal_message(self, message: Dict[str, Any], user_id: str):
        """Send message to specific user"""
        if user_id in self.active_connections:
            try:
                websocket = self.active_connections[user_id]
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message to {user_id}: {str(e)}")
                # Remove broken connection
                self.disconnect(user_id)
    
    async def send_room_message(self, message: Dict[str, Any], room_id: str, exclude_user: Optional[str] = None):
        """Send message to all users in a chat room"""
        if room_id in self.chat_rooms:
            participants = self.chat_rooms[room_id].copy()
            if exclude_user:
                participants.discard(exclude_user)
            
            for user_id in participants:
                await self.send_personal_message(message, user_id)
    
    def create_chat_room(self, doctor_id: str, patient_id: str) -> str:
        """Create or get existing chat room for doctor-patient pair"""
        # Create room ID (consistent regardless of order)
        room_id = f"chat_{min(doctor_id, patient_id)}_{max(doctor_id, patient_id)}"
        
        if room_id not in self.chat_rooms:
            self.chat_rooms[room_id] = set()
            self.message_history[room_id] = []
        
        # Add participants
        self.chat_rooms[room_id].add(doctor_id)
        self.chat_rooms[room_id].add(patient_id)
        
        logger.info(f"Chat room {room_id} created/updated for doctor {doctor_id} and patient {patient_id}")
        return room_id
    
    def join_room(self, user_id: str, room_id: str):
        """Add user to chat room"""
        if room_id not in self.chat_rooms:
            self.chat_rooms[room_id] = set()
            self.message_history[room_id] = []
        
        self.chat_rooms[room_id].add(user_id)
        logger.info(f"User {user_id} joined room {room_id}")
    
    def leave_room(self, user_id: str, room_id: str):
        """Remove user from chat room"""
        if room_id in self.chat_rooms and user_id in self.chat_rooms[room_id]:
            self.chat_rooms[room_id].remove(user_id)
            logger.info(f"User {user_id} left room {room_id}")
    
    async def handle_chat_message(self, message_data: Dict[str, Any], sender_id: str):
        """Handle incoming chat message"""
        try:
            message_type = message_data.get('type', 'text')
            room_id = message_data.get('room_id')
            content = message_data.get('content', '')
            
            if not room_id:
                await self.send_personal_message({
                    'type': 'error',
                    'message': 'Room ID is required for chat messages'
                }, sender_id)
                return
            
            # Get sender info
            sender_info = self.user_info.get(sender_id, {})
            
            # Create message object
            chat_message = {
                'type': 'chat_message',
                'message_type': message_type,
                'room_id': room_id,
                'sender_id': sender_id,
                'sender_name': sender_info.get('full_name', 'Unknown'),
                'sender_role': sender_info.get('role', 'UNKNOWN'),
                'content': content,
                'timestamp': datetime.now().isoformat(),
                'message_id': f"msg_{datetime.now().timestamp()}"
            }
            
            # Store message in history
            if room_id in self.message_history:
                self.message_history[room_id].append(chat_message)
                
                # Keep only last 100 messages per room
                if len(self.message_history[room_id]) > 100:
                    self.message_history[room_id] = self.message_history[room_id][-100:]
            
            # Send to all participants in the room
            await self.send_room_message(chat_message, room_id)
            
            logger.info(f"Chat message sent in room {room_id} by {sender_id}")
            
        except Exception as e:
            logger.error(f"Error handling chat message: {str(e)}")
            await self.send_personal_message({
                'type': 'error',
                'message': 'Failed to send message'
            }, sender_id)
    
    async def handle_typing_indicator(self, data: Dict[str, Any], user_id: str):
        """Handle typing indicator"""
        room_id = data.get('room_id')
        is_typing = data.get('is_typing', False)
        
        if room_id:
            typing_message = {
                'type': 'typing_indicator',
                'room_id': room_id,
                'user_id': user_id,
                'user_name': self.user_info.get(user_id, {}).get('full_name', 'Unknown'),
                'is_typing': is_typing,
                'timestamp': datetime.now().isoformat()
            }
            
            # Send to other participants (exclude sender)
            await self.send_room_message(typing_message, room_id, exclude_user=user_id)
    
    async def get_chat_history(self, room_id: str, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get chat history for a room"""
        if room_id not in self.chat_rooms or user_id not in self.chat_rooms[room_id]:
            return []
        
        history = self.message_history.get(room_id, [])
        return history[-limit:] if limit else history
    
    async def handle_file_share(self, data: Dict[str, Any], sender_id: str):
        """Handle file sharing in chat"""
        try:
            room_id = data.get('room_id')
            file_info = data.get('file_info', {})
            
            if not room_id or not file_info:
                await self.send_personal_message({
                    'type': 'error',
                    'message': 'Room ID and file info are required'
                }, sender_id)
                return
            
            # Get sender info
            sender_info = self.user_info.get(sender_id, {})
            
            # Create file share message
            file_message = {
                'type': 'file_share',
                'room_id': room_id,
                'sender_id': sender_id,
                'sender_name': sender_info.get('full_name', 'Unknown'),
                'sender_role': sender_info.get('role', 'UNKNOWN'),
                'file_info': {
                    'name': file_info.get('name'),
                    'size': file_info.get('size'),
                    'type': file_info.get('type'),
                    'url': file_info.get('url'),
                    'thumbnail': file_info.get('thumbnail')
                },
                'timestamp': datetime.now().isoformat(),
                'message_id': f"file_{datetime.now().timestamp()}"
            }
            
            # Store in message history
            if room_id in self.message_history:
                self.message_history[room_id].append(file_message)
            
            # Send to all participants
            await self.send_room_message(file_message, room_id)
            
            logger.info(f"File shared in room {room_id} by {sender_id}: {file_info.get('name')}")
            
        except Exception as e:
            logger.error(f"Error handling file share: {str(e)}")
            await self.send_personal_message({
                'type': 'error',
                'message': 'Failed to share file'
            }, sender_id)
    
    async def handle_message_status(self, data: Dict[str, Any], user_id: str):
        """Handle message read/delivered status"""
        try:
            room_id = data.get('room_id')
            message_id = data.get('message_id')
            status = data.get('status')  # 'delivered', 'read'
            
            if room_id and message_id and status:
                status_message = {
                    'type': 'message_status',
                    'room_id': room_id,
                    'message_id': message_id,
                    'status': status,
                    'user_id': user_id,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Send to other participants
                await self.send_room_message(status_message, room_id, exclude_user=user_id)
                
        except Exception as e:
            logger.error(f"Error handling message status: {str(e)}")
    
    def get_active_users(self) -> List[Dict[str, Any]]:
        """Get list of currently active users"""
        return [
            {
                'user_id': user_id,
                'name': info.get('full_name', 'Unknown'),
                'role': info.get('role', 'UNKNOWN'),
                'connected_at': info.get('connected_at')
            }
            for user_id, info in self.user_info.items()
        ]
    
    def get_user_rooms(self, user_id: str) -> List[str]:
        """Get all chat rooms a user is part of"""
        return [
            room_id for room_id, participants in self.chat_rooms.items()
            if user_id in participants
        ]
    
    async def broadcast_system_message(self, message: str, message_type: str = 'system'):
        """Broadcast system message to all connected users"""
        system_message = {
            'type': message_type,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        
        for user_id in self.active_connections.keys():
            await self.send_personal_message(system_message, user_id)
    
    async def send_notification(self, user_id: str, notification: Dict[str, Any]):
        """Send notification to specific user"""
        notification_message = {
            'type': 'notification',
            'notification': notification,
            'timestamp': datetime.now().isoformat()
        }
        
        await self.send_personal_message(notification_message, user_id)


# Global connection manager instance
connection_manager = ConnectionManager()


class ChatMessageHandler:
    """Handles different types of chat messages"""
    
    @staticmethod
    async def handle_websocket_message(websocket: WebSocket, user_id: str, message_data: Dict[str, Any]):
        """Route WebSocket message to appropriate handler"""
        try:
            message_type = message_data.get('type')
            
            if message_type == 'chat_message':
                await connection_manager.handle_chat_message(message_data, user_id)
            
            elif message_type == 'typing_indicator':
                await connection_manager.handle_typing_indicator(message_data, user_id)
            
            elif message_type == 'file_share':
                await connection_manager.handle_file_share(message_data, user_id)
            
            elif message_type == 'message_status':
                await connection_manager.handle_message_status(message_data, user_id)
            
            elif message_type == 'join_room':
                room_id = message_data.get('room_id')
                if room_id:
                    connection_manager.join_room(user_id, room_id)
                    
                    # Send chat history
                    history = await connection_manager.get_chat_history(room_id, user_id)
                    await connection_manager.send_personal_message({
                        'type': 'chat_history',
                        'room_id': room_id,
                        'messages': history
                    }, user_id)
            
            elif message_type == 'leave_room':
                room_id = message_data.get('room_id')
                if room_id:
                    connection_manager.leave_room(user_id, room_id)
            
            elif message_type == 'get_active_users':
                active_users = connection_manager.get_active_users()
                await connection_manager.send_personal_message({
                    'type': 'active_users',
                    'users': active_users
                }, user_id)
            
            elif message_type == 'ping':
                await connection_manager.send_personal_message({
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                }, user_id)
            
            else:
                logger.warning(f"Unknown message type: {message_type}")
                await connection_manager.send_personal_message({
                    'type': 'error',
                    'message': f'Unknown message type: {message_type}'
                }, user_id)
                
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {str(e)}")
            await connection_manager.send_personal_message({
                'type': 'error',
                'message': 'Failed to process message'
            }, user_id)
