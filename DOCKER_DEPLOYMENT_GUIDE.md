# 🐳 MedReserve AI Chatbot Docker Deployment Guide

## 🚨 **PyJWT Fix Applied**

**Issue Resolved**: `ModuleNotFoundError: No module named 'jwt'`

### **What Was Fixed:**
1. ✅ Added `PyJWT>=2.8.0` to requirements.txt
2. ✅ Enhanced Dockerfile with package verification
3. ✅ Created comprehensive build and test scripts
4. ✅ Added production-ready Dockerfile variant

## 🛠️ **Quick Fix Summary**

The error occurred because:
- Your code imports `jwt` directly: `import jwt`
- But you only had `python-jose[cryptography]` in requirements.txt
- `python-jose` provides JWT functionality but under `jose` import name
- **Solution**: Added `PyJWT>=2.8.0` which provides the `jwt` module

## 🔍 Original Problem
```
error: failed to solve: failed to read dockerfile: open Dockerfile: no such file or directory
```

**Root Cause:** Missing Dockerfile in the chatbot directory.

**Solution:** Created complete Docker configuration files.

## 📁 Required Files (Now Created)

```
backend/chatbot/
├── Dockerfile              ✅ Created
├── docker-compose.yml      ✅ Created  
├── .dockerignore           ✅ Created
├── start.sh               ✅ Created
├── .env.example           ✅ Exists
└── requirements.txt       ✅ Exists
```

## 🚀 Step-by-Step Deployment Instructions

### 1. **Navigate to Chatbot Directory**
```bash
cd backend/chatbot
```

### 2. **Verify Files Exist**
```bash
ls -la
# Should show: Dockerfile, docker-compose.yml, .dockerignore, etc.
```

### 3. **Configure Environment**
```bash
# Copy environment template
cp .env.example .env

# Edit configuration (important!)
nano .env
```

**Required Environment Variables:**
```bash
# Application Settings
DEBUG=false
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8001

# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/medreserve

# Spring Boot Backend Integration
SPRING_BOOT_BASE_URL=http://localhost:8080/api

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_ALGORITHM=HS256

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000","http://localhost:8080"]
```

### 4. **Build Docker Image**

#### Option A: Single Container Build
```bash
# Build the chatbot image
docker build -t medreserve-chatbot .

# Run the container
docker run -d \
  --name medreserve-chatbot \
  -p 8001:8001 \
  --env-file .env \
  medreserve-chatbot
```

#### Option B: Docker Compose (Recommended)
```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f chatbot

# Stop services
docker-compose down
```

### 5. **Verify Deployment**
```bash
# Check container status
docker ps

# Test health endpoint
curl http://localhost:8001/health

# Check logs
docker logs medreserve-chatbot
```

## 🔧 Troubleshooting Common Issues

### Issue 1: Port Already in Use
```bash
# Find process using port 8001
lsof -i :8001

# Kill process or change port in .env
PORT=8002
```

### Issue 2: Permission Denied
```bash
# Make start script executable
chmod +x start.sh

# Fix Docker permissions
sudo chown -R $USER:$USER .
```

### Issue 3: Environment Variables Not Loading
```bash
# Verify .env file exists and has correct format
cat .env

# Rebuild with no cache
docker build --no-cache -t medreserve-chatbot .
```

### Issue 4: Database Connection Failed
```bash
# Update DATABASE_URL in .env
DATABASE_URL=postgresql://username:password@host:port/database

# Or use Docker network
DATABASE_URL=postgresql://postgres:password@db:5432/medreserve
```

## 🌐 Production Deployment

### 1. **Environment Configuration**
```bash
# Production .env
DEBUG=false
ENVIRONMENT=production
JWT_SECRET_KEY=super-secure-production-key
CORS_ORIGINS=["https://yourdomain.com"]
```

### 2. **Docker Compose for Production**
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  chatbot:
    build: .
    ports:
      - "8001:8001"
    environment:
      - DEBUG=false
      - ENVIRONMENT=production
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### 3. **Deploy to Production**
```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up -d

# Monitor logs
docker-compose -f docker-compose.prod.yml logs -f
```

## 📊 Monitoring & Maintenance

### Health Checks
```bash
# Application health
curl http://localhost:8001/health

# Container health
docker inspect --format='{{.State.Health.Status}}' medreserve-chatbot
```

### Log Management
```bash
# View real-time logs
docker-compose logs -f chatbot

# View specific number of lines
docker-compose logs --tail=100 chatbot

# Export logs
docker-compose logs chatbot > chatbot.log
```

### Updates & Maintenance
```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Clean up old images
docker image prune -f
```

## 🔐 Security Best Practices

### 1. **Environment Security**
- Never commit `.env` files to version control
- Use strong, unique JWT secret keys
- Limit CORS origins to trusted domains
- Use HTTPS in production

### 2. **Container Security**
- Run as non-root user (already configured)
- Keep base images updated
- Scan for vulnerabilities regularly
- Limit container resources

### 3. **Network Security**
- Use Docker networks for service communication
- Expose only necessary ports
- Implement proper firewall rules
- Use reverse proxy (nginx) in production

## 🎯 Quick Commands Reference

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild after changes
docker-compose build --no-cache

# Scale services
docker-compose up -d --scale chatbot=3

# Execute commands in container
docker-compose exec chatbot bash

# View container stats
docker stats medreserve-chatbot
```

## ✅ Deployment Checklist

- [ ] Dockerfile exists and is properly configured
- [ ] docker-compose.yml is set up
- [ ] .env file is configured with correct values
- [ ] Port 8001 is available
- [ ] Database connection is configured
- [ ] JWT secret key is set
- [ ] CORS origins are configured
- [ ] Health check endpoint responds
- [ ] Logs show successful startup
- [ ] API endpoints are accessible

## 🎉 Success Indicators

When deployment is successful, you should see:

1. **Container Running:**
   ```bash
   docker ps
   # Shows medreserve-chatbot container as "Up"
   ```

2. **Health Check Passing:**
   ```bash
   curl http://localhost:8001/health
   # Returns: {"status": "healthy", ...}
   ```

3. **API Documentation Available:**
   ```bash
   # Visit: http://localhost:8001/docs
   ```

4. **WebSocket Connection Ready:**
   ```bash
   # WebSocket endpoint: ws://localhost:8001/chat/ws/{user_id}
   ```

---

**🎊 Your MedReserve AI Chatbot is now successfully deployed with Docker!**
