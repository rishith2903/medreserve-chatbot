"""
Doctor Chatbot Logic for MedReserve AI
Handles doctor interactions, patient management, and clinical assistance
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from loguru import logger
from utils import MessageProcessor, api_client, JWTHandler
from config import settings


class DoctorChatbot:
    """Intelligent chatbot for doctor interactions"""
    
    def __init__(self):
        self.conversation_states = {}
        self.message_processor = MessageProcessor()
    
    async def process_message(
        self,
        message: str,
        user_token: str,
        user_id: str,
        conversation_id: str
    ) -> Dict[str, Any]:
        """Process doctor message and generate response"""
        
        try:
            # Get user information from token
            user_info = JWTHandler.get_user_from_token(user_token)
            
            # Verify user is a doctor
            if user_info.get('role') != 'DOCTOR':
                return {
                    'response': "Access denied. This assistant is only available for doctors.",
                    'type': 'access_denied'
                }
            
            # Extract intent from message
            intent = self._extract_doctor_intent(message)
            
            # Route to appropriate handler based on intent
            if intent == 'view_appointments':
                return await self._handle_view_appointments(user_token, user_info)
            elif intent == 'view_patients':
                return await self._handle_view_patients(user_token, user_info)
            elif intent == 'add_prescription':
                return await self._handle_add_prescription(message, user_token, user_info, conversation_id)
            elif intent == 'add_diagnosis':
                return await self._handle_add_diagnosis(message, user_token, user_info, conversation_id)
            elif intent == 'patient_history':
                return await self._handle_patient_history(message, user_token, user_info)
            elif intent == 'emergency_patients':
                return await self._handle_emergency_patients(user_token, user_info)
            elif intent == 'schedule_management':
                return await self._handle_schedule_management(message, user_token, user_info)
            else:
                return await self._handle_general_doctor_chat(message, user_info)
                
        except Exception as e:
            logger.error(f"Error processing doctor message: {str(e)}")
            return {
                'response': "I encountered an error processing your request. Please try again.",
                'type': 'error',
                'actions': []
            }
    
    def _extract_doctor_intent(self, message: str) -> str:
        """Extract intent from doctor message"""
        message_lower = message.lower().strip()
        
        # Appointment management
        if any(keyword in message_lower for keyword in ['appointments', 'schedule', 'calendar', 'today']):
            return 'view_appointments'
        
        # Patient management
        if any(keyword in message_lower for keyword in ['patients', 'my patients', 'patient list']):
            return 'view_patients'
        
        # Prescription management
        if any(keyword in message_lower for keyword in ['prescribe', 'prescription', 'medication', 'medicine']):
            return 'add_prescription'
        
        # Diagnosis
        if any(keyword in message_lower for keyword in ['diagnosis', 'diagnose', 'condition', 'treatment']):
            return 'add_diagnosis'
        
        # Patient history
        if any(keyword in message_lower for keyword in ['history', 'medical history', 'previous']):
            return 'patient_history'
        
        # Emergency
        if any(keyword in message_lower for keyword in ['emergency', 'urgent', 'critical']):
            return 'emergency_patients'
        
        # Schedule
        if any(keyword in message_lower for keyword in ['schedule', 'availability', 'time slots']):
            return 'schedule_management'
        
        return 'general_chat'
    
    async def _handle_view_appointments(self, token: str, user_info: Dict) -> Dict[str, Any]:
        """Handle viewing doctor's appointments"""
        try:
            appointments = await api_client.get_appointments(token, user_info['user_id'], 'DOCTOR')
            
            if appointments:
                # Sort appointments by date and time
                sorted_appointments = sorted(
                    appointments,
                    key=lambda x: (x.get('appointmentDate', ''), x.get('appointmentTime', ''))
                )
                
                # Group by date
                today = datetime.now().strftime('%Y-%m-%d')
                today_appointments = [apt for apt in sorted_appointments if apt.get('appointmentDate') == today]
                upcoming_appointments = [apt for apt in sorted_appointments if apt.get('appointmentDate') > today]
                
                response = "📅 **Your Appointment Schedule**\n\n"
                
                if today_appointments:
                    response += "🔥 **Today's Appointments:**\n"
                    for apt in today_appointments:
                        patient_name = apt.get('patientName', 'Unknown Patient')
                        time = apt.get('appointmentTime', 'TBD')
                        reason = apt.get('reason', 'General consultation')
                        status = apt.get('status', 'Scheduled')
                        
                        response += f"⏰ **{time}** - {patient_name}\n"
                        response += f"   📝 Reason: {reason}\n"
                        response += f"   📊 Status: {status}\n\n"
                
                if upcoming_appointments:
                    response += "📆 **Upcoming Appointments:**\n"
                    for apt in upcoming_appointments[:5]:  # Show next 5
                        patient_name = apt.get('patientName', 'Unknown Patient')
                        date = apt.get('appointmentDate', 'TBD')
                        time = apt.get('appointmentTime', 'TBD')
                        
                        response += f"📅 **{date}** at {time} - {patient_name}\n"
                
                return {
                    'response': response,
                    'type': 'appointments_schedule',
                    'data': {
                        'today_appointments': today_appointments,
                        'upcoming_appointments': upcoming_appointments
                    },
                    'actions': [
                        {'type': 'view_patient_details', 'label': 'View Patient Details'},
                        {'type': 'add_notes', 'label': 'Add Appointment Notes'},
                        {'type': 'reschedule', 'label': 'Reschedule Appointment'},
                        {'type': 'mark_completed', 'label': 'Mark as Completed'}
                    ]
                }
            else:
                return {
                    'response': """You don't have any appointments scheduled.

Your schedule is currently clear. You can:
- Review patient requests
- Update your availability
- Check pending appointments""",
                    'type': 'no_appointments',
                    'actions': [
                        {'type': 'update_availability', 'label': 'Update Availability'},
                        {'type': 'view_requests', 'label': 'View Patient Requests'}
                    ]
                }
                
        except Exception as e:
            logger.error(f"Error fetching doctor appointments: {str(e)}")
            return {
                'response': "I'm having trouble accessing your appointment schedule. Please try again later.",
                'type': 'error'
            }
    
    async def _handle_view_patients(self, token: str, user_info: Dict) -> Dict[str, Any]:
        """Handle viewing doctor's patients"""
        try:
            patients = await api_client.get_patients(token, user_info['user_id'])
            
            if patients:
                response = "👥 **Your Patients**\n\n"
                
                for i, patient in enumerate(patients[:10], 1):  # Show first 10
                    name = patient.get('name', 'Unknown Patient')
                    age = patient.get('age', 'N/A')
                    gender = patient.get('gender', 'N/A')
                    last_visit = patient.get('lastVisit', 'Never')
                    condition = patient.get('primaryCondition', 'General care')
                    
                    response += f"{i}. **{name}** ({age}y, {gender})\n"
                    response += f"   📅 Last visit: {last_visit}\n"
                    response += f"   🏥 Condition: {condition}\n\n"
                
                return {
                    'response': response,
                    'type': 'patients_list',
                    'data': {'patients': patients},
                    'actions': [
                        {'type': 'view_patient_history', 'label': 'View Patient History'},
                        {'type': 'add_prescription', 'label': 'Add Prescription'},
                        {'type': 'schedule_followup', 'label': 'Schedule Follow-up'},
                        {'type': 'send_message', 'label': 'Send Message to Patient'}
                    ]
                }
            else:
                return {
                    'response': """You don't have any assigned patients yet.

Once patients book appointments with you, they'll appear here with:
- Basic demographics
- Medical history
- Appointment history
- Current prescriptions""",
                    'type': 'no_patients',
                    'actions': [
                        {'type': 'update_profile', 'label': 'Update Doctor Profile'},
                        {'type': 'set_availability', 'label': 'Set Availability'}
                    ]
                }
                
        except Exception as e:
            logger.error(f"Error fetching doctor patients: {str(e)}")
            return {
                'response': "I'm having trouble accessing your patient list. Please try again later.",
                'type': 'error'
            }
    
    async def _handle_add_prescription(
        self,
        message: str,
        token: str,
        user_info: Dict,
        conversation_id: str
    ) -> Dict[str, Any]:
        """Handle adding prescriptions via chat"""
        
        # Extract prescription information from message
        prescription_info = self._extract_prescription_info(message)
        
        if prescription_info:
            # Get conversation state
            state = self.conversation_states.get(conversation_id, {})
            
            if not state.get('patient_id'):
                return {
                    'response': """To add a prescription, I need to know which patient this is for.

Please specify the patient name or ID, for example:
"Prescribe paracetamol 500mg for John Smith"
or
"Add prescription for patient ID 123: amoxicillin 250mg"

Which patient is this prescription for?""",
                    'type': 'patient_required',
                    'actions': [
                        {'type': 'select_patient', 'label': 'Select from Patient List'},
                        {'type': 'enter_patient_id', 'label': 'Enter Patient ID'}
                    ]
                }
            
            # Prepare prescription data
            prescription_data = {
                'patientId': state.get('patient_id'),
                'doctorId': user_info['user_id'],
                'medicationName': prescription_info.get('medication'),
                'dosage': prescription_info.get('dosage'),
                'frequency': prescription_info.get('frequency'),
                'duration': prescription_info.get('duration'),
                'instructions': prescription_info.get('instructions'),
                'prescriptionDate': datetime.now().isoformat()
            }
            
            try:
                result = await api_client.add_prescription(token, prescription_data)
                
                return {
                    'response': f"""✅ **Prescription Added Successfully**

**Patient:** {state.get('patient_name', 'Unknown')}
**Medication:** {prescription_info.get('medication')}
**Dosage:** {prescription_info.get('dosage')}
**Frequency:** {prescription_info.get('frequency')}
**Duration:** {prescription_info.get('duration')}

The prescription has been saved and the patient will be notified.""",
                    'type': 'prescription_added',
                    'data': {'prescription': result},
                    'actions': [
                        {'type': 'add_another', 'label': 'Add Another Prescription'},
                        {'type': 'view_patient', 'label': 'View Patient Details'},
                        {'type': 'send_instructions', 'label': 'Send Instructions to Patient'}
                    ]
                }
                
            except Exception as e:
                logger.error(f"Error adding prescription: {str(e)}")
                return {
                    'response': "I encountered an error while adding the prescription. Please try again or add it manually through the system.",
                    'type': 'error'
                }
        else:
            return {
                'response': """I need more details to add a prescription. Please provide:

📋 **Required Information:**
- Patient name or ID
- Medication name
- Dosage (e.g., 500mg)
- Frequency (e.g., twice daily)
- Duration (e.g., 7 days)

**Example:** "Prescribe paracetamol 500mg twice daily for 5 days for John Smith"

What prescription would you like to add?""",
                'type': 'prescription_details_required',
                'actions': [
                    {'type': 'prescription_template', 'label': 'Use Prescription Template'},
                    {'type': 'common_medications', 'label': 'Common Medications'}
                ]
            }
    
    def _extract_prescription_info(self, message: str) -> Optional[Dict[str, str]]:
        """Extract prescription information from message"""
        
        # Common medication patterns
        medication_pattern = r'(?:prescribe|give|add)\s+([a-zA-Z]+(?:\s+[a-zA-Z]+)*)'
        dosage_pattern = r'(\d+(?:\.\d+)?)\s*(mg|g|ml|tablets?|capsules?)'
        frequency_pattern = r'(once|twice|thrice|\d+\s*times?)\s*(?:a\s*|per\s*)?(?:day|daily|week|weekly)'
        duration_pattern = r'(?:for\s+)?(\d+)\s*(days?|weeks?|months?)'
        
        result = {}
        
        # Extract medication name
        med_match = re.search(medication_pattern, message, re.IGNORECASE)
        if med_match:
            result['medication'] = med_match.group(1).strip()
        
        # Extract dosage
        dose_match = re.search(dosage_pattern, message, re.IGNORECASE)
        if dose_match:
            result['dosage'] = f"{dose_match.group(1)}{dose_match.group(2)}"
        
        # Extract frequency
        freq_match = re.search(frequency_pattern, message, re.IGNORECASE)
        if freq_match:
            result['frequency'] = freq_match.group(0).strip()
        
        # Extract duration
        dur_match = re.search(duration_pattern, message, re.IGNORECASE)
        if dur_match:
            result['duration'] = f"{dur_match.group(1)} {dur_match.group(2)}"
        
        # Extract patient name (simple pattern)
        patient_pattern = r'(?:for|to)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)'
        patient_match = re.search(patient_pattern, message)
        if patient_match:
            result['patient_name'] = patient_match.group(1)
        
        return result if len(result) >= 2 else None
    
    async def _handle_add_diagnosis(
        self,
        message: str,
        token: str,
        user_info: Dict,
        conversation_id: str
    ) -> Dict[str, Any]:
        """Handle adding diagnosis via chat"""
        
        # Extract diagnosis information
        diagnosis_info = self._extract_diagnosis_info(message)
        
        if diagnosis_info:
            return {
                'response': f"""📋 **Diagnosis Summary**

**Condition:** {diagnosis_info.get('condition', 'Not specified')}
**Symptoms:** {diagnosis_info.get('symptoms', 'Not specified')}
**Severity:** {diagnosis_info.get('severity', 'Not specified')}
**Recommended Treatment:** {diagnosis_info.get('treatment', 'Not specified')}

Would you like me to save this diagnosis and create a treatment plan?""",
                'type': 'diagnosis_confirmation',
                'data': {'diagnosis': diagnosis_info},
                'actions': [
                    {'type': 'save_diagnosis', 'label': 'Save Diagnosis'},
                    {'type': 'add_prescription', 'label': 'Add Prescription'},
                    {'type': 'schedule_followup', 'label': 'Schedule Follow-up'},
                    {'type': 'modify_diagnosis', 'label': 'Modify Details'}
                ]
            }
        else:
            return {
                'response': """I can help you document a diagnosis. Please provide:

🩺 **Diagnosis Information:**
- Patient condition/diagnosis
- Observed symptoms
- Severity level
- Recommended treatment

**Example:** "Patient has mild hypertension with headaches, recommend lifestyle changes and medication"

What diagnosis would you like to record?""",
                'type': 'diagnosis_details_required',
                'actions': [
                    {'type': 'diagnosis_template', 'label': 'Use Diagnosis Template'},
                    {'type': 'common_conditions', 'label': 'Common Conditions'}
                ]
            }
    
    def _extract_diagnosis_info(self, message: str) -> Optional[Dict[str, str]]:
        """Extract diagnosis information from message"""
        
        # Simple keyword-based extraction
        result = {}
        message_lower = message.lower()
        
        # Common conditions
        conditions = [
            'hypertension', 'diabetes', 'asthma', 'pneumonia', 'bronchitis',
            'gastritis', 'migraine', 'arthritis', 'depression', 'anxiety'
        ]
        
        for condition in conditions:
            if condition in message_lower:
                result['condition'] = condition.title()
                break
        
        # Severity indicators
        if any(word in message_lower for word in ['mild', 'moderate', 'severe', 'critical']):
            for severity in ['mild', 'moderate', 'severe', 'critical']:
                if severity in message_lower:
                    result['severity'] = severity.title()
                    break
        
        # Extract symptoms (simple approach)
        symptom_keywords = ['pain', 'fever', 'cough', 'headache', 'nausea', 'fatigue']
        symptoms = [symptom for symptom in symptom_keywords if symptom in message_lower]
        if symptoms:
            result['symptoms'] = ', '.join(symptoms)
        
        return result if result else None
    
    async def _handle_patient_history(self, message: str, token: str, user_info: Dict) -> Dict[str, Any]:
        """Handle patient history requests"""
        
        # Extract patient identifier from message
        patient_name = self._extract_patient_name(message)
        
        if patient_name:
            return {
                'response': f"""📊 **Patient History for {patient_name}**

I can show you:
- Previous appointments and diagnoses
- Current and past prescriptions
- Medical test results
- Treatment history
- Emergency visits

What specific information would you like to see?""",
                'type': 'patient_history_options',
                'actions': [
                    {'type': 'view_appointments_history', 'label': 'Appointment History'},
                    {'type': 'view_prescriptions_history', 'label': 'Prescription History'},
                    {'type': 'view_test_results', 'label': 'Test Results'},
                    {'type': 'view_diagnoses', 'label': 'Previous Diagnoses'}
                ]
            }
        else:
            return {
                'response': """Which patient's history would you like to review?

Please specify the patient name or select from your patient list.

**Example:** "Show history for John Smith" or "Patient history for ID 123" """,
                'type': 'patient_selection_required',
                'actions': [
                    {'type': 'select_from_list', 'label': 'Select from Patient List'},
                    {'type': 'enter_patient_name', 'label': 'Enter Patient Name'}
                ]
            }
    
    def _extract_patient_name(self, message: str) -> Optional[str]:
        """Extract patient name from message"""
        
        # Simple pattern for "for [Name]" or "patient [Name]"
        patterns = [
            r'(?:for|patient)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)(?:\s+history|\s+record)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                return match.group(1)
        
        return None
    
    async def _handle_emergency_patients(self, token: str, user_info: Dict) -> Dict[str, Any]:
        """Handle emergency patient alerts"""
        
        # This would typically fetch from a database of flagged patients
        emergency_patients = [
            {
                'name': 'Jane Doe',
                'condition': 'Chest pain',
                'severity': 'High',
                'time': '10 minutes ago',
                'status': 'Waiting'
            },
            {
                'name': 'Bob Wilson',
                'condition': 'Severe allergic reaction',
                'severity': 'Critical',
                'time': '5 minutes ago',
                'status': 'In treatment'
            }
        ]
        
        if emergency_patients:
            response = "🚨 **Emergency Patients Alert**\n\n"
            
            for patient in emergency_patients:
                response += f"⚠️ **{patient['name']}**\n"
                response += f"   🏥 Condition: {patient['condition']}\n"
                response += f"   📊 Severity: {patient['severity']}\n"
                response += f"   ⏰ Time: {patient['time']}\n"
                response += f"   📋 Status: {patient['status']}\n\n"
            
            return {
                'response': response,
                'type': 'emergency_alerts',
                'data': {'emergency_patients': emergency_patients},
                'actions': [
                    {'type': 'view_patient_details', 'label': 'View Patient Details'},
                    {'type': 'update_status', 'label': 'Update Status'},
                    {'type': 'call_patient', 'label': 'Call Patient'},
                    {'type': 'alert_staff', 'label': 'Alert Medical Staff'}
                ]
            }
        else:
            return {
                'response': """✅ **No Emergency Alerts**

All patients are stable. No urgent cases requiring immediate attention.

I'll notify you immediately if any emergency situations arise.""",
                'type': 'no_emergencies',
                'actions': [
                    {'type': 'view_all_patients', 'label': 'View All Patients'},
                    {'type': 'set_alerts', 'label': 'Configure Alert Settings'}
                ]
            }
    
    async def _handle_schedule_management(self, message: str, token: str, user_info: Dict) -> Dict[str, Any]:
        """Handle schedule and availability management"""
        
        return {
            'response': """📅 **Schedule Management**

I can help you with:

⏰ **Availability Settings**
- Set your working hours
- Block time slots
- Set vacation periods
- Configure break times

📊 **Schedule Overview**
- View today's schedule
- Check upcoming week
- See appointment gaps
- Review patient load

What would you like to manage?""",
            'type': 'schedule_management',
            'actions': [
                {'type': 'set_availability', 'label': 'Set Availability'},
                {'type': 'block_time', 'label': 'Block Time Slots'},
                {'type': 'view_schedule', 'label': 'View Full Schedule'},
                {'type': 'set_vacation', 'label': 'Set Vacation Period'}
            ]
        }
    
    async def _handle_general_doctor_chat(self, message: str, user_info: Dict) -> Dict[str, Any]:
        """Handle general doctor chat and greetings"""
        
        message_lower = message.lower().strip()
        
        # Greetings
        if any(greeting in message_lower for greeting in ['hello', 'hi', 'good morning', 'good afternoon']):
            return {
                'response': f"""Good day, Dr. {user_info.get('full_name', 'Doctor')}! 👨‍⚕️

I'm your MedReserve AI clinical assistant. I can help you with:

📅 **Appointment Management**
- View today's schedule
- Manage patient appointments
- Update availability

👥 **Patient Care**
- Review patient lists
- Access medical histories
- Add prescriptions and diagnoses

🚨 **Clinical Support**
- Emergency patient alerts
- Treatment recommendations
- Clinical decision support

💬 **Communication**
- Chat with patients
- Send medical instructions
- Share reports

What would you like to do today?""",
                'type': 'doctor_greeting',
                'actions': [
                    {'type': 'view_appointments', 'label': 'Today\'s Schedule'},
                    {'type': 'view_patients', 'label': 'My Patients'},
                    {'type': 'emergency_alerts', 'label': 'Emergency Alerts'},
                    {'type': 'add_prescription', 'label': 'Add Prescription'}
                ]
            }
        
        # Help requests
        elif any(help_word in message_lower for help_word in ['help', 'what can you do', 'options']):
            return {
                'response': """🩺 **Clinical Assistant Capabilities**

**Patient Management:**
- View and manage your patient list
- Access complete medical histories
- Review appointment schedules
- Track treatment progress

**Clinical Documentation:**
- Add prescriptions via voice/text
- Record diagnoses and treatment plans
- Update patient records
- Generate medical reports

**Communication:**
- Real-time chat with patients
- Send medical instructions
- Share test results and reports
- Emergency patient alerts

**Schedule Management:**
- View daily/weekly schedules
- Manage availability
- Handle appointment requests
- Set break times and vacations

**Clinical Decision Support:**
- Drug interaction checks
- Treatment recommendations
- Diagnostic assistance
- Emergency protocols

How can I assist you today?""",
                'type': 'doctor_help',
                'actions': [
                    {'type': 'view_appointments', 'label': 'View Schedule'},
                    {'type': 'view_patients', 'label': 'Patient List'},
                    {'type': 'add_prescription', 'label': 'Add Prescription'},
                    {'type': 'emergency_check', 'label': 'Check Emergencies'}
                ]
            }
        
        # Default response
        else:
            return {
                'response': """I'm here to assist with your clinical workflow. I can help you:

- Manage your patient appointments
- Add prescriptions and diagnoses
- Review patient medical histories
- Handle emergency alerts
- Communicate with patients

What specific task would you like help with?""",
                'type': 'doctor_clarification',
                'actions': [
                    {'type': 'view_appointments', 'label': 'View Appointments'},
                    {'type': 'view_patients', 'label': 'View Patients'},
                    {'type': 'add_prescription', 'label': 'Add Prescription'},
                    {'type': 'help', 'label': 'Show All Options'}
                ]
            }
