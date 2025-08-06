"""
Utility functions for MedReserve AI Chatbot System
"""

import json
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import httpx
import jwt
from fastapi import HTTPException, status
from loguru import logger
from config import settings


class JWTHandler:
    """JWT token handling utilities"""
    
    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """Decode JWT token and extract user information"""
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm]
            )
            
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    @staticmethod
    def get_user_from_token(token: str) -> Dict[str, Any]:
        """Extract user information from JWT token"""
        payload = JWTHandler.decode_token(token)
        
        user_info = {
            'user_id': payload.get('sub'),
            'username': payload.get('username'),
            'email': payload.get('email'),
            'role': payload.get('role', 'PATIENT'),
            'full_name': payload.get('full_name'),
            'exp': payload.get('exp')
        }
        
        return user_info


class SpringBootAPIClient:
    """Client for communicating with Spring Boot backend"""
    
    def __init__(self):
        self.base_url = settings.spring_boot_base_url
        self.timeout = 30.0
    
    async def make_request(
        self,
        method: str,
        endpoint: str,
        token: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make authenticated request to Spring Boot API"""
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if method.upper() == 'GET':
                    response = await client.get(url, headers=headers, params=params)
                elif method.upper() == 'POST':
                    response = await client.post(url, headers=headers, json=data)
                elif method.upper() == 'PUT':
                    response = await client.put(url, headers=headers, json=data)
                elif method.upper() == 'DELETE':
                    response = await client.delete(url, headers=headers)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Backend API error: {e.response.text}"
            )
        except httpx.RequestError as e:
            logger.error(f"Request error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Backend service unavailable"
            )
    
    # Appointment-related methods
    async def get_appointments(self, token: str, user_id: str, role: str) -> List[Dict]:
        """Get appointments for user"""
        if role == 'PATIENT':
            endpoint = f"/appointments/patient/{user_id}"
        else:  # DOCTOR
            endpoint = f"/appointments/doctor/{user_id}"
        
        response = await self.make_request('GET', endpoint, token)
        return response if isinstance(response, list) else []
    
    async def book_appointment(self, token: str, appointment_data: Dict) -> Dict:
        """Book a new appointment"""
        endpoint = "/appointments/book"
        return await self.make_request('POST', endpoint, token, appointment_data)
    
    async def cancel_appointment(self, token: str, appointment_id: str) -> Dict:
        """Cancel an appointment"""
        endpoint = f"/appointments/{appointment_id}/cancel"
        return await self.make_request('PUT', endpoint, token)
    
    async def reschedule_appointment(self, token: str, appointment_id: str, new_data: Dict) -> Dict:
        """Reschedule an appointment"""
        endpoint = f"/appointments/{appointment_id}/reschedule"
        return await self.make_request('PUT', endpoint, token, new_data)
    
    # Doctor-related methods
    async def get_doctors(self, token: str, specialization: Optional[str] = None) -> List[Dict]:
        """Get list of doctors"""
        endpoint = "/doctors"
        params = {'specialization': specialization} if specialization else None
        response = await self.make_request('GET', endpoint, token, params=params)
        return response if isinstance(response, list) else []
    
    async def get_doctor_availability(self, token: str, doctor_id: str, date: str) -> Dict:
        """Get doctor availability for a specific date"""
        endpoint = f"/doctors/{doctor_id}/available-slots"
        params = {'date': date}
        return await self.make_request('GET', endpoint, token, params=params)
    
    # Prescription-related methods
    async def get_prescriptions(self, token: str, patient_id: str) -> List[Dict]:
        """Get prescriptions for a patient"""
        endpoint = f"/prescriptions/patient/{patient_id}"
        response = await self.make_request('GET', endpoint, token)
        return response if isinstance(response, list) else []
    
    async def add_prescription(self, token: str, prescription_data: Dict) -> Dict:
        """Add a new prescription"""
        endpoint = "/prescriptions"
        return await self.make_request('POST', endpoint, token, prescription_data)
    
    # Medical reports methods
    async def get_medical_reports(self, token: str, patient_id: str) -> List[Dict]:
        """Get medical reports for a patient"""
        endpoint = f"/medical-reports/patient/{patient_id}"
        response = await self.make_request('GET', endpoint, token)
        return response if isinstance(response, list) else []
    
    # Patient-related methods
    async def get_patients(self, token: str, doctor_id: str) -> List[Dict]:
        """Get patients assigned to a doctor"""
        endpoint = f"/doctors/{doctor_id}/patients"
        response = await self.make_request('GET', endpoint, token)
        return response if isinstance(response, list) else []


class MessageProcessor:
    """Process and analyze chat messages"""
    
    @staticmethod
    def extract_intent(message: str) -> str:
        """Extract intent from user message using rule-based approach"""
        message_lower = message.lower().strip()
        
        # Appointment booking intents
        if any(keyword in message_lower for keyword in ['book', 'schedule', 'appointment', 'meet']):
            return 'book_appointment'
        
        # View appointments
        if any(keyword in message_lower for keyword in ['my appointments', 'upcoming', 'scheduled']):
            return 'view_appointments'
        
        # Cancel/reschedule
        if any(keyword in message_lower for keyword in ['cancel', 'reschedule', 'change']):
            return 'modify_appointment'
        
        # Prescriptions
        if any(keyword in message_lower for keyword in ['prescription', 'medicine', 'medication', 'pills']):
            return 'view_prescriptions'
        
        # Medical reports
        if any(keyword in message_lower for keyword in ['report', 'test result', 'lab result']):
            return 'view_reports'
        
        # Doctor information
        if any(keyword in message_lower for keyword in ['doctor', 'specialist', 'available']):
            return 'doctor_info'
        
        # Emergency
        if any(keyword in message_lower for keyword in settings.emergency_keywords):
            return 'emergency'
        
        # General chat
        return 'general_chat'
    
    @staticmethod
    def extract_specialization(message: str) -> Optional[str]:
        """Extract medical specialization from message"""
        message_lower = message.lower()
        
        for specialization in settings.medical_specializations:
            if specialization.lower() in message_lower:
                return specialization
        
        # Common variations
        specialization_map = {
            'heart': 'Cardiology',
            'skin': 'Dermatology',
            'brain': 'Neurology',
            'bone': 'Orthopedics',
            'eye': 'Ophthalmology',
            'ear': 'ENT',
            'mental': 'Psychiatry',
            'lung': 'Pulmonology',
            'stomach': 'Gastroenterology',
            'kidney': 'Urology',
            'child': 'Pediatrics',
            'cancer': 'Oncology'
        }
        
        for keyword, specialization in specialization_map.items():
            if keyword in message_lower:
                return specialization
        
        return None
    
    @staticmethod
    def extract_date_time(message: str) -> Optional[Dict[str, str]]:
        """Extract date and time from message"""
        # Simple regex patterns for date/time extraction
        date_patterns = [
            r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b',  # DD/MM/YYYY or DD-MM-YYYY
            r'\b(\d{4})[/-](\d{1,2})[/-](\d{1,2})\b',  # YYYY/MM/DD or YYYY-MM-DD
        ]
        
        time_patterns = [
            r'\b(\d{1,2}):(\d{2})\s*(am|pm)?\b',  # HH:MM am/pm
            r'\b(\d{1,2})\s*(am|pm)\b',  # H am/pm
        ]
        
        result = {}
        
        # Extract date
        for pattern in date_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                result['date'] = match.group(0)
                break
        
        # Extract time
        for pattern in time_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                result['time'] = match.group(0)
                break
        
        return result if result else None
    
    @staticmethod
    def is_emergency(message: str) -> bool:
        """Check if message indicates an emergency"""
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in settings.emergency_keywords)
    
    @staticmethod
    def format_prescription(prescriptions: List[Dict]) -> str:
        """Format prescription data for display"""
        if not prescriptions:
            return "No prescriptions found."
        
        formatted = "📋 **Your Current Prescriptions:**\n\n"
        
        for i, prescription in enumerate(prescriptions, 1):
            medication = prescription.get('medicationName', 'Unknown')
            dosage = prescription.get('dosage', 'As prescribed')
            frequency = prescription.get('frequency', 'As directed')
            
            formatted += f"{i}. **{medication}**\n"
            formatted += f"   💊 Dosage: {dosage}\n"
            formatted += f"   ⏰ Frequency: {frequency}\n\n"
        
        return formatted
    
    @staticmethod
    def format_appointments(appointments: List[Dict]) -> str:
        """Format appointment data for display"""
        if not appointments:
            return "No upcoming appointments found."
        
        formatted = "📅 **Your Upcoming Appointments:**\n\n"
        
        for i, appointment in enumerate(appointments, 1):
            doctor_name = appointment.get('doctorName', 'Unknown Doctor')
            date = appointment.get('appointmentDate', 'TBD')
            time = appointment.get('appointmentTime', 'TBD')
            reason = appointment.get('reason', 'General consultation')
            
            formatted += f"{i}. **Dr. {doctor_name}**\n"
            formatted += f"   📅 Date: {date}\n"
            formatted += f"   ⏰ Time: {time}\n"
            formatted += f"   📝 Reason: {reason}\n\n"
        
        return formatted


# Global API client instance
api_client = SpringBootAPIClient()
