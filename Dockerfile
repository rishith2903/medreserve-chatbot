# ---------- Build Stage ----------
FROM maven:3.9.6-eclipse-temurin-17 AS build

# Set working directory
WORKDIR /app

# Copy pom.xml and download dependencies (caching layer)
COPY pom.xml .
RUN mvn dependency:go-offline

# Copy full source code
COPY src ./src

# Build the Spring Boot application, skip tests
RUN mvn clean package -DskipTests


# ---------- Runtime Stage ----------
FROM openjdk:17-jdk-slim

# Set working directory
WORKDIR /app

# Create non-root user for better security
RUN groupadd -r chatbot && useradd -r -g chatbot chatbot

# Install curl for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy the built JAR from build stage
COPY --from=build /app/target/medreserve-chatbot.jar app.jar

# Change ownership to non-root user
RUN chown chatbot:chatbot app.jar

# Switch to non-root user
USER chatbot

# Expose port (uses PORT env var, defaults to 8080 in production)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:${PORT:-8080}/actuator/health || exit 1

# Run the application
CMD ["java", "-jar", "app.jar"]
