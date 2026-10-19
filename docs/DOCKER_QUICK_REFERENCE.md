# Docker Quick Reference - Cheat Sheet

## 🚀 Quick Start (30 seconds)

```bash
# Build and run
docker-compose up --build

# Test (in another terminal)
curl http://localhost:8000/health

# Stop
CTRL + C
```

---

## 📦 Essential Docker Commands

### Build

```bash
docker build -t heart-disease-api:latest .          # Build image
docker build -t heart-disease-api:latest --no-cache .  # Force rebuild
docker images | grep heart-disease-api              # List images
```

### Run

```bash
docker run -p 8000:8000 heart-disease-api:latest    # Basic run
docker run -d -p 8000:8000 heart-disease-api:latest # Background
docker run -p 8000:8000 -v $(pwd)/artifacts:/app/artifacts heart-disease-api:latest  # With volume
```

### Container Management

```bash
docker ps                           # List running containers
docker ps -a                        # List all containers
docker logs <container-id>          # View logs
docker exec -it <id> /bin/bash      # Access shell
docker stop <container-id>          # Stop container
docker rm <container-id>            # Remove container
docker rmi heart-disease-api:latest # Remove image
```

---

## 🐳 Docker Compose Commands

```bash
docker-compose up                   # Start services
docker-compose up -d                # Start in background
docker-compose up --build           # Rebuild images first
docker-compose logs -f              # View logs (follow)
docker-compose down                 # Stop services
docker-compose down -v              # Stop and remove volumes
docker-compose ps                   # List services
```

---

## 🧪 API Testing

### Health Check

```bash
curl http://localhost:8000/health
```

### Single Prediction

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "age": 55, "sex": 1, "cp": 3, "trestbps": 130,
    "chol": 250, "fbs": 0, "restecg": 0, "thalach": 142,
    "exang": 1, "oldpeak": 1.4, "slope": 1, "ca": 2, "thal": 6
  }'
```

### Batch Prediction

```bash
curl -X POST http://localhost:8000/predict-batch \
  -H "Content-Type: application/json" \
  -d '{"samples": [{...}, {...}]}'
```

### Model Selection

```bash
curl -X POST "http://localhost:8000/predict?model=logistic_regression" ...
curl -X POST "http://localhost:8000/predict?model=random_forest" ...
```

### Interactive Docs

```
Browser: http://localhost:8000/docs
```

---

## 🧪 Test Suite

```bash
# Run all tests
python src/test_api.py

# Expected output:
# ✓ Root Endpoint OK
# ✓ Health Check OK
# ✓ Single Prediction (LR) successful
# ✓ Single Prediction (RF) successful
# ✓ Batch Prediction successful
# ✓ Metrics retrieved
# ✓ Error handling working
# Results: 7/7 tests passed
```

---

## 📊 API Endpoints

| Method | Endpoint         | Purpose             |
| ------ | ---------------- | ------------------- |
| GET    | `/`              | API info            |
| GET    | `/health`        | Health check        |
| POST   | `/predict`       | Single prediction   |
| POST   | `/predict-batch` | Batch prediction    |
| GET    | `/metrics`       | Model metrics       |
| GET    | `/docs`          | Swagger UI docs     |
| GET    | `/redoc`         | ReDoc documentation |

---

## 🔧 Debugging

### View logs

```bash
docker logs <container-id>
docker logs -f <container-id>       # Follow logs
docker logs --tail 100 <container>  # Last 100 lines
```

### Check status

```bash
docker ps                           # Running containers
docker ps -a                        # All containers
docker inspect <container-id>       # Detailed info
docker stats <container-id>         # Resource usage
```

### Access container

```bash
docker exec -it <container-id> /bin/bash
docker cp <container-id>:/path/file ./local-file
```

### Network issues

```bash
# Find process on port 8000
lsof -i :8000
kill -9 <PID>

# Use different port
docker run -p 8001:8000 heart-disease-api:latest
```

---

## 📝 Common Issues & Solutions

### Issue: Port Already in Use

```bash
# Kill process on port 8000
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

### Issue: Models Not Found

```bash
# Verify models exist
ls artifacts/models/

# Mount artifacts correctly
docker run -v $(pwd)/artifacts:/app/artifacts ...
```

### Issue: Container Won't Start

```bash
# Check logs
docker logs <container-id>

# Rebuild without cache
docker build --no-cache -t heart-disease-api:latest .
```

### Issue: API Not Responding

```bash
# Check if container is running
docker ps

# Check health
curl http://localhost:8000/health

# View logs
docker logs <container-id>

# Test connectivity
docker exec <container-id> curl localhost:8000/health
```

---

## 🚀 Production Deployment

### Docker Hub

```bash
docker login
docker tag heart-disease-api:latest <username>/heart-disease-api:latest
docker push <username>/heart-disease-api:latest
docker pull <username>/heart-disease-api:latest
```

### Environment Variables

```bash
docker run -p 8000:8000 \
  -e PYTHONUNBUFFERED=1 \
  -e LOG_LEVEL=INFO \
  heart-disease-api:latest
```

### Resource Limits

```bash
docker run -p 8000:8000 \
  --memory=512m \
  --cpus=1.0 \
  heart-disease-api:latest
```

---

## 📊 Image Info

### Build info

```bash
docker history heart-disease-api:latest
docker inspect heart-disease-api:latest
docker images heart-disease-api
```

### Size check

```bash
docker images | grep heart-disease-api
# Shows: REPOSITORY, TAG, IMAGE ID, CREATED, SIZE
```

---

## 🔐 Security Basics

### Non-root user

```dockerfile
RUN useradd -m -u 1000 appuser
USER appuser
```

### Read-only volumes

```bash
docker run -v $(pwd)/artifacts:/app/artifacts:ro ...
```

### Health checks

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

---

## 📁 File Structure

```
.
├── Dockerfile              # Container definition
├── docker-compose.yml      # Compose config
├── .dockerignore          # Exclude files
├── src/
│   ├── app.py             # FastAPI app
│   └── test_api.py        # Tests
├── artifacts/
│   ├── models/
│   │   ├── *.pkl          # Trained models
│   │   └── scaler.pkl     # Feature scaler
│   └── metrics.json       # Metrics
└── requirements.txt       # Dependencies
```

---

## 📞 Help & Documentation

| Resource       | Location                         |
| -------------- | -------------------------------- |
| Complete Guide | DOCKER_GUIDE.md                  |
| Notebook Cells | DOCKER_NOTEBOOK_CELLS.md         |
| Implementation | DOCKER_IMPLEMENTATION_SUMMARY.md |
| FastAPI Code   | src/app.py                       |
| Test Suite     | src/test_api.py                  |
| Docker Image   | Dockerfile                       |
| Compose Config | docker-compose.yml               |

---

## ⚡ Performance Tips

```bash
# Build with BuildKit (faster)
DOCKER_BUILDKIT=1 docker build -t heart-disease-api:latest .

# Use .dockerignore to reduce context size
# Check file size
docker images | grep heart-disease-api

# Optimize layers
# - Install, clean cache in one RUN
# - Use multi-stage builds
# - Order by change frequency
```

---

## 🎯 Verification Checklist

- [ ] Docker installed (`docker --version`)
- [ ] Image built (`docker images | grep heart-disease-api`)
- [ ] Container runs (`docker ps` shows container)
- [ ] Health check passes (`curl http://localhost:8000/health`)
- [ ] Prediction works (`curl -X POST http://localhost:8000/predict ...`)
- [ ] Tests pass (`python src/test_api.py`)
- [ ] API docs available (`http://localhost:8000/docs`)

---

## 🚀 One-Liner Commands

```bash
# Build and test
docker build -t heart-disease-api:latest . && docker run -p 8000:8000 heart-disease-api:latest

# Run and test
docker-compose up --build && sleep 5 && python src/test_api.py

# Quick health check
curl http://localhost:8000/health | jq '.'

# View last logs
docker logs $(docker ps -q | head -1) --tail 50

# Clean everything
docker system prune -a
```

---

## 📝 Sample Request/Response

### Request

```json
{
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
}
```

### Response

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

---

**Last Updated:** January 2025  
**Status:** Complete ✅  
**Ready for:** Development & Production
