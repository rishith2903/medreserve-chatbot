package com.medreserve.chatbot.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;
import lombok.Data;

import java.util.List;
import java.util.ArrayList;

/**
 * Configuration properties for the chatbot service
 */
@Configuration
@ConfigurationProperties(prefix = "chatbot")
@Data
public class ChatbotConfig {
    
    /**
     * List of supported language codes (e.g., ["en", "hi", "te"])
     */
    private List<String> supportedLanguages = List.of("en", "hi", "te");
    
    /**
     * Default language code when language detection fails
     */
    private String defaultLanguage = "en";
    
    /**
     * Session timeout duration
     */
    private String sessionTimeout = "30m";
    
    /**
     * Debug mode flag for additional logging
     */
    private boolean debugMode = false;
}
