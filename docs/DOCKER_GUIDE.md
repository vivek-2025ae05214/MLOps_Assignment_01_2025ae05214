# Docker Containerization Guide - Heart Disease Prediction API

## Overview

This guide explains how to build, run, and test a Docker container for the Heart Disease Prediction FastAPI application.

---

## 📋 Prerequisites

### Required Software
- **Docker** (v20.10+) - [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose** (v1.29+) - Usually included with Docker Desktop
- **Python 3.9+** - For running test scripts
- **curl** - For testing endpoints (or Postman)

### Verify Installation
```bash
docker --version
docker-compose --version
docker run hello-world
```

---

## 🏗️ Project Structure

```
MLOps_Assignment_01_2025ae05214/
├── Dockerfile                      # Container image definition
├── docker-compose.yml              # Container orchestration
├── .dockerignore                   # Exclude files from image
├── src/
│   ├── app.py                      # FastAPI application
│   ├── test_api.py                 # API testing script
│   └── __init__.py
├── artifacts/
│   ├── models/
│   │   ├── logistic_regression_model.pkl
│   │   ├── random_forest_model.pkl
│   │   └── scaler.pkl
│   └── metrics.json
└── requirements.txt                # Python dependencies
```

---

## 🐳 Method 1: Docker Compose (Recommended for Beginners)

### Step 1: Verify Files Exist

Ensure these files are in your project root:
```bash
ls -la | grep -E "^-.*docker"
# Should show: Dockerfile, docker-compose.yml, .dockerignore
```

### Step 2: Build and Run

```bash
# Build the image and start the container
docker-compose up --build

# Expected output:
# heart-disease-api | Uvicorn running on http://0.0.0.0:8000
# heart-disease-api | Application startup complete [INFO]
```

### Step 3: Test the API

In another terminal:
```bash
# Health check
curl http://localhost:8000/health

# Make a prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "age": 55,
    "sex": 1,
    "cp": 3,
    "trestbps": 130,
    "chol": 250,
    "fbs": 0,
    "restecg": 0,
    "thalach": 142,
    "exang": 1,
    "oldpeak": 1.4,
    "slope": 1,
    "ca": 2,
    "thal": 6
  }'
```

### Step 4: Stop Container

```bash
# In the docker-compose terminal
CTRL + C

# Or in another terminal
docker-compose down
```

---

## 🐳 Method 2: Docker CLI (Advanced)

### Step 1: Build Image

```bash
# Build the Docker image
docker build -t heart-disease-api:latest .

# With progress output
docker build -t heart-disease-api:latest --progress=plain .

# Expected output:
# Step 1/10 : FROM python:3.9-slim
# Step 2/10 : WORKDIR /app
# ...
# Successfully tagged heart-disease-api:latest
```

### Step 2: Run Container

```bash
# Basic run (maps port 8000)
docker run -p 8000:8000 heart-disease-api:latest

# With volume mount (so you can update models)
docker run -p 8000:8000 \
  -v $(pwd)/artifacts:/app/artifacts \
  heart-disease-api:latest

# With environment variables
docker run -p 8000:8000 \
  -e PYTHONUNBUFFERED=1 \
  -v $(pwd)/artifacts:/app/artifacts \
  heart-disease-api:latest

# Run in background
docker run -d -p 8000:8000 \
  -v $(pwd)/artifacts:/app/artifacts \
  --name heart-api \
  heart-disease-api:latest
```

### Step 3: View Logs

```bash
# View logs from running container
docker logs -f heart-api

# View last 100 lines
docker logs --tail 100 heart-api
```

### Step 4: Stop and Remove Container

```bash
# Stop the container
docker stop heart-api

# Remove the container
docker rm heart-api

# Remove the image
docker rmi heart-disease-api:latest
```

---

## 🧪 Testing the API

### Option 1: Using curl (Command Line)

```bash
# 1. Health check
curl http://localhost:8000/health

# 2. Interactive API documentation
# Open in browser: http://localhost:8000/docs

# 3. Single prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "age": 55,
    "sex": 1,
    "cp": 3,
    "trestbps": 130,
    "chol": 250,
    "fbs": 0,
    "restecg": 0,
    "thalach": 142,
    "exang": 1,
    "oldpeak": 1.4,
    "slope": 1,
    "ca": 2,
    "thal": 6
  }'

# 4. With specific model
curl -X POST "http://localhost:8000/predict?model=logistic_regression" \
  -H "Content-Type: application/json" \
  -d '{...}'  # same patient data

# 5. Get metrics
curl http://localhost:8000/metrics?model=random_forest
```

### Option 2: Using Python Test Script

```bash
# Run comprehensive test suite
python src/test_api.py

# Expected output:
# [PASS] Root Endpoint OK: 1.0.0
# [PASS] Health check OK: healthy
# [PASS] Prediction successful: Pred=1, Conf=0.8234
# [PASS] Batch prediction successful: 3 samples processed
# [PASS] Metrics retrieved
# [PASS] Error handling working correctly
# Results: 6/6 tests passed
```

### Option 3: Using Postman

1. **Import Sample Request:**
   ```json
   {
     "name": "Heart Disease Prediction",
     "request": {
       "method": "POST",
       "header": [
         {
           "key": "Content-Type",
           "value": "application/json"
         }
       ],
       "body": {
         "mode": "raw",
         "raw": "{\n  \"age\": 55,\n  \"sex\": 1,\n  \"cp\": 3,\n  \"trestbps\": 130,\n  \"chol\": 250,\n  \"fbs\": 0,\n  \"restecg\": 0,\n  \"thalach\": 142,\n  \"exang\": 1,\n  \"oldpeak\": 1.4,\n  \"slope\": 1,\n  \"ca\": 2,\n  \"thal\": 6\n}"
       },
       "url": {
         "raw": "http://localhost:8000/predict",
         "protocol": "http",
         "host": ["localhost"],
         "port": "8000",
         "path": ["predict"]
       }
     }
   }
   ```

2. **Set Environment:**
   - Base URL: `http://localhost:8000`

3. **Send Request**

---

## 📊 Response Examples

### Successful Prediction Response

```json
{
  "patient_id": "patient_001",
  "prediction": 1,
  "confidence": 0.8234,
  "probabilities": {
    "no_disease": 0.1766,
    "disease": 0.8234
  },
  "model_used": "random_forest",
  "timestamp": "2024-01-15T14:30:22.123456"
}
```

### Health Check Response

```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T14:30:22.123456",
  "models_loaded": true,
  "version": "1.0.0"
}
```

### Metrics Response

```json
{
  "model_name": "random_forest",
  "metrics": {
    "accuracy": 0.9016,
    "precision": 0.9130,
    "recall": 0.8929,
    "f1": 0.9028
  }
}
```

---

## 🔍 Debugging

### Check Container Status

```bash
# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# Inspect container details
docker inspect heart-api

# View resource usage
docker stats heart-api
```

### Common Issues

#### 1. **Port Already in Use**
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use different port
docker run -p 8001:8000 heart-disease-api:latest
```

#### 2. **Models Not Found**
```bash
# Ensure artifacts directory has models
ls artifacts/models/

# Mount artifacts with correct path
docker run -p 8000:8000 \
  -v $(pwd)/artifacts:/app/artifacts \
  heart-disease-api:latest
```

#### 3. **API Not Responding**
```bash
# Check logs
docker logs heart-api

# Test connectivity
curl http://localhost:8000/health

# Check network
docker network ls
```

### Useful Docker Commands

```bash
# View image layers
docker history heart-disease-api:latest

# Access container shell
docker exec -it heart-api /bin/bash

# Copy file from container
docker cp heart-api:/app/logs.txt ./logs.txt

# Rebuild without cache
docker build -t heart-disease-api:latest --no-cache .
```

---

## 📈 Performance Optimization

### Reduce Image Size

```dockerfile
# In Dockerfile - use multi-stage build
FROM python:3.9-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.9-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY src/ ./src/
```

### Resource Limits

```bash
# Set memory and CPU limits
docker run -p 8000:8000 \
  --memory=512m \
  --cpus=1.0 \
  heart-disease-api:latest
```

---

## 🚀 Production Deployment

### Push to Docker Registry

```bash
# Login to Docker Hub
docker login

# Tag image
docker tag heart-disease-api:latest <username>/heart-disease-api:latest

# Push image
docker push <username>/heart-disease-api:latest

# Pull from other machines
docker pull <username>/heart-disease-api:latest
```

### Docker Compose in Production

```bash
# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Scale service (if configured)
docker-compose up -d --scale api=3

# Stop services
docker-compose down -v
```

---

## 📚 Additional Resources

### Docker Commands Cheat Sheet

```bash
# Image Management
docker build -t <image> .          # Build image
docker images                      # List images
docker rmi <image>                 # Remove image

# Container Management
docker run <image>                 # Run container
docker ps                          # List running containers
docker ps -a                       # List all containers
docker stop <container>            # Stop container
docker rm <container>              # Remove container

# Compose
docker-compose up                  # Start services
docker-compose down                # Stop services
docker-compose logs                # View logs
docker-compose ps                  # List services

# Debugging
docker logs <container>            # View container logs
docker exec -it <container> bash   # Access container shell
docker inspect <container>         # Inspect container
```

### Useful Links

- [Docker Documentation](https://docs.docker.com/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [FastAPI Docker Docs](https://fastapi.tiangolo.com/deployment/docker/)
- [Docker Security](https://docs.docker.com/engine/security/)

---

## ✅ Verification Checklist

Before submitting, verify:

- [x] Dockerfile builds without errors
- [x] Container runs and API responds
- [x] `/health` endpoint returns `healthy`
- [x] `/predict` endpoint works with sample input
- [x] `/predict-batch` endpoint works
- [x] API documentation available at `/docs`
- [x] Models are loaded and making predictions
- [x] Error handling works for invalid inputs
- [x] docker-compose.yml creates container successfully
- [x] Test script `src/test_api.py` passes all tests

---

## 🎯 Summary

Your Docker containerized API:

✅ **Containerized** - Runs in isolated environment  
✅ **Reproducible** - Same behavior everywhere  
✅ **Scalable** - Can run multiple instances  
✅ **Production-Ready** - Health checks, logging, error handling  
✅ **Well-Tested** - Comprehensive test suite included  
✅ **Well-Documented** - This guide and FastAPI auto-docs  

Ready for deployment! 🚀
