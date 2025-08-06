"""
Patient Chatbot Logic for MedReserve AI
Handles patient interactions, appointment booking, and medical assistance
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from loguru import logger
from utils import MessageProcessor, api_client, JWTHandler
from config import settings


class PatientChatbot:
    """Intelligent chatbot for patient interactions"""
    
    def __init__(self):
        self.conversation_states = {}  # Store conversation state per user
        self.message_processor = MessageProcessor()
    
    async def process_message(
        self,
        message: str,
        user_token: str,
        user_id: str,
        conversation_id: str
    ) -> Dict[str, Any]:
        """Process patient message and generate response"""
        
        try:
            # Get user information from token
            user_info = JWTHandler.get_user_from_token(user_token)
            
            # Extract intent from message
            intent = self.message_processor.extract_intent(message)
            
            # Check for emergency
            if self.message_processor.is_emergency(message):
                return await self._handle_emergency(message, user_info)
            
            # Route to appropriate handler based on intent
            if intent == 'book_appointment':
                return await self._handle_appointment_booking(message, user_token, user_info, conversation_id)
            elif intent == 'view_appointments':
                return await self._handle_view_appointments(user_token, user_info)
            elif intent == 'modify_appointment':
                return await self._handle_modify_appointment(message, user_token, user_info, conversation_id)
            elif intent == 'view_prescriptions':
                return await self._handle_view_prescriptions(user_token, user_info)
            elif intent == 'view_reports':
                return await self._handle_view_reports(user_token, user_info)
            elif intent == 'doctor_info':
                return await self._handle_doctor_info(message, user_token, user_info)
            else:
                return await self._handle_general_chat(message, user_info)
                
        except Exception as e:
            logger.error(f"Error processing patient message: {str(e)}")
            return {
                'response': "I'm sorry, I encountered an error. Please try again or contact support.",
                'type': 'error',
                'actions': []
            }
    
    async def _handle_emergency(self, message: str, user_info: Dict) -> Dict[str, Any]:
        """Handle emergency situations"""
        return {
            'response': """🚨 **EMERGENCY DETECTED** 🚨

I understand this may be urgent. For immediate medical emergencies:

🆘 **Call Emergency Services: 911**
🏥 **Go to nearest Emergency Room**
📞 **Contact your doctor immediately**

If this is not a life-threatening emergency, I can help you:
- Book an urgent appointment
- Find nearby urgent care centers
- Connect you with a doctor

Please let me know how I can assist you further.""",
            'type': 'emergency',
            'actions': [
                {'type': 'call_emergency', 'label': 'Call 911', 'value': '911'},
                {'type': 'book_urgent', 'label': 'Book Urgent Appointment'},
                {'type': 'find_urgent_care', 'label': 'Find Urgent Care'}
            ]
        }
    
    async def _handle_appointment_booking(
        self,
        message: str,
        token: str,
        user_info: Dict,
        conversation_id: str
    ) -> Dict[str, Any]:
        """Handle appointment booking process"""
        
        # Get or initialize conversation state
        state = self.conversation_states.get(conversation_id, {})
        
        # Extract information from message
        specialization = self.message_processor.extract_specialization(message)
        date_time = self.message_processor.extract_date_time(message)
        
        # Multi-step booking process
        if not state.get('booking_step'):
            # Step 1: Get specialization
            if specialization:
                state['specialization'] = specialization
                state['booking_step'] = 'doctor_selection'
                self.conversation_states[conversation_id] = state
                
                # Get available doctors
                try:
                    doctors = await api_client.get_doctors(token, specialization)
                    if doctors:
                        doctor_list = "\n".join([
                            f"👨‍⚕️ **Dr. {doc.get('name', 'Unknown')}** - {doc.get('experience', 'N/A')} years experience"
                            for doc in doctors[:5]
                        ])
                        
                        return {
                            'response': f"""Great! I found {len(doctors)} {specialization} doctors available.

{doctor_list}

Please tell me which doctor you'd prefer, or say "any doctor" for the next available appointment.""",
                            'type': 'doctor_selection',
                            'data': {'doctors': doctors},
                            'actions': [
                                {'type': 'select_doctor', 'label': f"Dr. {doc.get('name')}", 'value': doc.get('id')}
                                for doc in doctors[:3]
                            ] + [{'type': 'any_doctor', 'label': 'Any Available Doctor'}]
                        }
                    else:
                        return {
                            'response': f"I couldn't find any {specialization} doctors available right now. Would you like me to check other specializations or help you find general practitioners?",
                            'type': 'no_doctors',
                            'actions': [
                                {'type': 'general_practice', 'label': 'General Practice'},
                                {'type': 'other_specialization', 'label': 'Other Specialization'}
                            ]
                        }
                except Exception as e:
                    logger.error(f"Error fetching doctors: {str(e)}")
                    return {
                        'response': "I'm having trouble accessing doctor information. Please try again later.",
                        'type': 'error'
                    }
            else:
                return {
                    'response': """I'd be happy to help you book an appointment! 

Which type of doctor would you like to see? For example:
- Cardiologist (heart specialist)
- Dermatologist (skin specialist)  
- Neurologist (brain/nerve specialist)
- General Practitioner
- Or tell me your symptoms and I'll suggest the right specialist""",
                    'type': 'specialization_request',
                    'actions': [
                        {'type': 'specialization', 'label': spec, 'value': spec}
                        for spec in settings.medical_specializations[:6]
                    ]
                }
        
        elif state.get('booking_step') == 'doctor_selection':
            # Step 2: Select doctor and get availability
            # This would continue the booking flow...
            return {
                'response': "Please select a preferred date and time for your appointment. I can check availability for the next 30 days.",
                'type': 'datetime_selection',
                'actions': [
                    {'type': 'date_picker', 'label': 'Select Date'},
                    {'type': 'time_picker', 'label': 'Select Time'}
                ]
            }
        
        # Default response
        return {
            'response': "Let me help you book an appointment. What type of doctor would you like to see?",
            'type': 'booking_start'
        }
    
    async def _handle_view_appointments(self, token: str, user_info: Dict) -> Dict[str, Any]:
        """Handle viewing upcoming appointments"""
        try:
            appointments = await api_client.get_appointments(token, user_info['user_id'], 'PATIENT')
            
            if appointments:
                formatted_appointments = self.message_processor.format_appointments(appointments)
                
                return {
                    'response': formatted_appointments,
                    'type': 'appointments_list',
                    'data': {'appointments': appointments},
                    'actions': [
                        {'type': 'reschedule', 'label': 'Reschedule Appointment'},
                        {'type': 'cancel', 'label': 'Cancel Appointment'},
                        {'type': 'book_new', 'label': 'Book New Appointment'}
                    ]
                }
            else:
                return {
                    'response': """You don't have any upcoming appointments scheduled.

Would you like me to help you book a new appointment?""",
                    'type': 'no_appointments',
                    'actions': [
                        {'type': 'book_appointment', 'label': 'Book New Appointment'},
                        {'type': 'find_doctors', 'label': 'Find Doctors'}
                    ]
                }
                
        except Exception as e:
            logger.error(f"Error fetching appointments: {str(e)}")
            return {
                'response': "I'm having trouble accessing your appointment information. Please try again later.",
                'type': 'error'
            }
    
    async def _handle_modify_appointment(
        self,
        message: str,
        token: str,
        user_info: Dict,
        conversation_id: str
    ) -> Dict[str, Any]:
        """Handle appointment cancellation or rescheduling"""
        
        # First, get user's appointments
        try:
            appointments = await api_client.get_appointments(token, user_info['user_id'], 'PATIENT')
            
            if not appointments:
                return {
                    'response': "You don't have any appointments to modify.",
                    'type': 'no_appointments'
                }
            
            # Check if user wants to cancel or reschedule
            if 'cancel' in message.lower():
                appointment_list = "\n".join([
                    f"{i+1}. Dr. {apt.get('doctorName', 'Unknown')} - {apt.get('appointmentDate')} at {apt.get('appointmentTime')}"
                    for i, apt in enumerate(appointments)
                ])
                
                return {
                    'response': f"""Which appointment would you like to cancel?

{appointment_list}

Please tell me the number of the appointment you want to cancel.""",
                    'type': 'cancel_selection',
                    'data': {'appointments': appointments},
                    'actions': [
                        {'type': 'cancel_appointment', 'label': f"Cancel #{i+1}", 'value': apt.get('id')}
                        for i, apt in enumerate(appointments)
                    ]
                }
            else:
                # Reschedule
                return {
                    'response': "I can help you reschedule your appointment. Which appointment would you like to reschedule, and what's your preferred new date and time?",
                    'type': 'reschedule_request',
                    'data': {'appointments': appointments}
                }
                
        except Exception as e:
            logger.error(f"Error handling appointment modification: {str(e)}")
            return {
                'response': "I'm having trouble accessing your appointments. Please try again later.",
                'type': 'error'
            }
    
    async def _handle_view_prescriptions(self, token: str, user_info: Dict) -> Dict[str, Any]:
        """Handle viewing prescriptions"""
        try:
            prescriptions = await api_client.get_prescriptions(token, user_info['user_id'])
            
            if prescriptions:
                formatted_prescriptions = self.message_processor.format_prescription(prescriptions)
                
                return {
                    'response': formatted_prescriptions + "\n💡 **Reminder:** Take medications as prescribed by your doctor.",
                    'type': 'prescriptions_list',
                    'data': {'prescriptions': prescriptions},
                    'actions': [
                        {'type': 'set_reminder', 'label': 'Set Medication Reminder'},
                        {'type': 'pharmacy_info', 'label': 'Find Nearby Pharmacy'},
                        {'type': 'side_effects', 'label': 'Check Side Effects'}
                    ]
                }
            else:
                return {
                    'response': """You don't have any active prescriptions in our system.

If you have prescriptions from recent appointments, they may not be updated yet. You can:
- Contact your doctor's office
- Check with your pharmacy
- Book a follow-up appointment""",
                    'type': 'no_prescriptions',
                    'actions': [
                        {'type': 'contact_doctor', 'label': 'Contact Doctor'},
                        {'type': 'book_appointment', 'label': 'Book Appointment'}
                    ]
                }
                
        except Exception as e:
            logger.error(f"Error fetching prescriptions: {str(e)}")
            return {
                'response': "I'm having trouble accessing your prescription information. Please try again later.",
                'type': 'error'
            }
    
    async def _handle_view_reports(self, token: str, user_info: Dict) -> Dict[str, Any]:
        """Handle viewing medical reports"""
        try:
            reports = await api_client.get_medical_reports(token, user_info['user_id'])
            
            if reports:
                formatted_reports = "📊 **Your Medical Reports:**\n\n"
                
                for i, report in enumerate(reports, 1):
                    report_type = report.get('reportType', 'General Report')
                    date = report.get('reportDate', 'Unknown date')
                    doctor = report.get('doctorName', 'Unknown doctor')
                    
                    formatted_reports += f"{i}. **{report_type}**\n"
                    formatted_reports += f"   📅 Date: {date}\n"
                    formatted_reports += f"   👨‍⚕️ Doctor: Dr. {doctor}\n\n"
                
                return {
                    'response': formatted_reports,
                    'type': 'reports_list',
                    'data': {'reports': reports},
                    'actions': [
                        {'type': 'download_report', 'label': 'Download Report'},
                        {'type': 'share_report', 'label': 'Share with Doctor'},
                        {'type': 'explain_report', 'label': 'Explain Results'}
                    ]
                }
            else:
                return {
                    'response': """You don't have any medical reports available yet.

Medical reports are typically available after:
- Lab tests
- Imaging studies (X-rays, MRI, etc.)
- Diagnostic procedures

Would you like me to help you book a test or check with your doctor?""",
                    'type': 'no_reports',
                    'actions': [
                        {'type': 'book_test', 'label': 'Book Lab Test'},
                        {'type': 'contact_doctor', 'label': 'Contact Doctor'}
                    ]
                }
                
        except Exception as e:
            logger.error(f"Error fetching medical reports: {str(e)}")
            return {
                'response': "I'm having trouble accessing your medical reports. Please try again later.",
                'type': 'error'
            }
    
    async def _handle_doctor_info(self, message: str, token: str, user_info: Dict) -> Dict[str, Any]:
        """Handle doctor information queries"""
        
        specialization = self.message_processor.extract_specialization(message)
        
        try:
            doctors = await api_client.get_doctors(token, specialization)
            
            if doctors:
                if specialization:
                    response = f"🩺 **Available {specialization} Doctors:**\n\n"
                else:
                    response = "🩺 **Available Doctors:**\n\n"
                
                for i, doctor in enumerate(doctors[:5], 1):
                    name = doctor.get('name', 'Unknown')
                    experience = doctor.get('experience', 'N/A')
                    rating = doctor.get('rating', 'N/A')
                    
                    response += f"{i}. **Dr. {name}**\n"
                    response += f"   📅 Experience: {experience} years\n"
                    response += f"   ⭐ Rating: {rating}/5\n\n"
                
                return {
                    'response': response,
                    'type': 'doctor_list',
                    'data': {'doctors': doctors},
                    'actions': [
                        {'type': 'book_with_doctor', 'label': f"Book with Dr. {doc.get('name')}", 'value': doc.get('id')}
                        for doc in doctors[:3]
                    ] + [{'type': 'view_all', 'label': 'View All Doctors'}]
                }
            else:
                return {
                    'response': f"I couldn't find any doctors{' for ' + specialization if specialization else ''} at the moment. Would you like me to check other specializations?",
                    'type': 'no_doctors_found'
                }
                
        except Exception as e:
            logger.error(f"Error fetching doctor info: {str(e)}")
            return {
                'response': "I'm having trouble accessing doctor information. Please try again later.",
                'type': 'error'
            }
    
    async def _handle_general_chat(self, message: str, user_info: Dict) -> Dict[str, Any]:
        """Handle general chat and greetings"""
        
        message_lower = message.lower().strip()
        
        # Greetings
        if any(greeting in message_lower for greeting in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
            return {
                'response': f"""Hello {user_info.get('full_name', 'there')}! 👋

I'm your MedReserve AI assistant. I can help you with:

🩺 **Book appointments** with doctors
📅 **View your upcoming appointments**
💊 **Check your prescriptions**
📊 **View your medical reports**
👨‍⚕️ **Find doctor information**
💬 **Chat with your assigned doctor**

What would you like to do today?""",
                'type': 'greeting',
                'actions': [
                    {'type': 'book_appointment', 'label': 'Book Appointment'},
                    {'type': 'view_appointments', 'label': 'My Appointments'},
                    {'type': 'view_prescriptions', 'label': 'My Prescriptions'},
                    {'type': 'find_doctors', 'label': 'Find Doctors'}
                ]
            }
        
        # Help requests
        elif any(help_word in message_lower for help_word in ['help', 'what can you do', 'options']):
            return {
                'response': """I'm here to help with your healthcare needs! Here's what I can do:

🩺 **Appointments**
- Book new appointments
- View upcoming appointments
- Cancel or reschedule appointments

💊 **Medications**
- View your current prescriptions
- Set medication reminders
- Find nearby pharmacies

📊 **Medical Records**
- View your medical reports
- Download test results
- Share reports with doctors

👨‍⚕️ **Doctor Services**
- Find doctors by specialization
- Check doctor availability
- Get doctor information

💬 **Communication**
- Chat with your assigned doctor
- Get medical advice
- Emergency assistance

Just tell me what you need help with!""",
                'type': 'help',
                'actions': [
                    {'type': 'book_appointment', 'label': 'Book Appointment'},
                    {'type': 'view_appointments', 'label': 'My Appointments'},
                    {'type': 'view_prescriptions', 'label': 'My Prescriptions'},
                    {'type': 'emergency', 'label': 'Emergency Help'}
                ]
            }
        
        # Default response
        else:
            return {
                'response': """I understand you're looking for assistance. I can help you with:

- Booking appointments
- Viewing your medical information
- Finding doctors
- Managing prescriptions

Could you please tell me specifically what you'd like to do?""",
                'type': 'clarification',
                'actions': [
                    {'type': 'book_appointment', 'label': 'Book Appointment'},
                    {'type': 'view_info', 'label': 'View My Info'},
                    {'type': 'find_doctors', 'label': 'Find Doctors'},
                    {'type': 'help', 'label': 'Show All Options'}
                ]
            }
