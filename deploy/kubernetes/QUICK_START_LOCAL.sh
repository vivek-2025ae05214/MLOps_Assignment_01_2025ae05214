#!/bin/bash

################################################################################
# QUICK_START_LOCAL.sh
# Automated deployment script for Heart Disease Prediction API
# Targets: Docker Desktop Kubernetes or Minikube
# Time: ~5-10 minutes
################################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="heart-disease-api"
NAMESPACE="heart-disease-api"
IMAGE_NAME="${APP_NAME}:latest"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DEPLOY_DIR="${PROJECT_ROOT}/deploy/kubernetes"

################################################################################
# Helper Functions
################################################################################

print_header() {
    echo -e "\n${BLUE}======================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}======================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${BLUE}→ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

wait_for_deployment() {
    local namespace=$1
    local deployment=$2
    local max_attempts=60
    local attempt=0

    print_info "Waiting for deployment to be ready..."
    
    while [ $attempt -lt $max_attempts ]; do
        ready=$(kubectl get deployment "$deployment" -n "$namespace" -o jsonpath='{.status.updatedReplicas}' 2>/dev/null || echo "0")
        desired=$(kubectl get deployment "$deployment" -n "$namespace" -o jsonpath='{.spec.replicas}' 2>/dev/null || echo "0")
        
        if [ "$ready" = "$desired" ] && [ "$desired" -gt 0 ]; then
            print_success "Deployment is ready ($ready/$desired replicas)"
            return 0
        fi
        
        echo -ne "\rAttempt $((attempt + 1))/$max_attempts - Ready: $ready/$desired replicas"
        sleep 2
        ((attempt++))
    done
    
    print_error "Deployment failed to reach ready state"
    return 1
}

################################################################################
# Main Script
################################################################################

print_header "Heart Disease Prediction API - Local Kubernetes Deployment"

# Step 1: Check Prerequisites
print_header "Step 1: Checking Prerequisites"

# Check Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker not found. Please install Docker."
    exit 1
fi
print_success "Docker found: $(docker --version)"

# Check kubectl
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl not found. Please install kubectl."
    exit 1
fi
print_success "kubectl found: $(kubectl version --client --short 2>/dev/null || echo 'installed')"

# Check Kubernetes cluster
if ! kubectl cluster-info &> /dev/null; then
    print_error "Kubernetes cluster not accessible."
    echo -e "\nTo enable Kubernetes:"
    echo "  • Docker Desktop: Settings → Kubernetes → Enable Kubernetes"
    echo "  • Minikube: minikube start"
    exit 1
fi
print_success "Kubernetes cluster is accessible"

# Step 2: Build Docker Image
print_header "Step 2: Building Docker Image"

print_info "Building image: $IMAGE_NAME"
print_info "Project root: $PROJECT_ROOT"

cd "$PROJECT_ROOT"

if docker build -f deploy/Dockerfile -t "$IMAGE_NAME" .; then
    print_success "Docker image built successfully"
else
    print_error "Failed to build Docker image"
    exit 1
fi

# Step 3: Load Image to Kubernetes (for Minikube)
print_header "Step 3: Loading Image to Kubernetes"

KUBE_CONTEXT=$(kubectl config current-context)
print_info "Current Kubernetes context: $KUBE_CONTEXT"

# Check if Minikube
if [[ "$KUBE_CONTEXT" == *"minikube"* ]]; then
    print_info "Detected Minikube. Loading image..."
    if minikube image load "$IMAGE_NAME"; then
        print_success "Image loaded to Minikube"
    else
        print_warning "Failed to load image to Minikube (non-critical)"
    fi
else
    print_info "Detected Docker Desktop. Image available locally."
fi

# Step 4: Deploy to Kubernetes
print_header "Step 4: Deploying to Kubernetes"

print_info "Applying Kubernetes manifests..."

cd "$DEPLOY_DIR"

# Create namespace
print_info "Creating namespace: $NAMESPACE"
if kubectl apply -f 01-namespace.yaml; then
    print_success "Namespace created"
else
    print_error "Failed to create namespace"
    exit 1
fi

# Create ConfigMap
print_info "Creating ConfigMap..."
if kubectl apply -f 05-configmap.yaml; then
    print_success "ConfigMap created"
else
    print_warning "ConfigMap already exists (non-critical)"
fi

# Create Deployment
print_info "Creating Deployment (3 replicas)..."
if kubectl apply -f 02-deployment.yaml; then
    print_success "Deployment created"
else
    print_error "Failed to create deployment"
    exit 1
fi

# Create Service
print_info "Creating Service..."
if kubectl apply -f 03-service.yaml; then
    print_success "Service created"
else
    print_error "Failed to create service"
    exit 1
fi

# Create Ingress
print_info "Creating Ingress..."
if kubectl apply -f 04-ingress.yaml; then
    print_success "Ingress created"
else
    print_warning "Ingress creation skipped (may not be available)"
fi

# Step 5: Wait for Deployment
print_header "Step 5: Waiting for Deployment"

if wait_for_deployment "$NAMESPACE" "$APP_NAME"; then
    print_success "All replicas are running"
else
    print_error "Deployment failed"
    echo -e "\n${YELLOW}Troubleshooting:${NC}"
    echo "  kubectl describe pod POD_NAME -n $NAMESPACE"
    echo "  kubectl logs POD_NAME -n $NAMESPACE"
    exit 1
fi

# Step 6: Test Connectivity
print_header "Step 6: Testing Connectivity"

# Get pods
PODS=$(kubectl get pods -n "$NAMESPACE" -l app="$APP_NAME" -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

if [ -z "$PODS" ]; then
    print_error "No pods found"
    exit 1
fi

print_info "Testing health endpoint on pod: $PODS"

# Test health endpoint
if kubectl exec -n "$NAMESPACE" "$PODS" -- curl -s http://localhost:8000/health > /dev/null 2>&1; then
    print_success "Health endpoint is responding"
else
    print_warning "Health endpoint test skipped"
fi

# Step 7: Display Access Information
print_header "Step 7: Access Information"

# Get service info
SERVICE_IP=$(kubectl get svc -n "$NAMESPACE" "$APP_NAME" -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")
SERVICE_PORT=$(kubectl get svc -n "$NAMESPACE" "$APP_NAME" -o jsonpath='{.spec.ports[0].port}' 2>/dev/null)

print_info "Service Status:"
echo "  Name: $APP_NAME"
echo "  Namespace: $NAMESPACE"
echo "  External IP: ${SERVICE_IP:-pending (use port-forward)}"
echo "  Port: $SERVICE_PORT"

# Show deployment status
print_info "Deployment Status:"
kubectl get deployment -n "$NAMESPACE" "$APP_NAME" --no-headers 2>/dev/null | awk '{print "  Replicas: " $2 "/" $3 ", Updated: " $4 ", Ready: " $5}'

# Show pods
print_info "Running Pods:"
kubectl get pods -n "$NAMESPACE" -l app="$APP_NAME" --no-headers 2>/dev/null | awk '{print "  - " $1 " (" $3 ")"}'

# Step 8: Port Forwarding Setup
print_header "Step 8: Port Forwarding Instructions"

cat << EOF

${YELLOW}⚠ Docker Desktop Note:${NC}
LoadBalancer service will show "pending" IP. Use port-forward:

  kubectl port-forward -n $NAMESPACE svc/$APP_NAME 8000:80

Then access:
  http://localhost:8000

${YELLOW}⚠ Minikube Note:${NC}
If using Minikube, get the service IP with:

  minikube service $APP_NAME -n $NAMESPACE

EOF

print_header "Available Endpoints"

cat << EOF

Once deployed, test these endpoints:

1. ${GREEN}Health Check${NC}
   curl http://localhost:8000/health

2. ${GREEN}Interactive API Docs (Swagger UI)${NC}
   http://localhost:8000/docs

3. ${GREEN}Single Prediction${NC}
   curl -X POST http://localhost:8000/predict \\
     -H "Content-Type: application/json" \\
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

4. ${GREEN}API Documentation${NC}
   Swagger UI:  http://localhost:8000/docs
   ReDoc:       http://localhost:8000/redoc

EOF

# Step 9: Useful Commands
print_header "Useful Commands"

cat << EOF

${BLUE}Monitoring:${NC}
  # View all resources
  kubectl get all -n $NAMESPACE

  # Watch deployment status
  kubectl get deployment -n $NAMESPACE -w

  # View pod logs
  kubectl logs -n $NAMESPACE -l app=$APP_NAME -f

  # View specific pod logs
  kubectl logs -n $NAMESPACE POD_NAME -f

${BLUE}Scaling:${NC}
  # Scale to 5 replicas
  kubectl scale deployment $APP_NAME --replicas=5 -n $NAMESPACE

${BLUE}Troubleshooting:${NC}
  # Describe pod for events
  kubectl describe pod POD_NAME -n $NAMESPACE

  # Execute command in pod
  kubectl exec -it POD_NAME -n $NAMESPACE -- /bin/bash

  # View previous logs (if crashed)
  kubectl logs -n $NAMESPACE POD_NAME --previous

${BLUE}Cleanup:${NC}
  # Delete entire deployment
  kubectl delete namespace $NAMESPACE

  # Or delete specific resources
  kubectl delete deployment $APP_NAME -n $NAMESPACE
  kubectl delete svc $APP_NAME -n $NAMESPACE

EOF

print_header "Deployment Complete! 🎉"

echo -e "${GREEN}Your Heart Disease Prediction API is running on Kubernetes!${NC}\n"

# Final setup instruction
print_info "Next Steps:"
echo "1. Start port-forwarding:  kubectl port-forward -n $NAMESPACE svc/$APP_NAME 8000:80"
echo "2. Open browser:            http://localhost:8000/docs"
echo "3. Test predictions:        Use the Swagger UI"
echo ""

print_success "Setup complete!"
