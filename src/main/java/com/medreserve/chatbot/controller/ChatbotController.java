package com.medreserve.chatbot.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.beans.factory.annotation.Autowired;
import lombok.extern.slf4j.Slf4j;
import com.medreserve.chatbot.config.ChatbotConfig;

import java.util.HashMap;
import java.util.Map;
import java.util.List;

/**
 * Multilingual Dialogflow Webhook Controller
 * 
 * Handles webhook requests from Dialogflow CX/ES agents and returns
 * localized responses in English, Hindi, and Telugu for medical intents.
 */
@RestController
@RequestMapping("/api/chatbot")
@CrossOrigin("*")
@Slf4j
public class ChatbotController {

    @Autowired
    private ChatbotConfig chatbotConfig;

    /**
     * Main webhook endpoint for Dialogflow
     * 
     * @param request Dialogflow webhook request containing queryResult
     * @return ResponseEntity with fulfillmentText for Dialogflow
     */
    @PostMapping
    public ResponseEntity<Map<String, Object>> handleWebhook(@RequestBody Map<String, Object> request) {
        try {
            if (chatbotConfig.isDebugMode()) {
                log.info("📥 Incoming Dialogflow request: {}", request);
            }

            // Extract queryResult from Dialogflow request
            Map<String, Object> queryResult = (Map<String, Object>) request.get("queryResult");
            if (queryResult == null) {
                log.warn("⚠️ No queryResult found in request");
                return ResponseEntity.badRequest().body(createErrorResponse("Invalid request format"));
            }

            // Extract language code
            String languageCode = (String) queryResult.get("languageCode");
            if (languageCode == null || languageCode.isEmpty()) {
                languageCode = chatbotConfig.getDefaultLanguage();
            }

            // Normalize language code (remove region if present, e.g., "en-US" -> "en")
            languageCode = languageCode.split("-")[0].toLowerCase();

            // Validate supported language
            if (!chatbotConfig.getSupportedLanguages().contains(languageCode)) {
                log.warn("⚠️ Unsupported language: {}, using default: {}", languageCode, chatbotConfig.getDefaultLanguage());
                languageCode = chatbotConfig.getDefaultLanguage();
            }

            // Extract intent information
            Map<String, Object> intent = (Map<String, Object>) queryResult.get("intent");
            String intentName = "Default";
            if (intent != null) {
                intentName = (String) intent.get("displayName");
            }

            if (intentName == null || intentName.isEmpty()) {
                intentName = "Default";
            }

            log.info("🎯 Processing intent: {} in language: {}", intentName, languageCode);

            // Generate localized response
            String fulfillmentText = generateResponse(intentName, languageCode);
            
            // Create Dialogflow response
            Map<String, Object> response = new HashMap<>();
            response.put("fulfillmentText", fulfillmentText);
            
            // Add additional response data for debugging
            if (chatbotConfig.isDebugMode()) {
                Map<String, Object> debugInfo = new HashMap<>();
                debugInfo.put("detectedIntent", intentName);
                debugInfo.put("detectedLanguage", languageCode);
                debugInfo.put("timestamp", System.currentTimeMillis());
                response.put("debugInfo", debugInfo);
            }

            log.info("📤 Sending response: {}", fulfillmentText);
            return ResponseEntity.ok(response);

        } catch (Exception e) {
            log.error("❌ Error processing webhook request", e);
            return ResponseEntity.internalServerError()
                    .body(createErrorResponse("Internal server error: " + e.getMessage()));
        }
    }

    /**
     * Health check endpoint
     */
    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> healthCheck() {
        Map<String, Object> health = new HashMap<>();
        health.put("status", "healthy");
        health.put("service", "MedReserve Multilingual Chatbot");
        health.put("supportedLanguages", chatbotConfig.getSupportedLanguages());
        health.put("timestamp", System.currentTimeMillis());
        return ResponseEntity.ok(health);
    }

    /**
     * Test endpoint for manual testing
     */
    @PostMapping("/test")
    public ResponseEntity<Map<String, Object>> testIntent(
            @RequestParam String intent,
            @RequestParam(defaultValue = "en") String language) {
        
        String response = generateResponse(intent, language);
        Map<String, Object> result = new HashMap<>();
        result.put("intent", intent);
        result.put("language", language);
        result.put("response", response);
        return ResponseEntity.ok(result);
    }

    /**
     * Generate localized response based on intent and language
     */
    private String generateResponse(String intentName, String languageCode) {
        return switch (intentName.toLowerCase()) {
            case "bookappointment", "book.appointment", "appointment.book" -> 
                getBookingResponse(languageCode);
            case "cancelappointment", "cancel.appointment", "appointment.cancel" -> 
                getCancelResponse(languageCode);
            case "listmedicines", "list.medicines", "medicines.list", "medicine.info" -> 
                getMedicineResponse(languageCode);
            case "conditionexplainer", "condition.explainer", "health.condition", "disease.info" -> 
                getConditionResponse(languageCode);
            case "faq", "help", "support" -> 
                getFaqResponse(languageCode);
            default -> 
                getDefaultResponse(languageCode);
        };
    }

    /**
     * Booking appointment responses
     */
    private String getBookingResponse(String lang) {
        return switch (lang) {
            case "hi" -> "आपकी अपॉइंटमेंट बुक हो गई है! डॉक्टर आपसे जल्द ही मिलेंगे। क्या आपको कोई और सहायता चाहिए?";
            case "te" -> "మీ అపాయింట్మెంట్ బుకైంది! డాక్టర్ త్వరలో మిమ్మల్ని కలుస్తారు. మీకు ఇంకా ఏదైనా సహాయం కావాలా?";
            default -> "Your appointment has been booked successfully! The doctor will see you soon. Is there anything else I can help you with?";
        };
    }

    /**
     * Cancel appointment responses
     */
    private String getCancelResponse(String lang) {
        return switch (lang) {
            case "hi" -> "आपकी अपॉइंटमेंट रद्द कर दी गई है। यदि आपको दोबारा अपॉइंटमेंट बुक करनी हो तो कृपया बताएं।";
            case "te" -> "మీ అపాయింట్మెంట్ రద్దు చేయబడింది. మీకు మళ్లీ అపాయింట్మెంట్ బుక్ చేయాలంటే దయచేసి చెప్పండి.";
            default -> "Your appointment has been cancelled successfully. Please let me know if you'd like to book another appointment.";
        };
    }

    /**
     * Medicine information responses
     */
    private String getMedicineResponse(String lang) {
        return switch (lang) {
            case "hi" -> "दवा की जानकारी के लिए कृपया डॉक्टर से परामर्श करें। मैं आपको डॉक्टर से अपॉइंटमेंट बुक करने में मदद कर सकता हूं।";
            case "te" -> "మందుల కోసం దయచేసి డాక్టర్‌ను సంప్రదించండి. నేను మీకు డాక్టర్‌తో అపాయింట్మెంట్ బుక్ చేయడంలో సహాయం చేయగలను.";
            default -> "For medicine information, please consult with a doctor. I can help you book an appointment with a specialist.";
        };
    }

    /**
     * Medical condition explanation responses
     */
    private String getConditionResponse(String lang) {
        return switch (lang) {
            case "hi" -> "अस्थमा एक ऐसी स्थिति है जो सांस लेने को प्रभावित करती है। सटीक जानकारी के लिए कृपया डॉक्टर से मिलें।";
            case "te" -> "ఆస్థమా అనేది శ్వాసపై ప్రభావం చూపించే పరిస్థితి. ఖచ్చితమైన సమాచారం కోసం దయచేసి డాక్టర్‌ను కలవండి.";
            default -> "Asthma is a condition that affects breathing and airways. For accurate information about your specific condition, please consult with a doctor.";
        };
    }

    /**
     * FAQ and help responses
     */
    private String getFaqResponse(String lang) {
        return switch (lang) {
            case "hi" -> "आप 'अपॉइंटमेंट रद्द करें' कहकर अपॉइंटमेंट रद्द कर सकते हैं। अन्य सहायता के लिए 'मदद' कहें।";
            case "te" -> "మీరు 'అపాయింట్మెంట్ రద్దు చేయండి' అని చెప్పి అపాయింట్మెంట్ రద్దు చేయవచ్చు. ఇతర సహాయం కోసం 'సహాయం' అని చెప్పండి.";
            default -> "You can cancel appointments by saying 'Cancel appointment'. For other help, just say 'help' or ask me anything about MedReserve services.";
        };
    }

    /**
     * Default response for unrecognized intents
     */
    private String getDefaultResponse(String lang) {
        return switch (lang) {
            case "hi" -> "मुझे खुशी होगी आपकी मदद करने में! मैं अपॉइंटमेंट बुकिंग, रद्दीकरण, और स्वास्थ्य जानकारी में सहायता कर सकता हूं।";
            case "te" -> "మీకు సహాయం చేయడంలో నేను సంతోషిస్తాను! నేను అపాయింట్మెంట్ బుకింగ్, రద్దు మరియు ఆరోగ్య సమాచారంలో సహాయం చేయగలను.";
            default -> "I'm here to help you with MedReserve services! I can assist with appointment booking, cancellations, and general health information.";
        };
    }

    /**
     * Create error response
     */
    private Map<String, Object> createErrorResponse(String message) {
        Map<String, Object> error = new HashMap<>();
        error.put("fulfillmentText", "Sorry, I encountered an error. Please try again.");
        error.put("error", message);
        return error;
    }
}
