package com.medreserve.chatbot;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;
import org.springframework.context.annotation.Bean;

/**
 * Main application class for MedReserve Multilingual Chatbot
 * 
 * This Spring Boot application provides a Dialogflow webhook handler
 * that supports multilingual responses in English, Hindi, and Telugu.
 */
@SpringBootApplication
public class ChatbotApplication {

    public static void main(String[] args) {
        SpringApplication.run(ChatbotApplication.class, args);
        System.out.println("🤖 MedReserve Multilingual Chatbot started successfully!");
        System.out.println("📡 Webhook endpoint: /api/chatbot");
        System.out.println("🌐 Supported languages: English (en), Hindi (hi), Telugu (te)");
    }

    /**
     * Configure CORS for cross-origin requests from Dialogflow and frontend
     */
    @Bean
    public WebMvcConfigurer corsConfigurer() {
        return new WebMvcConfigurer() {
            @Override
            public void addCorsMappings(CorsRegistry registry) {
                registry.addMapping("/api/**")
                        .allowedOriginPatterns("*")
                        .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS")
                        .allowedHeaders("*")
                        .allowCredentials(false)
                        .maxAge(3600);
            }
        };
    }
}
