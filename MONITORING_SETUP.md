# Monitoring Setup Guide - Heart Disease Prediction API

## 🎯 Overview

Your API now includes comprehensive monitoring capabilities:
- ✅ **Request Logging** - All API requests logged to `api_requests.log`
- ✅ **Prometheus Metrics** - Full metrics for scraping
- ✅ **Built-in Dashboard** - Simple monitoring without external tools
- ✅ **Grafana Ready** - Can integrate with Grafana for visualization

---

## 📊 Monitoring Architecture

```
┌─────────────────────────────────────────────────────────┐
│         Heart Disease Prediction API                    │
│  ┌─────────────────────────────────────────────────┐   │
│  │ REQUEST LOGGING MIDDLEWARE                      │   │
│  │ - Logs all requests/responses                   │   │
│  │ - Tracks request duration                       │   │
│  │ - Records error details                         │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │ PROMETHEUS METRICS                              │   │
│  │ - api_requests_total                            │   │
│  │ - api_request_duration_seconds                  │   │
│  │ - predictions_total                             │   │
│  │ - prediction_duration_seconds                   │   │
│  │ - api_errors_total                              │   │
│  │ - models_loaded (Gauge)                         │   │
│  │ - api_active_requests (Gauge)                   │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
           │                    │                    │
           ▼                    ▼                    ▼
    ┌──────────────┐    ┌──────────────┐   ┌──────────────┐
    │ Built-in     │    │ Prometheus   │   │ Log Files    │
    │ Dashboard    │    │ Scraper      │   │              │
    │ /dashboard   │    │ :9090        │   │ api_requests │
    │ /logs        │    │              │   │ .log         │
    └──────────────┘    └──────────────┘   └──────────────┘
           │                    │
           ▼                    ▼
    ┌──────────────────────────────────┐
    │         Grafana Dashboards       │
    │ (Optional visualization layer)   │
    └──────────────────────────────────┘
```

---

## 🚀 Quick Start - 3 Options

### Option 1: Simple Monitoring (No External Tools) ⭐ RECOMMENDED

Access built-in monitoring endpoints:

```bash
# 1. Port forward (if not already running)
kubectl port-forward -n heart-disease-api svc/heart-disease-api 8000:80

# 2. Dashboard Summary
curl http://localhost:8000/dashboard/summary

# 3. API Statistics
curl http://localhost:8000/stats

# 4. Recent Logs (last 50 lines)
curl http://localhost:8000/logs

# 5. Detailed Health
curl http://localhost:8000/health/detailed

# 6. Prometheus Metrics (raw)
curl http://localhost:8000/prometheus
```

**Expected Output - Dashboard Summary:**
```json
{
  "timestamp": "2025-01-19T10:23:44.504Z",
  "status": "healthy",
  "models_loaded": true,
  "key_metrics": {
    "total_requests": 42,
    "total_predictions": 15,
    "total_errors": 0,
    "active_requests": 0
  },
  "request_performance": {
    "endpoints": {}
  }
}
```

---

### Option 2: Prometheus + Grafana (Full Stack)

#### Step 1: Deploy Prometheus

```bash
# Apply Prometheus configuration
kubectl apply -f deploy/kubernetes/06-prometheus-configmap.yaml

# Deploy Prometheus (if cluster supports StatefulSets)
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
  namespace: heart-disease-api
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      containers:
      - name: prometheus
        image: prom/prometheus:latest
        ports:
        - containerPort: 9090
        volumeMounts:
        - name: config
          mountPath: /etc/prometheus
        args:
          - --config.file=/etc/prometheus/prometheus.yml
          - --storage.tsdb.path=/prometheus
        resources:
          requests:
            cpu: 100m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
      volumes:
      - name: config
        configMap:
          name: prometheus-config
---
apiVersion: v1
kind: Service
metadata:
  name: prometheus
  namespace: heart-disease-api
spec:
  type: LoadBalancer
  selector:
    app: prometheus
  ports:
  - port: 9090
    targetPort: 9090
EOF
```

#### Step 2: Access Prometheus

```bash
# Port forward to Prometheus
kubectl port-forward -n heart-disease-api svc/prometheus 9090:9090

# Open browser
open http://localhost:9090
```

**In Prometheus UI:**
1. Go to **Graph** tab
2. Search metrics:
   - `api_requests_total` - Total API requests
   - `predictions_total` - Total predictions
   - `api_request_duration_seconds` - Request latency
   - `api_errors_total` - Error count

#### Step 3: Deploy Grafana (Optional)

```bash
# Deploy Grafana
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana
  namespace: heart-disease-api
spec:
  replicas: 1
  selector:
    matchLabels:
      app: grafana
  template:
    metadata:
      labels:
        app: grafana
    spec:
      containers:
      - name: grafana
        image: grafana/grafana:latest
        ports:
        - containerPort: 3000
        env:
        - name: GF_SECURITY_ADMIN_PASSWORD
          value: "admin"
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
---
apiVersion: v1
kind: Service
metadata:
  name: grafana
  namespace: heart-disease-api
spec:
  type: LoadBalancer
  selector:
    app: grafana
  ports:
  - port: 3000
    targetPort: 3000
EOF
```

#### Step 4: Configure Grafana

```bash
# Port forward to Grafana
kubectl port-forward -n heart-disease-api svc/grafana 3000:3000

# Open browser
open http://localhost:3000
```

**Login:**
- Username: `admin`
- Password: `admin`

**Add Prometheus Data Source:**
1. Click **Configuration** → **Data Sources**
2. Click **Add data source**
3. Select **Prometheus**
4. URL: `http://prometheus:9090`
5. Click **Save & test**

**Create Dashboard:**
1. Click **+** → **Dashboard**
2. Click **Add panel**
3. Select Prometheus as data source
4. Add queries:
   - `rate(api_requests_total[1m])` - Requests per minute
   - `histogram_quantile(0.95, api_request_duration_seconds)` - 95th percentile latency
   - `predictions_total` - Total predictions

---

### Option 3: Docker Compose (Local Development)

Create `docker-compose.monitoring.yml`:

```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./deploy/kubernetes/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - --config.file=/etc/prometheus/prometheus.yml
      - --storage.tsdb.path=/prometheus

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
    depends_on:
      - prometheus

volumes:
  prometheus_data:
  grafana_data:
```

Run:
```bash
docker-compose -f docker-compose.monitoring.yml up -d
```

---

## 📝 Integrated Logging Features

### Request Logging Middleware

Every API request is logged with:
- ✅ Request timestamp
- ✅ HTTP method (GET, POST, etc.)
- ✅ Endpoint path
- ✅ Client IP address
- ✅ Request ID (for tracking)
- ✅ Response status code
- ✅ Request duration (latency)
- ✅ Error details (if any)

**Log File Location:** `api_requests.log`

**Log Entry Example:**
```
2025-01-19 10:23:44 - src.app - INFO - [REQUEST] POST /predict | Client: 127.0.0.1 | Request ID: /predict
2025-01-19 10:23:44 - src.app - INFO - [PREDICTION] Patient: patient_123, Model: random_forest, Age: 55
2025-01-19 10:23:44 - src.app - INFO - [PREDICTION_RESULT] Prediction: 1 | Confidence: 0.85 | Prediction Time: 0.0124s | Total Time: 0.0156s | Patient: patient_123
2025-01-19 10:23:44 - src.app - INFO - [RESPONSE] POST /predict | Status: 200 | Duration: 0.0156s | Request ID: /predict
```

### View Logs

**Option 1: Via API Endpoint**
```bash
# Last 50 lines
curl http://localhost:8000/logs

# Filter by level (INFO, ERROR, WARNING, DEBUG)
curl http://localhost:8000/logs?level=ERROR

# Get 100 lines
curl http://localhost:8000/logs?lines=100
```

**Option 2: Direct File Access**
```bash
# Follow logs in real-time
tail -f api_requests.log

# Last 100 lines
tail -100 api_requests.log

# Search for errors
grep ERROR api_requests.log

# Search for predictions
grep PREDICTION api_requests.log
```

**Option 3: In Kubernetes**
```bash
# Pod logs
kubectl logs -n heart-disease-api <POD_NAME> -f

# All pod logs
kubectl logs -n heart-disease-api -l app=heart-disease-api -f
```

---

## 📊 Available Metrics

### Prometheus Metrics (scraped from `/prometheus`)

#### Counter Metrics (cumulative)
| Metric | Labels | Description |
|--------|--------|-------------|
| `api_requests_total` | method, endpoint, status | Total API requests |
| `predictions_total` | model, result | Total predictions |
| `api_errors_total` | error_type, endpoint | Total errors |

#### Histogram Metrics (distribution)
| Metric | Labels | Description |
|--------|--------|-------------|
| `api_request_duration_seconds` | method, endpoint | Request latency |
| `prediction_duration_seconds` | model | Prediction latency |

#### Gauge Metrics (point-in-time)
| Metric | Description |
|--------|-------------|
| `models_loaded` | Number of models loaded (0 or 2) |
| `api_active_requests` | Current active requests |

---

## 🎯 Example Prometheus Queries

```promql
# Requests per second (last 5 minutes)
rate(api_requests_total[5m])

# 95th percentile request latency
histogram_quantile(0.95, api_request_duration_seconds)

# Prediction success rate
predictions_total{result="no_disease"} / predictions_total

# Error rate
rate(api_errors_total[5m])

# Average prediction time
rate(prediction_duration_seconds_sum[5m]) / rate(prediction_duration_seconds_count[5m])

# Models health (should be 2)
models_loaded

# Current load
api_active_requests
```

---

## 🚨 Alerts & Health Checks

### Health Endpoints

```bash
# Basic health
curl http://localhost:8000/health

# Detailed health
curl http://localhost:8000/health/detailed

# Model status
curl http://localhost:8000/health/models
```

### Sample Alert Rules

Create `alerts.yml`:

```yaml
groups:
- name: heart_disease_api
  interval: 30s
  rules:
  - alert: HighErrorRate
    expr: rate(api_errors_total[5m]) > 0.05
    for: 5m
    annotations:
      summary: "High error rate detected"

  - alert: SlowPredictions
    expr: histogram_quantile(0.95, prediction_duration_seconds) > 1
    for: 5m
    annotations:
      summary: "Slow predictions detected"

  - alert: ModelsNotLoaded
    expr: models_loaded == 0
    for: 1m
    annotations:
      summary: "No models loaded - API degraded"

  - alert: HighLatency
    expr: histogram_quantile(0.99, api_request_duration_seconds) > 0.5
    for: 5m
    annotations:
      summary: "High API latency detected"
```

---

## 📊 Dashboard Examples

### Built-in Dashboard (/dashboard/summary)
Returns JSON with:
- Current status
- Total requests, predictions, errors
- Active request count
- Endpoint performance

### Grafana Panel Examples

**1. Request Rate (Graph)**
```
Query: rate(api_requests_total[1m])
Title: Requests per Second
```

**2. Prediction Count (Stat)**
```
Query: predictions_total
Title: Total Predictions
```

**3. Error Rate (Gauge)**
```
Query: rate(api_errors_total[5m])
Title: Error Rate
```

**4. Latency Distribution (Histogram)**
```
Query: histogram_quantile(0.95, api_request_duration_seconds)
Title: P95 Latency
```

---

## 🔧 Configuration & Customization

### Change Scrape Interval

Edit `06-prometheus-configmap.yaml`:
```yaml
global:
  scrape_interval: 10s  # Change from 15s
  evaluation_interval: 10s
```

### Add Custom Metrics

In `src/app.py`, add new metrics:
```python
from prometheus_client import Counter, Histogram

# Add new metric
custom_counter = Counter('custom_metric', 'My custom metric')

# Use in code
custom_counter.inc()
```

### Modify Log Format

Edit logging configuration in `src/app.py`:
```python
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

---

## 📈 Performance Tuning

### For High Load

```yaml
# In deployment.yaml
resources:
  requests:
    cpu: 250m
    memory: 512Mi
  limits:
    cpu: 1000m
    memory: 1Gi
```

### Log Rotation

Add to deployment:
```yaml
volumeMounts:
- name: logs
  mountPath: /app/logs
```

---

## ✅ Verification Checklist

- [ ] API running with `./QUICK_START_LOCAL.sh`
- [ ] Port forward active: `kubectl port-forward -n heart-disease-api svc/heart-disease-api 8000:80`
- [ ] Health check responds: `curl http://localhost:8000/health`
- [ ] Logs endpoint works: `curl http://localhost:8000/logs`
- [ ] Dashboard accessible: `curl http://localhost:8000/dashboard/summary`
- [ ] Prometheus metrics available: `curl http://localhost:8000/prometheus`
- [ ] Make test predictions to generate metrics
- [ ] Check `api_requests.log` file exists

---

## 🎯 Next Steps

1. **Start API with logging:**
   ```bash
   ./deploy/kubernetes/QUICK_START_LOCAL.sh
   ```

2. **View logs:**
   ```bash
   curl http://localhost:8000/logs
   ```

3. **Access dashboard:**
   ```bash
   curl http://localhost:8000/dashboard/summary
   ```

4. **Make predictions to generate metrics:**
   ```bash
   curl -X POST http://localhost:8000/predict \
     -H "Content-Type: application/json" \
     -d '{"age": 55, "sex": 1, ...'
   ```

5. **(Optional) Deploy Prometheus:**
   ```bash
   kubectl apply -f deploy/kubernetes/06-prometheus-configmap.yaml
   ```

6. **(Optional) Deploy Grafana for visualization**

---

## 📚 Resources

- **Prometheus Docs**: https://prometheus.io/docs/
- **Grafana Docs**: https://grafana.com/docs/grafana/latest/
- **FastAPI Monitoring**: https://fastapi.tiangolo.com/
- **prometheus-client**: https://github.com/prometheus/client_python

---

## ✨ Summary

Your API now has **3-tier monitoring**:

1. ✅ **Built-in** - No dependencies, instant access to logs & dashboard
2. ✅ **Prometheus** - Metrics scraping & time-series storage
3. ✅ **Grafana** - Beautiful visualizations & dashboards

Choose based on your needs:
- **Simple testing**: Use built-in endpoints (`/logs`, `/dashboard/summary`)
- **Production monitoring**: Deploy Prometheus + Grafana
- **Quick debugging**: Access `api_requests.log` file

**Status**: ✅ All monitoring features ready!

---

**Last Updated**: January 2025  
**Version**: 1.0.0
