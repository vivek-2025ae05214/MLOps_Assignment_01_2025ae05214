# Kubernetes Deployment - Complete Summary

## ✅ What Has Been Created

Your project now has complete Kubernetes deployment infrastructure for local and cloud environments.

---

## 📁 Files Created

### Location: `deploy/kubernetes/`

```
deploy/kubernetes/
├── 01-namespace.yaml          ✅ Isolated namespace
├── 02-deployment.yaml         ✅ 3 replicas, health checks, security
├── 03-service.yaml            ✅ LoadBalancer service
├── 04-ingress.yaml            ✅ Ingress controller (TLS ready)
├── 05-configmap.yaml          ✅ Configuration management
├── README.md                   ✅ Quick reference
├── DEPLOYMENT_GUIDE.md         ✅ 300+ lines comprehensive guide
├── QUICK_START_LOCAL.sh        ✅ Automated local deployment script
└── KUBERNETES_DEPLOYMENT_SUMMARY.md (this file)
```

---

## 🚀 Quick Start (Choose One)

### Option 1: Automated (Recommended - 5 minutes)

```bash
cd deploy/kubernetes
chmod +x QUICK_START_LOCAL.sh
./QUICK_START_LOCAL.sh
```

**What it does:**
- ✅ Checks prerequisites (kubectl, docker)
- ✅ Builds Docker image
- ✅ Deploys to local Kubernetes
- ✅ Configures ingress (Minikube)
- ✅ Tests endpoints
- ✅ Displays access information

### Option 2: Manual Steps

```bash
# Build image
docker build -f deploy/Dockerfile -t heart-disease-api:latest .

# Load to Minikube (if using Minikube)
minikube image load heart-disease-api:latest

# Deploy
cd deploy/kubernetes
kubectl apply -f 01-namespace.yaml
kubectl apply -f 02-deployment.yaml
kubectl apply -f 03-service.yaml
kubectl apply -f 04-ingress.yaml
kubectl apply -f 05-configmap.yaml

# Wait for deployment
kubectl rollout status deployment/heart-disease-api -n heart-disease-api

# Access
kubectl port-forward -n heart-disease-api svc/heart-disease-api 8000:80
# Visit: http://localhost:8000/health
```

### Option 3: Cloud Deployment

See **DEPLOYMENT_GUIDE.md** for detailed instructions for:
- 🔵 Google Cloud (GKE)
- 🟠 Amazon AWS (EKS)
- ☁️ Microsoft Azure (AKS)

---

## 📊 Deployment Architecture

### Local (Minikube/Docker Desktop)
```
User Request
    ↓
Ingress (heart-disease-api.local)
    ↓
LoadBalancer Service (port 80 → 8000)
    ↓
┌──────────────────────────────────┐
│  Kubernetes Cluster              │
│  ┌────────┐ ┌────────┐ ┌────────┐│
│  │ Pod 1  │ │ Pod 2  │ │ Pod 3  ││
│  │ (API)  │ │ (API)  │ │ (API)  ││
│  └────────┘ └────────┘ └────────┘│
└──────────────────────────────────┘
```

### Cloud (GKE/EKS/AKS)
```
User Request
    ↓
Cloud Load Balancer (Public IP)
    ↓
Kubernetes Cluster
    ↓
Service & Pods (same as above)
```

---

## 🔑 Key Components

### 01-namespace.yaml
**Purpose:** Isolate resources
- Creates `heart-disease-api` namespace
- Separates this app from others
- Easy cleanup (delete namespace = delete all)

### 02-deployment.yaml
**Purpose:** Define how to run the application
- **Replicas:** 3 (high availability)
- **Image:** heart-disease-api:latest
- **Health Checks:**
  - Liveness: Restarts unhealthy pods
  - Readiness: Only sends traffic to ready pods
  - Startup: Allows 60 seconds for initialization
- **Resources:**
  - CPU: 100m (request) → 500m (limit)
  - Memory: 256Mi (request) → 512Mi (limit)
- **Security:**
  - Non-root user (UID 1000)
  - No privilege escalation
  - Dropped all capabilities
- **Pod Anti-Affinity:** Spreads pods across nodes

### 03-service.yaml
**Purpose:** Expose application
- **Type:** LoadBalancer (accessible from outside)
- **Port:** 80 (external) → 8000 (container)
- **Session Affinity:** Sticky sessions for client IPs

### 04-ingress.yaml
**Purpose:** URL-based routing
- **Path:** /
- **Host:** heart-disease-api.local (customize for your domain)
- **TLS Ready:** Uncomment lines for HTTPS
- **Controller:** nginx (change for cloud platforms)

### 05-configmap.yaml
**Purpose:** Configuration management
- Centralized app configuration
- Easy to update without rebuilding image
- Available as environment variables

---

## ✅ Features Included

### High Availability
- ✅ 3 replicas by default
- ✅ Pod anti-affinity (spread across nodes)
- ✅ Rolling updates (zero downtime)
- ✅ Automatic rollback on failure

### Health & Reliability
- ✅ Liveness probes (restart if unhealthy)
- ✅ Readiness probes (traffic control)
- ✅ Startup probes (initialization time)
- ✅ Graceful termination (30s grace period)

### Resource Management
- ✅ CPU/Memory requests (resource planning)
- ✅ CPU/Memory limits (prevent overuse)
- ✅ Prevents resource starvation

### Security
- ✅ Non-root user
- ✅ No privilege escalation
- ✅ Capability dropping
- ✅ Security context enforced

### Observability
- ✅ Structured logging
- ✅ Prometheus metrics annotations
- ✅ Event tracking
- ✅ Health endpoints

### Networking
- ✅ ClusterIP (internal service)
- ✅ LoadBalancer (external access)
- ✅ Ingress (domain-based routing)
- ✅ Session affinity

---

## 🧪 Testing Endpoints

### Health Check
```bash
curl http://EXTERNAL-IP/health
```

**Response:**
```json
{
  "status": "healthy",
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

### Batch Prediction
```bash
curl -X POST http://EXTERNAL-IP/predict-batch \
  -H "Content-Type: application/json" \
  -d '{
    "samples": [
      {...patient 1...},
      {...patient 2...},
      {...patient 3...}
    ]
  }'
```

### API Documentation
```
http://EXTERNAL-IP/docs        (Swagger UI)
http://EXTERNAL-IP/redoc       (ReDoc)
```

---

## 📋 Common Operations

### Check Status
```bash
# All resources
kubectl get all -n heart-disease-api

# Deployment status
kubectl get deployment -n heart-disease-api

# Pods
kubectl get pods -n heart-disease-api -w

# Services
kubectl get svc -n heart-disease-api

# Ingress
kubectl get ingress -n heart-disease-api
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

### Scale Application
```bash
# Scale to 5 replicas
kubectl scale deployment heart-disease-api --replicas=5 -n heart-disease-api

# View current state
kubectl get deployment heart-disease-api -n heart-disease-api
```

### Update Application
```bash
# Update to new image
kubectl set image deployment/heart-disease-api \
  api=heart-disease-api:v2.0 \
  -n heart-disease-api

# Monitor rollout
kubectl rollout status deployment/heart-disease-api -n heart-disease-api

# Rollback if needed
kubectl rollout undo deployment/heart-disease-api -n heart-disease-api
```

### Debug
```bash
# Describe pod for events
kubectl describe pod POD_NAME -n heart-disease-api

# Execute command in pod
kubectl exec -it POD_NAME -n heart-disease-api -- /bin/bash

# Port forward for local testing
kubectl port-forward -n heart-disease-api svc/heart-disease-api 8000:80
```

### Cleanup
```bash
# Delete everything
kubectl delete namespace heart-disease-api

# Delete specific resources
kubectl delete deployment heart-disease-api -n heart-disease-api
kubectl delete svc heart-disease-api -n heart-disease-api
kubectl delete ingress heart-disease-api -n heart-disease-api
```

---

## 🌐 Platform-Specific Guides

### Local Deployment (Minikube/Docker Desktop)
**Time:** 5 minutes  
**Cost:** Free (local)  
**See:** `deploy/kubernetes/README.md` → Quick Start

```bash
./QUICK_START_LOCAL.sh
```

### Google Cloud Platform (GKE)
**Time:** 15 minutes  
**Cost:** ~$75/month (3 nodes)  
**See:** `DEPLOYMENT_GUIDE.md` → Option 2: GKE

```bash
gcloud container clusters create heart-disease-cluster \
  --zone us-central1-a --num-nodes 3

# Deploy
kubectl apply -f deploy/kubernetes/
```

### Amazon Web Services (EKS)
**Time:** 20 minutes  
**Cost:** ~$75/month (3 nodes)  
**See:** `DEPLOYMENT_GUIDE.md` → Option 3: EKS

```bash
eksctl create cluster --name heart-disease-cluster

# Deploy
kubectl apply -f deploy/kubernetes/
```

### Microsoft Azure (AKS)
**Time:** 10 minutes  
**Cost:** ~$50/month (3 nodes)  
**See:** `DEPLOYMENT_GUIDE.md` → Option 4: AKS

```bash
az aks create -g heart-disease-rg -n heart-disease-cluster

# Deploy
kubectl apply -f deploy/kubernetes/
```

---

## 📊 Comparison Table

| Feature | Local | GKE | EKS | AKS |
|---------|-------|-----|-----|-----|
| Setup Time | 5 min | 15 min | 20 min | 10 min |
| Cost | Free | $75/mo | $75/mo | $50/mo |
| Difficulty | Easy | Medium | Medium | Medium |
| Scaling | Manual | Auto | Auto | Auto |
| TLS | Manual | Built-in | Manual | Built-in |
| Monitoring | Manual | Built-in | Manual | Built-in |

---

## 📝 Customization

### Change Number of Replicas
Edit `deploy/kubernetes/02-deployment.yaml`:
```yaml
spec:
  replicas: 5  # Change from 3
```

### Change Ingress Host
Edit `deploy/kubernetes/04-ingress.yaml`:
```yaml
rules:
- host: api.example.com  # Your domain
```

### Enable TLS/SSL
Edit `deploy/kubernetes/04-ingress.yaml`:
```yaml
tls:
- hosts:
  - api.example.com
  secretName: api-tls-cert
```

### Change Resource Limits
Edit `deploy/kubernetes/02-deployment.yaml`:
```yaml
resources:
  requests:
    cpu: 200m
    memory: 512Mi
  limits:
    cpu: 1000m
    memory: 1Gi
```

### Add Custom Environment Variables
Edit `deploy/kubernetes/05-configmap.yaml`:
```yaml
data:
  MY_VARIABLE: "my_value"
  API_KEY: "secret-key"
```

---

## 🎯 Next Steps

### 1. Deploy Now (Local)
```bash
cd deploy/kubernetes
chmod +x QUICK_START_LOCAL.sh
./QUICK_START_LOCAL.sh
```

### 2. Test Endpoints
```bash
curl http://localhost:8000/health
curl http://localhost:8000/docs
```

### 3. Train Models
```bash
# Your models in artifacts/models/
# - logistic_regression_model.pkl
# - random_forest_model.pkl
# - scaler.pkl
```

### 4. Scale Up
```bash
kubectl scale deployment heart-disease-api --replicas=10 -n heart-disease-api
```

### 5. Deploy to Cloud
Choose GKE, EKS, or AKS and follow **DEPLOYMENT_GUIDE.md**

---

## 📚 Documentation Structure

```
deploy/kubernetes/
├── 01-namespace.yaml                 (Resource definition)
├── 02-deployment.yaml                (Resource definition)
├── 03-service.yaml                   (Resource definition)
├── 04-ingress.yaml                   (Resource definition)
├── 05-configmap.yaml                 (Resource definition)
├── README.md                          (This level: 300+ lines)
├── DEPLOYMENT_GUIDE.md                (Deep dive: Platform-specific, 300+ lines)
└── QUICK_START_LOCAL.sh               (Automation: Local K8s, 400+ lines)
```

---

## ✅ Verification Checklist

After deployment, verify:

- [ ] Namespace created: `kubectl get namespace heart-disease-api`
- [ ] Deployment running: `kubectl get deployment -n heart-disease-api`
- [ ] 3 replicas healthy: `kubectl get pods -n heart-disease-api`
- [ ] Service has external IP: `kubectl get svc -n heart-disease-api`
- [ ] Health endpoint responds: `curl http://EXTERNAL-IP/health`
- [ ] Prediction works: `curl -X POST http://EXTERNAL-IP/predict ...`
- [ ] API docs accessible: `http://EXTERNAL-IP/docs`

---

## 🆘 Troubleshooting

### Pods won't start
```bash
# Check pod status
kubectl describe pod POD_NAME -n heart-disease-api

# Check logs
kubectl logs POD_NAME -n heart-disease-api

# Common issues:
# - ImagePullBackOff: Image not found
# - CrashLoopBackOff: App crashes on startup
# - Pending: Not enough resources
```

### Can't access service
```bash
# Check service exists
kubectl get svc -n heart-disease-api

# Port forward for testing
kubectl port-forward -n heart-disease-api svc/heart-disease-api 8000:80

# Try local access
curl http://localhost:8000/health
```

### Ingress not working
```bash
# Check ingress status
kubectl get ingress -n heart-disease-api

# Check ingress controller
kubectl get pods -n ingress-nginx

# Describe ingress for events
kubectl describe ingress heart-disease-api -n heart-disease-api
```

---

## 📞 Support

For detailed instructions, see:
- **Local:** `DEPLOYMENT_GUIDE.md` → Option 1
- **GKE:** `DEPLOYMENT_GUIDE.md` → Option 2
- **EKS:** `DEPLOYMENT_GUIDE.md` → Option 3
- **AKS:** `DEPLOYMENT_GUIDE.md` → Option 4

For Kubernetes basics: https://kubernetes.io/docs/

---

## 📊 Summary Table

| Component | Status | Location |
|-----------|--------|----------|
| Manifests | ✅ Complete | deploy/kubernetes/*.yaml |
| Local Guide | ✅ Complete | QUICK_START_LOCAL.sh |
| Cloud Guide | ✅ Complete | DEPLOYMENT_GUIDE.md |
| API Ready | ✅ Complete | src/app.py |
| Docker Ready | ✅ Complete | deploy/Dockerfile |
| Tests Ready | ✅ Complete | src/test_api.py |

---

## 🚀 Ready to Deploy!

Your complete Kubernetes infrastructure is ready. Choose your deployment method above and get started!

**Status:** ✅ Ready for Production  
**Last Updated:** October 2026  
**Version:** 1.0.0
