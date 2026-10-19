# Kubernetes Deployment Guide for Heart Disease Prediction API

## Overview

This guide covers deploying the Heart Disease Prediction API to Kubernetes on different platforms:
- **Local:** Minikube, Docker Desktop Kubernetes
- **Cloud:** GKE (Google), EKS (AWS), AKS (Microsoft Azure)

---

## Prerequisites

### Required Tools
```bash
# Install kubectl
# macOS
brew install kubectl

# Linux
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# Windows
choco install kubernetes-cli

# Verify installation
kubectl version --client
```

### Docker Image
```bash
# Build and push Docker image to registry
docker build -f deploy/Dockerfile -t heart-disease-api:latest .

# For public cloud, push to registry
# GCP
docker tag heart-disease-api:latest gcr.io/PROJECT_ID/heart-disease-api:latest
docker push gcr.io/PROJECT_ID/heart-disease-api:latest

# AWS
docker tag heart-disease-api:latest ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/heart-disease-api:latest
docker push ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/heart-disease-api:latest

# Azure
docker tag heart-disease-api:latest myregistry.azurecr.io/heart-disease-api:latest
docker push myregistry.azurecr.io/heart-disease-api:latest
```

---

## Option 1: Local Deployment (Minikube / Docker Desktop)

### Step 1: Start Local Kubernetes

#### Using Minikube
```bash
# Install minikube
brew install minikube  # macOS
choco install minikube # Windows

# Start cluster
minikube start --cpus=4 --memory=4096 --disk-size=20g

# Enable metrics server (for monitoring)
minikube addons enable metrics-server

# Enable ingress controller
minikube addons enable ingress
```

#### Using Docker Desktop
```bash
# Enable Kubernetes in Docker Desktop Settings
# Settings → Kubernetes → Enable Kubernetes

# Verify
kubectl get nodes
```

### Step 2: Load Docker Image (Minikube only)

```bash
# For Minikube, load local image
minikube image load heart-disease-api:latest

# Verify image is available
minikube image ls | grep heart-disease-api
```

### Step 3: Deploy to Kubernetes

```bash
# Create namespace
kubectl apply -f deploy/kubernetes/01-namespace.yaml

# Deploy application
kubectl apply -f deploy/kubernetes/02-deployment.yaml

# Create service
kubectl apply -f deploy/kubernetes/03-service.yaml

# Create ingress
kubectl apply -f deploy/kubernetes/04-ingress.yaml

# Create configmap
kubectl apply -f deploy/kubernetes/05-configmap.yaml

# Verify deployment
kubectl get all -n heart-disease-api
```

### Step 4: Access the API Locally

#### Via Service (Port Forward)
```bash
# Forward local port to service
kubectl port-forward -n heart-disease-api svc/heart-disease-api 8000:80

# Test API
curl http://localhost:8000/health

# View docs
open http://localhost:8000/docs
```

#### Via Ingress
```bash
# For Minikube, get ingress IP
minikube ip
# Add to /etc/hosts
echo "$(minikube ip) heart-disease-api.local" | sudo tee -a /etc/hosts

# Access
curl http://heart-disease-api.local
open http://heart-disease-api.local/docs

# Or use tunnel (one-command)
minikube tunnel
# Then access at http://heart-disease-api.local
```

### Step 5: Monitor Deployment

```bash
# Watch deployment status
kubectl get deployment -n heart-disease-api -w

# View pods
kubectl get pods -n heart-disease-api

# View logs
kubectl logs -n heart-disease-api -l app=heart-disease-api -f

# View events
kubectl describe deployment heart-disease-api -n heart-disease-api

# Check service
kubectl get svc -n heart-disease-api

# Check ingress
kubectl get ingress -n heart-disease-api
```

---

## Option 2: GKE (Google Cloud)

### Step 1: Setup GCP Project

```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init

# Set project
gcloud config set project PROJECT_ID

# Enable APIs
gcloud services enable container.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### Step 2: Create GKE Cluster

```bash
# Create cluster
gcloud container clusters create heart-disease-cluster \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type n1-standard-1 \
  --enable-stackdriver-kubernetes

# Get credentials
gcloud container clusters get-credentials heart-disease-cluster --zone us-central1-a

# Verify connection
kubectl cluster-info
```

### Step 3: Push Docker Image to GCR

```bash
# Configure docker authentication
gcloud auth configure-docker

# Tag image
docker tag heart-disease-api:latest gcr.io/PROJECT_ID/heart-disease-api:latest

# Push to GCR
docker push gcr.io/PROJECT_ID/heart-disease-api:latest

# Verify
gcloud container images list
```

### Step 4: Update Deployment Manifest

```bash
# Edit 02-deployment.yaml
# Change:
# image: heart-disease-api:latest
# To:
# image: gcr.io/PROJECT_ID/heart-disease-api:latest
# Also change imagePullPolicy: IfNotPresent to Always
```

### Step 5: Deploy to GKE

```bash
# Create namespace
kubectl apply -f deploy/kubernetes/01-namespace.yaml

# Deploy
kubectl apply -f deploy/kubernetes/02-deployment.yaml
kubectl apply -f deploy/kubernetes/03-service.yaml
kubectl apply -f deploy/kubernetes/04-ingress.yaml
kubectl apply -f deploy/kubernetes/05-configmap.yaml

# Check deployment
kubectl get all -n heart-disease-api
```

### Step 6: Get External IP

```bash
# Watch for external IP assignment
kubectl get svc -n heart-disease-api -w

# Once EXTERNAL-IP is assigned, access API
curl http://EXTERNAL_IP/health

# View docs
open http://EXTERNAL_IP/docs
```

### Step 7: (Optional) Setup Cloud Load Balancer

```bash
# The service type LoadBalancer automatically creates Cloud LB
# View load balancer in GCP Console:
# Compute → Load balancing → Your Load Balancer

# Get load balancer IP
gcloud compute forwarding-rules list
```

### Step 8: Cleanup

```bash
# Delete deployment
kubectl delete namespace heart-disease-api

# Delete cluster
gcloud container clusters delete heart-disease-cluster --zone us-central1-a

# Delete images
gcloud container images delete gcr.io/PROJECT_ID/heart-disease-api:latest
```

---

## Option 3: EKS (Amazon AWS)

### Step 1: Setup AWS Account

```bash
# Install AWS CLI
pip install awscli

# Configure credentials
aws configure

# Install eksctl
brew install eksctl

# Install kubectl (if not already)
brew install kubectl
```

### Step 2: Create EKS Cluster

```bash
# Create cluster (takes ~15 minutes)
eksctl create cluster \
  --name heart-disease-cluster \
  --version 1.27 \
  --region us-east-1 \
  --nodegroup-name standard-workers \
  --node-type t3.medium \
  --nodes 3 \
  --nodes-min 1 \
  --nodes-max 4

# Verify
kubectl get nodes
```

### Step 3: Push Docker Image to ECR

```bash
# Create ECR repository
aws ecr create-repository --repository-name heart-disease-api --region us-east-1

# Get login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Tag image
docker tag heart-disease-api:latest ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/heart-disease-api:latest

# Push to ECR
docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/heart-disease-api:latest
```

### Step 4: Update Deployment & Deploy

```bash
# Edit 02-deployment.yaml - update image URI
# Update 03-service.yaml - change to LoadBalancer type

# Deploy
kubectl apply -f deploy/kubernetes/01-namespace.yaml
kubectl apply -f deploy/kubernetes/02-deployment.yaml
kubectl apply -f deploy/kubernetes/03-service.yaml
kubectl apply -f deploy/kubernetes/04-ingress.yaml
kubectl apply -f deploy/kubernetes/05-configmap.yaml

# Get LoadBalancer DNS
kubectl get svc -n heart-disease-api

# Access via DNS
curl http://EXTERNAL-IP.elb.amazonaws.com/health
```

### Step 5: Cleanup

```bash
# Delete deployment
kubectl delete namespace heart-disease-api

# Delete cluster
eksctl delete cluster --name heart-disease-cluster --region us-east-1

# Delete ECR repository
aws ecr delete-repository --repository-name heart-disease-api --force --region us-east-1
```

---

## Option 4: AKS (Microsoft Azure)

### Step 1: Setup Azure Account

```bash
# Install Azure CLI
brew install azure-cli

# Login
az login

# Set subscription
az account set --subscription SUBSCRIPTION_ID

# Install kubectl
az aks install-cli
```

### Step 2: Create AKS Cluster

```bash
# Create resource group
az group create --name heart-disease-rg --location eastus

# Create AKS cluster
az aks create \
  --resource-group heart-disease-rg \
  --name heart-disease-cluster \
  --node-count 3 \
  --vm-set-type VirtualMachineScaleSets \
  --load-balancer-sku standard \
  --enable-managed-identity \
  --network-plugin azure

# Get credentials
az aks get-credentials --resource-group heart-disease-rg --name heart-disease-cluster

# Verify
kubectl get nodes
```

### Step 3: Push Docker Image to ACR

```bash
# Create container registry
az acr create --resource-group heart-disease-rg --name heartdisease --sku Basic

# Login to ACR
az acr login --name heartdisease

# Tag image
docker tag heart-disease-api:latest heartdisease.azurecr.io/heart-disease-api:latest

# Push to ACR
docker push heartdisease.azurecr.io/heart-disease-api:latest

# Configure AKS to pull from ACR
az aks update -n heart-disease-cluster -g heart-disease-rg --attach-acr heartdisease
```

### Step 4: Deploy to AKS

```bash
# Update image in 02-deployment.yaml
# image: heartdisease.azurecr.io/heart-disease-api:latest

# Deploy
kubectl apply -f deploy/kubernetes/01-namespace.yaml
kubectl apply -f deploy/kubernetes/02-deployment.yaml
kubectl apply -f deploy/kubernetes/03-service.yaml
kubectl apply -f deploy/kubernetes/04-ingress.yaml
kubectl apply -f deploy/kubernetes/05-configmap.yaml

# Get public IP
kubectl get svc -n heart-disease-api

# Access API
curl http://EXTERNAL-IP/health
```

### Step 5: Cleanup

```bash
# Delete deployment
kubectl delete namespace heart-disease-api

# Delete resource group (deletes cluster + ACR)
az group delete --name heart-disease-rg
```

---

## Testing Deployed API

### Test Health Endpoint
```bash
# Test health
curl -i http://EXTERNAL-IP/health

# Expected response
# HTTP/1.1 200 OK
# {
#   "status": "healthy",
#   "timestamp": "2025-01-19T10:23:44.504Z",
#   "models_loaded": false,
#   "version": "1.0.0"
# }
```

### Test Prediction Endpoint
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

# Expected response
# {
#   "patient_id": null,
#   "prediction": 1,
#   "confidence": 0.85,
#   "probabilities": {
#     "no_disease": 0.15,
#     "disease": 0.85
#   },
#   "model_used": "random_forest",
#   "timestamp": "2025-01-19T10:23:44.504Z"
# }
```

### View API Documentation
```bash
# Open in browser
http://EXTERNAL-IP/docs

# View interactive Swagger UI
http://EXTERNAL-IP/redoc
```

---

## Monitoring & Logging

### View Logs
```bash
# All pods
kubectl logs -n heart-disease-api -l app=heart-disease-api -f

# Specific pod
kubectl logs -n heart-disease-api POD_NAME -f

# Previous logs (if pod crashed)
kubectl logs -n heart-disease-api POD_NAME --previous
```

### Monitor Resource Usage
```bash
# View resource metrics
kubectl top nodes
kubectl top pods -n heart-disease-api

# (Requires metrics-server installed)
```

### Describe Resources
```bash
# Deployment details
kubectl describe deployment heart-disease-api -n heart-disease-api

# Pod details
kubectl describe pod POD_NAME -n heart-disease-api

# Service details
kubectl describe svc heart-disease-api -n heart-disease-api
```

---

## Scaling

### Manual Scaling
```bash
# Scale to 5 replicas
kubectl scale deployment heart-disease-api --replicas=5 -n heart-disease-api

# Verify
kubectl get pods -n heart-disease-api
```

### Horizontal Pod Autoscaling (HPA)
```bash
# Create HPA (requires metrics-server)
kubectl autoscale deployment heart-disease-api \
  --cpu-percent=80 \
  --min=2 \
  --max=10 \
  -n heart-disease-api

# View HPA status
kubectl get hpa -n heart-disease-api
```

---

## Troubleshooting

### Pods not starting
```bash
# Check pod status
kubectl get pods -n heart-disease-api

# View events
kubectl describe pod POD_NAME -n heart-disease-api

# View logs
kubectl logs POD_NAME -n heart-disease-api
```

### Image pull errors
```bash
# Check image URI in deployment
kubectl get deployment heart-disease-api -n heart-disease-api -o yaml | grep image:

# Verify image exists in registry
# For GCR: gcloud container images list
# For ECR: aws ecr describe-repositories
# For ACR: az acr repository list --name REGISTRY_NAME
```

### Service not accessible
```bash
# Check service
kubectl get svc -n heart-disease-api

# Port forward to test
kubectl port-forward -n heart-disease-api svc/heart-disease-api 8000:80

# Test locally
curl http://localhost:8000/health
```

### Ingress not working
```bash
# Check ingress class is available
kubectl get ingressclass

# Check ingress controller is running
kubectl get pods -n ingress-nginx

# Describe ingress for events
kubectl describe ingress heart-disease-api -n heart-disease-api
```

---

## Production Checklist

- [ ] Docker image built and pushed to registry
- [ ] Kubernetes manifests reviewed and customized
- [ ] Image pull secrets configured (if private registry)
- [ ] Resource requests/limits set appropriately
- [ ] Health checks configured
- [ ] Logging configured (e.g., ELK stack, Datadog)
- [ ] Monitoring configured (e.g., Prometheus, Grafana)
- [ ] Load balancer or Ingress controller installed
- [ ] TLS/SSL certificates configured
- [ ] RBAC policies configured
- [ ] Network policies configured
- [ ] Disaster recovery plan documented
- [ ] Scaling policies configured (HPA)

---

## Quick Reference Commands

```bash
# Deployment
kubectl apply -f deploy/kubernetes/
kubectl rollout status deployment/heart-disease-api -n heart-disease-api
kubectl rollout undo deployment/heart-disease-api -n heart-disease-api

# Debugging
kubectl exec -it POD_NAME -n heart-disease-api -- /bin/bash
kubectl port-forward svc/heart-disease-api 8000:80 -n heart-disease-api

# Cleanup
kubectl delete namespace heart-disease-api
```

---

## References

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [GKE Documentation](https://cloud.google.com/kubernetes-engine/docs)
- [EKS Documentation](https://docs.aws.amazon.com/eks/)
- [AKS Documentation](https://docs.microsoft.com/en-us/azure/aks/)
- [Minikube Documentation](https://minikube.sigs.k8s.io/)

---

**Status:** Ready for Deployment  
**Last Updated:** January 2025  
**Version:** 1.0.0
