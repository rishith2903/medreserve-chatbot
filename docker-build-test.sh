#!/bin/bash

# MedReserve AI Chatbot - Docker Build and Test Script
# This script builds the Docker image and tests for common deployment issues

set -e  # Exit on any error

echo "🚀 MedReserve AI Chatbot - Docker Build & Test"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="medreserve-chatbot"
TAG="latest"
CONTAINER_NAME="medreserve-chatbot-test"

echo -e "${BLUE}📋 Build Configuration:${NC}"
echo "  Image: $IMAGE_NAME:$TAG"
echo "  Container: $CONTAINER_NAME"
echo ""

# Step 1: Clean up any existing containers/images
echo -e "${YELLOW}🧹 Cleaning up existing containers and images...${NC}"
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true
docker rmi $IMAGE_NAME:$TAG 2>/dev/null || true

# Step 2: Build the Docker image
echo -e "${BLUE}🔨 Building Docker image...${NC}"
docker build -t $IMAGE_NAME:$TAG . --no-cache

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Docker image built successfully!${NC}"
else
    echo -e "${RED}❌ Docker build failed!${NC}"
    exit 1
fi

# Step 3: Test package installations
echo -e "${BLUE}🧪 Testing package installations...${NC}"
docker run --rm $IMAGE_NAME:$TAG python -c "
import sys
print('🐍 Python version:', sys.version)

# Test critical imports
try:
    import jwt
    print('✅ PyJWT imported successfully')
    print('   Version:', jwt.__version__ if hasattr(jwt, '__version__') else 'Unknown')
except ImportError as e:
    print('❌ PyJWT import failed:', e)
    sys.exit(1)

try:
    import jose
    print('✅ python-jose imported successfully')
except ImportError as e:
    print('❌ python-jose import failed:', e)
    sys.exit(1)

try:
    import fastapi
    print('✅ FastAPI imported successfully')
    print('   Version:', fastapi.__version__)
except ImportError as e:
    print('❌ FastAPI import failed:', e)
    sys.exit(1)

try:
    import uvicorn
    print('✅ Uvicorn imported successfully')
    print('   Version:', uvicorn.__version__)
except ImportError as e:
    print('❌ Uvicorn import failed:', e)
    sys.exit(1)

try:
    import passlib
    print('✅ Passlib imported successfully')
except ImportError as e:
    print('❌ Passlib import failed:', e)
    sys.exit(1)

print('🎉 All critical packages imported successfully!')
"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Package installation test passed!${NC}"
else
    echo -e "${RED}❌ Package installation test failed!${NC}"
    exit 1
fi

# Step 4: Test application startup (quick test)
echo -e "${BLUE}🚀 Testing application startup...${NC}"
docker run -d --name $CONTAINER_NAME -p 8001:8001 $IMAGE_NAME:$TAG

# Wait for container to start
sleep 5

# Check if container is running
if docker ps | grep -q $CONTAINER_NAME; then
    echo -e "${GREEN}✅ Container started successfully!${NC}"
    
    # Test health endpoint if available
    echo -e "${BLUE}🏥 Testing health endpoint...${NC}"
    if curl -f http://localhost:8001/health 2>/dev/null; then
        echo -e "${GREEN}✅ Health endpoint responding!${NC}"
    else
        echo -e "${YELLOW}⚠️  Health endpoint not responding (this might be normal if not implemented)${NC}"
    fi
    
    # Show container logs
    echo -e "${BLUE}📋 Container logs (last 20 lines):${NC}"
    docker logs --tail 20 $CONTAINER_NAME
    
else
    echo -e "${RED}❌ Container failed to start!${NC}"
    echo -e "${BLUE}📋 Container logs:${NC}"
    docker logs $CONTAINER_NAME
    exit 1
fi

# Step 5: Cleanup
echo -e "${YELLOW}🧹 Cleaning up test container...${NC}"
docker stop $CONTAINER_NAME
docker rm $CONTAINER_NAME

echo ""
echo -e "${GREEN}🎉 Docker build and test completed successfully!${NC}"
echo -e "${BLUE}📦 Image ready: $IMAGE_NAME:$TAG${NC}"
echo ""
echo -e "${YELLOW}💡 Next steps:${NC}"
echo "  1. Run: docker run -p 8001:8001 $IMAGE_NAME:$TAG"
echo "  2. Test: curl http://localhost:8001/health"
echo "  3. Deploy to your preferred platform"
