# Kubernetes Deployment - Heart Disease Prediction API

## Quick Overview

This directory contains all necessary Kubernetes manifests and guides for deploying the Heart Disease Prediction API to:
- ✅ **Local:** Minikube or Docker Desktop Kubernetes
- ✅ **Cloud:** GKE (Google), EKS (AWS), AKS (Microsoft Azure)

---

## Files Overview

### Kubernetes Manifests
| File | Purpose |
|------|---------|
| **01-namespace.yaml** | Creates isolated namespace for the application |
| **02-deployment.yaml** | Defines 3 replicas with health checks, resource limits, security context |
| **03-service.yaml** | LoadBalancer service for external access |
| **04-ingress.yaml** | Ingress controller for URL-based routing |
| **05-configmap.yaml** | Configuration management |

### Documentation
| File | Purpose |
|------|---------|
| **DEPLOYMENT_GUIDE.md** | Comprehensive guide for all platforms (250+ lines) |
| **QUICK_START_LOCAL.sh** | Automated deployment script for local K8s |
| **README.md** | This file |

---

## Quick Start (Local - 5 minutes)

### Prerequisites
- Docker installed and running
- kubectl installed
- Minikube (for Mac/Linux/Windows) OR Docker Desktop with Kubernetes enabled

### Option A: Automated (Easiest)

```bash
# Make script executable
chmod +x QUICK_START_LOCAL.sh

# Run deployment
./QUICK_START_LOCAL.sh

# Follow the prompts!
```

### Option B: Manual

```bash
# Step 1: Build Docker image
docker build -f ../Dockerfile -t heart-disease-api:latest ../..

# Step 2: Load to Minikube (if using Minikube)
minikube image load heart-disease-api:latest

# Step 3: Deploy
kubectl apply -f 01-namespace.yaml
kubectl apply -f 02-deployment.yaml
kubectl apply -f 03-service.yaml
kubectl apply -f 04-ingress.yaml
kubectl apply -f 05-configmap.yaml

# Step 4: Wait for deployment
kubectl rollout status deployment/heart-disease-api -n heart-disease-api

# Step 5: Access API
kubectl port-forward -n heart-disease-api svc/heart-disease-api 8000:80
# Then: curl http://localhost:8000/health
```

---

## Architecture

```
┌─────────────────────────────────────────┐
│         External Traffic                │
└────────────────┬────────────────────────┘
                 │
        ┌────────▼────────┐
        │   Ingress       │ (heart-disease-api.local)
        │  Controller     │
        └────────┬────────┘
                 │
        ┌────────▼────────┐
        │   LoadBalancer  │ (port 80 → 8000)
        │    Service      │
        └────────┬────────┘
                 │
    ┌────────────┼────────────┬────────────┐
    │            │            │            │
┌───▼───┐   ┌───▼───┐   ┌───▼───┐   ┌───▼───┐
│ Pod 1 │   │ Pod 2 │   │ Pod 3 │   │Pod N  │
│ (App) │   │ (App) │   │ (App) │   │ (App) │
└───────┘   └───────┘   └───────┘   └───────┘
│
└─ Heart Disease API Container
   - FastAPI with Uvicorn
   - Health checks
   - Prediction endpoints
```

---

## Deployment on Different Platforms

### Local (Minikube/Docker Desktop)
```bash
# See: QUICK_START_LOCAL.sh or DEPLOYMENT_GUIDE.md Section: "Option 1"
./QUICK_START_LOCAL.sh
```

### Google Cloud (GKE)
```bash
# See: DEPLOYMENT_GUIDE.md Section: "Option 2: GKE"
# Takes ~15 minutes, uses Cloud Load Balancer
# Provides: Public IP for external access
```

### Amazon AWS (EKS)
```bash
# See: DEPLOYMENT_GUIDE.md Section: "Option 3: EKS"
# Takes ~20 minutes, uses AWS Load Balancer
# Provides: DNS endpoint for external access
```

### Microsoft Azure (AKS)
```bash
# See: DEPLOYMENT_GUIDE.md Section: "Option 4: AKS"
# Takes ~10 minutes, uses Azure Load Balancer
# Provides: Public IP for external access
```

---

## Key Features

### ✅ High Availability
- 3 replicas by default
- Pod anti-affinity for distribution
- Rolling updates (0 downtime)

### ✅ Health & Readiness Checks
- Liveness probe: Restart unhealthy pods
- Readiness probe: Only send traffic to ready pods
- Startup probe: Allow time for initialization

### ✅ Resource Management
- CPU requests: 100m, limits: 500m
- Memory requests: 256Mi, limits: 512Mi
- Prevents resource starvation

### ✅ Security
- Non-root user (UID 1000)
- No privilege escalation
- Dropped capabilities
- Read-only root filesystem option

### ✅ Networking
- Internal ClusterIP service
- External LoadBalancer service
- Ingress with TLS support (optional)

### ✅ Observability
- Structured logging
- Prometheus metrics ready
- Event tracking

---

## Testing Endpoints

### Health Check
```bash
curl http://EXTERNAL-IP/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-19T10:23:44.504Z",
  "models_loaded": false,
  "version": "1.0.0"
}
```

### Single Prediction
```bash
curl -X POST http://EXTERNAL-IP/predict \
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

**Response:**
```json
{
  "patient_id": null,
  "prediction": 1,
  "confidence": 0.85,
  "probabilities": {
    "no_disease": 0.15,
    "disease": 0.85
  },
  "model_used": "random_forest",
  "timestamp": "2025-01-19T10:23:44.504Z"
}
```

### Interactive API Docs
```
http://EXTERNAL-IP/docs
```

---

## Common Operations

### Check Deployment Status
```bash
kubectl get all -n heart-disease-api
kubectl describe deployment heart-disease-api -n heart-disease-api
```

### View Logs
```bash
# All pods
kubectl logs -n heart-disease-api -l app=heart-disease-api -f

# Specific pod
kubectl logs -n heart-disease-api POD_NAME -f

# Previous logs (if crashed)
kubectl logs -n heart-disease-api POD_NAME --previous
```

### Scale Deployment
```bash
# Scale to 5 replicas
kubectl scale deployment heart-disease-api --replicas=5 -n heart-disease-api

# View current replicas
kubectl get deployment heart-disease-api -n heart-disease-api
```

### Update Deployment
```bash
# Update image
kubectl set image deployment/heart-disease-api \
  api=heart-disease-api:v2.0 \
  -n heart-disease-api

# Monitor rollout
kubectl rollout status deployment/heart-disease-api -n heart-disease-api
```

### Restart Deployment
```bash
kubectl rollout restart deployment/heart-disease-api -n heart-disease-api
```

### Delete Deployment
```bash
# Delete entire namespace (all resources)
kubectl delete namespace heart-disease-api

# Or delete individually
kubectl delete deployment heart-disease-api -n heart-disease-api
kubectl delete svc heart-disease-api -n heart-disease-api
kubectl delete ingress heart-disease-api -n heart-disease-api
```

---

## Customization

### Change Number of Replicas
Edit `02-deployment.yaml`:
```yaml
spec:
  replicas: 5  # Change from 3 to 5
```

### Change Image
Edit `02-deployment.yaml`:
```yaml
containers:
- name: api
  image: gcr.io/PROJECT_ID/heart-disease-api:v2.0  # Change image
  imagePullPolicy: Always  # Force pull latest
```

### Add Environment Variables
Edit `02-deployment.yaml`:
```yaml
env:
- name: MODEL_TYPE
  value: "random_forest"
- name: BATCH_SIZE
  value: "100"
```

### Configure TLS/SSL
Edit `04-ingress.yaml`:
```yaml
tls:
- hosts:
  - heart-disease-api.example.com
  secretName: heart-disease-api-tls
```

### Set Resource Limits
Edit `02-deployment.yaml`:
```yaml
resources:
  requests:
    cpu: 200m
    memory: 512Mi
  limits:
    cpu: 1000m
    memory: 1Gi
```

---

## Monitoring & Troubleshooting

### Check Pod Status
```bash
# Detailed pod info
kubectl describe pod POD_NAME -n heart-disease-api

# Common issues:
# ImagePullBackOff - Image not found in registry
# CrashLoopBackOff - Application crashes on startup
# Pending - Insufficient resources or missing node selector
```

### Port Forward for Testing
```bash
# Forward local port to service
kubectl port-forward -n heart-disease-api svc/heart-disease-api 8000:80

# Access at http://localhost:8000
```

### Execute Commands in Pod
```bash
# Open shell in pod
kubectl exec -it POD_NAME -n heart-disease-api -- /bin/bash

# Check health endpoint
kubectl exec -it POD_NAME -n heart-disease-api -- curl http://localhost:8000/health
```

### View Resource Usage
```bash
# Pod resource usage
kubectl top pods -n heart-disease-api

# Node resource usage
kubectl top nodes

# (Requires metrics-server: kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml)
```

---

## Production Checklist

- [ ] Image built and pushed to registry
- [ ] Manifests customized for your environment
- [ ] Resource requests/limits configured
- [ ] Ingress controller installed (nginx, GCP, AWS, Azure)
- [ ] TLS certificates provisioned
- [ ] RBAC policies configured
- [ ] Network policies configured
- [ ] Persistent storage configured (if needed)
- [ ] Monitoring configured (Prometheus, Grafana)
- [ ] Logging configured (ELK, Datadog, etc.)
- [ ] Backup strategy in place
- [ ] Disaster recovery plan documented

---

## Support & Documentation

- **Kubernetes Docs:** https://kubernetes.io/docs/
- **GKE:** https://cloud.google.com/kubernetes-engine/docs
- **EKS:** https://docs.aws.amazon.com/eks/
- **AKS:** https://docs.microsoft.com/azure/aks/
- **Minikube:** https://minikube.sigs.k8s.io/

For detailed deployment instructions, see **DEPLOYMENT_GUIDE.md**

---

## Status

✅ **Ready for Deployment**
- All manifests created
- Guides complete
- Quick start script ready
- Tested and verified

**Last Updated:** January 2025  
**Version:** 1.0.0
