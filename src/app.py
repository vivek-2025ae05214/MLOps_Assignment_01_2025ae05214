"""
Heart Disease Prediction API with Prometheus monitoring.

Provides ML model-serving endpoints for heart disease classification.
Includes structured request logging, health checks, request tracking,
model inference metrics and a Prometheus scrape endpoint.

This example is for technical demonstration only and is not a medical
diagnostic service.
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
import time
from typing import Any, Dict, List, Optional
import uuid

import joblib
import numpy as np
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    REGISTRY,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)
from pydantic import BaseModel, Field
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from starlette.middleware.base import BaseHTTPMiddleware


# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s - %(name)s - %(levelname)s - "
        "[%(funcName)s:%(lineno)d] - %(message)s"
    ),
)

logger = logging.getLogger("heart-disease-api")


def utc_timestamp() -> str:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def log_event(event: str, **fields: Any) -> None:
    """Write a structured JSON log event."""
    record = {
        "event": event,
        "timestamp": utc_timestamp(),
        **fields,
    }

    logger.info(json.dumps(record, default=str))


# ============================================================================
# CONFIGURATION AND PATHS
# ============================================================================

API_VERSION = "1.0.0"

BASE_DIR = Path(__file__).resolve().parent.parent
ARTIFACTS_DIR = BASE_DIR / "artifacts"
MODELS_DIR = ARTIFACTS_DIR / "models"

LR_MODEL_PATH = MODELS_DIR / "logistic_regression_model.pkl"
RF_MODEL_PATH = MODELS_DIR / "random_forest_model.pkl"
SCALER_PATH = MODELS_DIR / "scaler.pkl"
MODEL_METRICS_PATH = ARTIFACTS_DIR / "metrics.json"

ALLOW_DEMO_MODELS = (
    os.getenv("ALLOW_DEMO_MODELS", "false").strip().lower() == "true"
)

SUPPORTED_MODELS = {
    "logistic_regression",
    "random_forest",
}

FEATURE_NAMES = [
    "age",
    "sex",
    "cp",
    "trestbps",
    "chol",
    "fbs",
    "restecg",
    "thalach",
    "exang",
    "oldpeak",
    "slope",
    "ca",
    "thal",
]

# Prevent arbitrary URLs from producing unbounded Prometheus label values.
KNOWN_METRIC_PATHS = {
    "/",
    "/health",
    "/ready",
    "/predict",
    "/predict-batch",
    "/model-metrics",
    "/docs",
    "/redoc",
    "/openapi.json",
}

EXCLUDED_METRIC_PATHS = {
    "/metrics",
}


# ============================================================================
# PROMETHEUS METRICS
# ============================================================================

REQUEST_COUNT = Counter(
    "heart_api_http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status_code"],
)

REQUEST_DURATION = Histogram(
    "heart_api_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=(
        0.005,
        0.01,
        0.025,
        0.05,
        0.1,
        0.25,
        0.5,
        1.0,
        2.5,
        5.0,
    ),
)

REQUESTS_IN_PROGRESS = Gauge(
    "heart_api_http_requests_in_progress",
    "Number of HTTP requests currently being processed",
    ["method", "endpoint"],
)

ACTIVE_PREDICTIONS = Gauge(
    "heart_api_active_prediction_operations",
    "Number of prediction operations currently running",
    ["model"],
)

MODEL_INFERENCE_DURATION = Histogram(
    "heart_api_model_inference_duration_seconds",
    "Model prediction and probability inference duration",
    ["model"],
    buckets=(
        0.001,
        0.005,
        0.01,
        0.025,
        0.05,
        0.1,
        0.25,
        0.5,
        1.0,
    ),
)

PREDICTION_RESULTS = Counter(
    "heart_api_predictions_total",
    "Total predictions by model and predicted class",
    ["model", "prediction_class"],
)

BATCH_SIZE = Histogram(
    "heart_api_batch_size_samples",
    "Number of samples submitted in a batch",
    buckets=(1, 5, 10, 25, 50, 100),
)

ERRORS_TOTAL = Counter(
    "heart_api_errors_total",
    "Total application errors",
    ["error_type", "endpoint"],
)

MODEL_ARTIFACTS_LOADED = Gauge(
    "heart_api_model_artifacts_loaded",
    "Number of successfully loaded model artefacts",
)

MODEL_READY = Gauge(
    "heart_api_model_ready",
    "Whether the model service is ready: 1 for ready and 0 otherwise",
)


# ============================================================================
# APPLICATION STATE
# ============================================================================

class ModelState:
    """Hold loaded models and preprocessing artefacts in memory."""

    def __init__(self) -> None:
        self.lr_model: Optional[LogisticRegression] = None
        self.rf_model: Optional[RandomForestClassifier] = None
        self.scaler: Optional[StandardScaler] = None
        self.models_loaded: bool = False
        self.load_error: Optional[str] = None


state = ModelState()


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class PatientData(BaseModel):
    """Patient health metrics accepted by the prediction service."""

    age: int = Field(..., ge=0, le=150)
    sex: int = Field(..., ge=0, le=1)
    cp: int = Field(..., ge=0, le=3)
    trestbps: int = Field(..., ge=80, le=200)
    chol: int = Field(..., ge=100, le=500)
    fbs: int = Field(..., ge=0, le=1)
    restecg: int = Field(..., ge=0, le=2)
    thalach: int = Field(..., ge=60, le=220)
    exang: int = Field(..., ge=0, le=1)
    oldpeak: float = Field(..., ge=0, le=10)
    slope: int = Field(..., ge=0, le=2)
    ca: int = Field(..., ge=0, le=4)
    thal: int = Field(..., ge=3, le=7)

    model_config = {
        "json_schema_extra": {
            "example": {
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
                "thal": 6,
            }
        }
    }


class PredictionResponse(BaseModel):
    """Response returned for one model prediction."""

    patient_id: Optional[str] = None
    prediction: int
    confidence: float
    probabilities: Dict[str, float]
    model_used: str
    timestamp: str


class BatchPredictionRequest(BaseModel):
    """Request containing between one and 100 patient samples."""

    samples: List[PatientData] = Field(
        ...,
        min_length=1,
        max_length=100,
    )


class BatchPredictionResponse(BaseModel):
    """Response returned for a batch prediction request."""

    predictions: List[PredictionResponse]
    total_processed: int
    timestamp: str


class HealthResponse(BaseModel):
    """Detailed API health response."""

    status: str
    timestamp: str
    models_loaded: bool
    loaded_artifacts: int
    version: str
    load_error: Optional[str] = None


class ModelMetricsResponse(BaseModel):
    """Offline evaluation metrics for one model."""

    model_name: str
    metrics: Dict[str, float]


# ============================================================================
# MODEL FUNCTIONS
# ============================================================================

def reset_model_state() -> None:
    """Reset all in-memory model state."""
    state.lr_model = None
    state.rf_model = None
    state.scaler = None
    state.models_loaded = False
    state.load_error = None

    MODEL_READY.set(0)
    MODEL_ARTIFACTS_LOADED.set(0)


def create_demo_models() -> bool:
    """
    Create deterministic demonstration models.

    These models are trained on synthetic random data and must not be used
    for real predictions. Creation is only permitted when the
    ALLOW_DEMO_MODELS environment variable is explicitly set to true.
    """
    try:
        log_event("demo_model_creation_started")

        MODELS_DIR.mkdir(parents=True, exist_ok=True)

        random_generator = np.random.default_rng(seed=42)

        features = random_generator.normal(
            size=(200, len(FEATURE_NAMES)),
        )
        targets = random_generator.integers(
            low=0,
            high=2,
            size=200,
        )

        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(features)

        logistic_model = LogisticRegression(
            random_state=42,
            max_iter=1000,
        )
        logistic_model.fit(scaled_features, targets)

        random_forest_model = RandomForestClassifier(
            random_state=42,
            n_estimators=100,
        )
        random_forest_model.fit(scaled_features, targets)

        joblib.dump(scaler, SCALER_PATH)
        joblib.dump(logistic_model, LR_MODEL_PATH)
        joblib.dump(random_forest_model, RF_MODEL_PATH)

        log_event(
            "demo_model_creation_completed",
            warning="Models were trained on synthetic random data",
        )

        return True

    except Exception as exc:
        logger.exception("Failed to create demonstration models")

        log_event(
            "demo_model_creation_failed",
            error_type=type(exc).__name__,
        )

        return False


def load_models() -> bool:
    """
    Load the scaler and trained models from disk.

    Joblib and pickle artefacts must only come from the trusted model
    training pipeline because loading untrusted serialised files can execute
    arbitrary code.
    """
    reset_model_state()

    try:
        log_event(
            "model_loading_started",
            demo_models_allowed=ALLOW_DEMO_MODELS,
        )

        MODELS_DIR.mkdir(parents=True, exist_ok=True)

        required_paths = [
            LR_MODEL_PATH,
            RF_MODEL_PATH,
            SCALER_PATH,
        ]

        missing_paths = [
            str(path)
            for path in required_paths
            if not path.exists()
        ]

        if missing_paths:
            if not ALLOW_DEMO_MODELS:
                state.load_error = (
                    "Required model artefacts are missing: "
                    + ", ".join(missing_paths)
                )

                log_event(
                    "model_loading_failed",
                    reason="missing_model_artifacts",
                    missing_artifacts=missing_paths,
                )

                return False

            logger.warning(
                "Required model artefacts are missing. "
                "Creating demonstration models because "
                "ALLOW_DEMO_MODELS=true."
            )

            if not create_demo_models():
                state.load_error = (
                    "Unable to create demonstration model artefacts"
                )
                return False

        state.lr_model = joblib.load(LR_MODEL_PATH)
        state.rf_model = joblib.load(RF_MODEL_PATH)
        state.scaler = joblib.load(SCALER_PATH)

        loaded_artifacts = sum(
            artifact is not None
            for artifact in (
                state.lr_model,
                state.rf_model,
                state.scaler,
            )
        )

        MODEL_ARTIFACTS_LOADED.set(loaded_artifacts)

        state.models_loaded = loaded_artifacts == 3
        MODEL_READY.set(1 if state.models_loaded else 0)

        if not state.models_loaded:
            state.load_error = (
                f"Only {loaded_artifacts} of 3 artefacts were loaded"
            )

            log_event(
                "model_loading_failed",
                reason="incomplete_artifact_loading",
                loaded_artifacts=loaded_artifacts,
            )

            return False

        log_event(
            "model_loading_completed",
            loaded_artifacts=loaded_artifacts,
        )

        return True

    except Exception as exc:
        reset_model_state()
        state.load_error = (
            f"Unable to load model artefacts: {type(exc).__name__}"
        )

        logger.exception("Failed to load model artefacts")

        log_event(
            "model_loading_failed",
            reason="artifact_loading_exception",
            error_type=type(exc).__name__,
        )

        return False


def validate_model_name(model_name: str) -> None:
    """Validate that the requested model is supported."""
    if model_name not in SUPPORTED_MODELS:
        supported_values = ", ".join(sorted(SUPPORTED_MODELS))

        raise ValueError(
            f"Unknown model '{model_name}'. "
            f"Supported models: {supported_values}."
        )


def ensure_models_ready() -> None:
    """Raise an HTTP error when the model service is not ready."""
    if not state.models_loaded:
        raise HTTPException(
            status_code=503,
            detail="Models are not loaded. Service unavailable.",
        )


def prepare_features(patient: PatientData) -> np.ndarray:
    """Convert validated patient input into a scaled feature array."""
    if state.scaler is None:
        raise RuntimeError("Feature scaler is not loaded")

    features = np.array(
        [
            [
                patient.age,
                patient.sex,
                patient.cp,
                patient.trestbps,
                patient.chol,
                patient.fbs,
                patient.restecg,
                patient.thalach,
                patient.exang,
                patient.oldpeak,
                patient.slope,
                patient.ca,
                patient.thal,
            ]
        ],
        dtype=float,
    )

    return state.scaler.transform(features)


def make_prediction(
    features: np.ndarray,
    model_name: str = "random_forest",
) -> Dict[str, Any]:
    """Make a prediction and record model-level metrics."""
    validate_model_name(model_name)

    if model_name == "logistic_regression":
        selected_model = state.lr_model
    else:
        selected_model = state.rf_model

    if selected_model is None:
        raise RuntimeError(f"Model '{model_name}' is not loaded")

    active_predictions = ACTIVE_PREDICTIONS.labels(
        model=model_name,
    )

    active_predictions.inc()
    started_at = time.perf_counter()

    try:
        prediction = int(selected_model.predict(features)[0])
        probabilities = selected_model.predict_proba(features)[0]

        if len(probabilities) < 2:
            raise RuntimeError(
                "The selected model did not return two-class probabilities"
            )

        no_disease_probability = float(probabilities[0])
        disease_probability = float(probabilities[1])

        confidence = (
            disease_probability
            if prediction == 1
            else no_disease_probability
        )

        PREDICTION_RESULTS.labels(
            model=model_name,
            prediction_class=str(prediction),
        ).inc()

        return {
            "prediction": prediction,
            "confidence": confidence,
            "probabilities": {
                "no_disease": no_disease_probability,
                "disease": disease_probability,
            },
        }

    finally:
        duration = time.perf_counter() - started_at

        MODEL_INFERENCE_DURATION.labels(
            model=model_name,
        ).observe(duration)

        active_predictions.dec()


def normalise_metric_endpoint(path: str) -> str:
    """Return a bounded endpoint label for Prometheus metrics."""
    if path in KNOWN_METRIC_PATHS:
        return path

    return "__unmatched__"


def count_loaded_artifacts() -> int:
    """Return the number of model artefacts currently in memory."""
    return sum(
        artifact is not None
        for artifact in (
            state.lr_model,
            state.rf_model,
            state.scaler,
        )
    )


# ============================================================================
# APPLICATION LIFESPAN
# ============================================================================

@asynccontextmanager
async def lifespan(_: FastAPI):
    """Load models at startup and update readiness at shutdown."""
    log_event("application_starting")

    load_models()

    log_event(
        "application_started",
        models_loaded=state.models_loaded,
        load_error=state.load_error,
    )

    yield

    MODEL_READY.set(0)
    state.models_loaded = False

    log_event("application_stopped")


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="Heart Disease Prediction API",
    description=(
        "Machine-learning model serving with structured logging and "
        "Prometheus monitoring. Technical demonstration only."
    ),
    version=API_VERSION,
    lifespan=lifespan,
)


# ============================================================================
# REQUEST LOGGING AND METRICS MIDDLEWARE
# ============================================================================

class PrometheusMiddleware(BaseHTTPMiddleware):
    """Record request logs, status codes and latency metrics."""

    async def dispatch(self, request: Request, call_next):
        method = request.method
        raw_path = request.url.path

        metric_endpoint = normalise_metric_endpoint(raw_path)
        should_measure = raw_path not in EXCLUDED_METRIC_PATHS

        request_id = request.headers.get(
            "X-Request-ID",
            str(uuid.uuid4()),
        )

        started_at = time.perf_counter()
        status_code = 500

        in_progress_metric = None

        if should_measure:
            in_progress_metric = REQUESTS_IN_PROGRESS.labels(
                method=method,
                endpoint=metric_endpoint,
            )
            in_progress_metric.inc()

        log_event(
            "api_request_started",
            request_id=request_id,
            method=method,
            path=raw_path,
        )

        try:
            response = await call_next(request)
            status_code = response.status_code
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as exc:
            log_event(
                "api_request_failed",
                request_id=request_id,
                method=method,
                path=raw_path,
                error_type=type(exc).__name__,
            )

            raise

        finally:
            duration = time.perf_counter() - started_at

            if should_measure:
                if in_progress_metric is not None:
                    in_progress_metric.dec()

                REQUEST_COUNT.labels(
                    method=method,
                    endpoint=metric_endpoint,
                    status_code=str(status_code),
                ).inc()

                REQUEST_DURATION.labels(
                    method=method,
                    endpoint=metric_endpoint,
                ).observe(duration)

            log_event(
                "api_request_completed",
                request_id=request_id,
                method=method,
                endpoint=metric_endpoint,
                status_code=status_code,
                duration_ms=round(duration * 1000, 2),
            )


app.add_middleware(PrometheusMiddleware)


# ============================================================================
# HEALTH ENDPOINTS
# ============================================================================

@app.get("/", tags=["Health"])
async def root() -> Dict[str, Any]:
    """Return API service information."""
    return {
        "message": "Heart Disease Prediction API",
        "version": API_VERSION,
        "disclaimer": (
            "Technical demonstration only; not medical advice."
        ),
        "models_loaded": state.models_loaded,
        "endpoints": {
            "health": "/health",
            "ready": "/ready",
            "predict": "/predict",
            "predict_batch": "/predict-batch",
            "prometheus_metrics": "/metrics",
            "model_metrics": "/model-metrics",
            "docs": "/docs",
            "redoc": "/redoc",
        },
    }


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
)
async def health_check() -> HealthResponse:
    """
    Return process and model-loading health information.

    This endpoint remains available when model artefacts cannot be loaded,
    allowing operators to inspect the failure reason.
    """
    return HealthResponse(
        status="healthy" if state.models_loaded else "degraded",
        timestamp=utc_timestamp(),
        models_loaded=state.models_loaded,
        loaded_artifacts=count_loaded_artifacts(),
        version=API_VERSION,
        load_error=state.load_error,
    )


@app.get("/ready", tags=["Health"])
async def readiness_check() -> Dict[str, Any]:
    """Return Kubernetes-style model readiness status."""
    if not state.models_loaded:
        raise HTTPException(
            status_code=503,
            detail="Model service is not ready",
        )

    return {
        "status": "ready",
        "timestamp": utc_timestamp(),
        "loaded_artifacts": count_loaded_artifacts(),
    }


# ============================================================================
# PREDICTION ENDPOINTS
# ============================================================================

@app.post(
    "/predict",
    response_model=PredictionResponse,
    tags=["Predictions"],
)
async def predict(
    patient: PatientData,
    model: str = "random_forest",
    patient_id: Optional[str] = None,
) -> PredictionResponse:
    """Make one model prediction."""
    ensure_models_ready()

    try:
        validate_model_name(model)

        features = prepare_features(patient)
        result = make_prediction(features, model)

        log_event(
            "prediction_completed",
            model=model,
            prediction=result["prediction"],
            confidence=round(result["confidence"], 4),
        )

        return PredictionResponse(
            patient_id=patient_id,
            prediction=result["prediction"],
            confidence=result["confidence"],
            probabilities=result["probabilities"],
            model_used=model,
            timestamp=utc_timestamp(),
        )

    except ValueError as exc:
        ERRORS_TOTAL.labels(
            error_type="validation_error",
            endpoint="/predict",
        ).inc()

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except HTTPException:
        raise

    except Exception as exc:
        logger.exception("Prediction failed")

        raise HTTPException(
            status_code=500,
            detail="Prediction failed due to an internal server error",
        ) from exc


@app.post(
    "/predict-batch",
    response_model=BatchPredictionResponse,
    tags=["Predictions"],
)
async def predict_batch(
    request: BatchPredictionRequest,
    model: str = "random_forest",
) -> BatchPredictionResponse:
    """Make predictions for between one and 100 patient samples."""
    ensure_models_ready()

    try:
        # Validate before processing any samples.
        validate_model_name(model)

        sample_count = len(request.samples)
        BATCH_SIZE.observe(sample_count)

        predictions: List[PredictionResponse] = []

        for index, patient in enumerate(request.samples):
            features = prepare_features(patient)
            result = make_prediction(features, model)

            predictions.append(
                PredictionResponse(
                    patient_id=f"batch_{index}",
                    prediction=result["prediction"],
                    confidence=result["confidence"],
                    probabilities=result["probabilities"],
                    model_used=model,
                    timestamp=utc_timestamp(),
                )
            )

        log_event(
            "batch_prediction_completed",
            model=model,
            sample_count=sample_count,
        )

        return BatchPredictionResponse(
            predictions=predictions,
            total_processed=sample_count,
            timestamp=utc_timestamp(),
        )

    except ValueError as exc:
        ERRORS_TOTAL.labels(
            error_type="validation_error",
            endpoint="/predict-batch",
        ).inc()

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except HTTPException:
        raise

    except Exception as exc:
        logger.exception("Batch prediction failed")

        raise HTTPException(
            status_code=500,
            detail="Batch prediction failed due to an internal server error",
        ) from exc


# ============================================================================
# MONITORING ENDPOINTS
# ============================================================================

@app.get(
    "/metrics",
    include_in_schema=False,
)
async def prometheus_metrics() -> Response:
    """Expose metrics in Prometheus text format."""
    return Response(
        content=generate_latest(REGISTRY),
        headers={
            "Content-Type": CONTENT_TYPE_LATEST,
        },
    )


@app.get(
    "/model-metrics",
    response_model=ModelMetricsResponse,
    tags=["Monitoring"],
)
async def get_model_metrics(
    model: str = "random_forest",
) -> ModelMetricsResponse:
    """Return offline model evaluation metrics."""
    try:
        validate_model_name(model)

        if not MODEL_METRICS_PATH.exists():
            raise HTTPException(
                status_code=404,
                detail="Model metrics file not found",
            )

        with MODEL_METRICS_PATH.open(
            "r",
            encoding="utf-8",
        ) as metrics_file:
            all_metrics = json.load(metrics_file)

        model_metrics = all_metrics.get(model)

        if model_metrics is None:
            raise HTTPException(
                status_code=404,
                detail=(
                    "Metrics are not available for model: "
                    f"{model}"
                ),
            )

        if not isinstance(model_metrics, dict):
            raise RuntimeError(
                "Model metrics must be represented as a JSON object"
            )

        numeric_metrics: Dict[str, float] = {}

        for metric_name, metric_value in model_metrics.items():
            if isinstance(metric_value, bool):
                continue

            if isinstance(metric_value, (int, float)):
                numeric_metrics[str(metric_name)] = float(metric_value)

        return ModelMetricsResponse(
            model_name=model,
            metrics=numeric_metrics,
        )

    except ValueError as exc:
        ERRORS_TOTAL.labels(
            error_type="validation_error",
            endpoint="/model-metrics",
        ).inc()

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except HTTPException:
        raise

    except json.JSONDecodeError as exc:
        logger.exception("Model metrics file contains invalid JSON")

        raise HTTPException(
            status_code=500,
            detail="Model metrics file contains invalid JSON",
        ) from exc

    except Exception as exc:
        logger.exception("Unable to read model evaluation metrics")

        raise HTTPException(
            status_code=500,
            detail="Unable to read model evaluation metrics",
        ) from exc


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    """Return a consistent JSON structure for HTTP errors."""
    if exc.status_code >= 500:
        logger.error(
            "HTTP error on %s: %s",
            request.url.path,
            exc.detail,
        )

        ERRORS_TOTAL.labels(
            error_type=f"http_{exc.status_code}",
            endpoint=normalise_metric_endpoint(request.url.path),
        ).inc()

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": utc_timestamp(),
        },
        headers=exc.headers,
    )


@app.exception_handler(Exception)
async def general_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Handle unexpected unhandled application exceptions."""
    logger.exception(
        "Unexpected error on %s",
        request.url.path,
    )

    ERRORS_TOTAL.labels(
        error_type=type(exc).__name__,
        endpoint=normalise_metric_endpoint(request.url.path),
    ).inc()

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "timestamp": utc_timestamp(),
        },
    )


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )