"""
FastAPI Application for Heart Disease Classification Model Serving
Provides REST API endpoints for model predictions with health checks and metrics.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import joblib
import numpy as np
import pandas as pd
import logging
from pathlib import Path
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# APPLICATION INITIALIZATION
# ============================================================================

app = FastAPI(
    title="Heart Disease Prediction API",
    description="FastAPI service for heart disease classification using ML models",
    version="1.0.0"
)

# ============================================================================
# CONFIGURATION & PATHS
# ============================================================================

BASE_DIR = Path(__file__).parent.parent
ARTIFACTS_DIR = BASE_DIR / 'artifacts'
MODELS_DIR = ARTIFACTS_DIR / 'models'

# Model paths
LR_MODEL_PATH = MODELS_DIR / 'logistic_regression_model.pkl'
RF_MODEL_PATH = MODELS_DIR / 'random_forest_model.pkl'
SCALER_PATH = MODELS_DIR / 'scaler.pkl'

# Feature names
FEATURE_NAMES = [
    'age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg',
    'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal'
]

# ============================================================================
# APPLICATION STATE
# ============================================================================

class ModelState:
    """Store loaded models in memory"""
    lr_model = None
    rf_model = None
    scaler = None
    models_loaded = False
    load_error = None

state = ModelState()

# ============================================================================
# PYDANTIC MODELS (Request/Response Schemas)
# ============================================================================

class PatientData(BaseModel):
    """Patient health metrics for prediction"""
    age: int = Field(..., ge=0, le=150, description="Patient age in years")
    sex: int = Field(..., ge=0, le=1, description="Sex (0=Female, 1=Male)")
    cp: int = Field(..., ge=0, le=3, description="Chest pain type (0-3)")
    trestbps: int = Field(..., ge=80, le=200, description="Resting blood pressure (mmHg)")
    chol: int = Field(..., ge=100, le=500, description="Serum cholesterol (mg/dl)")
    fbs: int = Field(..., ge=0, le=1, description="Fasting blood sugar (0/1)")
    restecg: int = Field(..., ge=0, le=2, description="Resting ECG (0-2)")
    thalach: int = Field(..., ge=60, le=200, description="Max heart rate achieved")
    exang: int = Field(..., ge=0, le=1, description="Exercise induced angina (0/1)")
    oldpeak: float = Field(..., ge=0, le=10, description="ST depression")
    slope: int = Field(..., ge=0, le=2, description="ST segment slope (0-2)")
    ca: int = Field(..., ge=0, le=4, description="Number of major vessels (0-4)")
    thal: int = Field(..., ge=3, le=7, description="Thalassemia (3/6/7)")

    class Config:
        json_schema_extra = {
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
                "thal": 6
            }
        }


class PredictionResponse(BaseModel):
    """Model prediction response"""
    patient_id: Optional[str] = None
    prediction: int = Field(description="Prediction (0=No Disease, 1=Disease)")
    confidence: float = Field(description="Confidence score (0-1)")
    probabilities: Dict[str, float] = Field(description="Class probabilities")
    model_used: str = Field(description="Model used for prediction")
    timestamp: str = Field(description="Prediction timestamp")


class BatchPredictionRequest(BaseModel):
    """Batch prediction request"""
    samples: List[PatientData] = Field(..., min_items=1, max_items=100)


class BatchPredictionResponse(BaseModel):
    """Batch prediction response"""
    predictions: List[PredictionResponse]
    total_processed: int
    timestamp: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    models_loaded: bool
    version: str


class MetricsResponse(BaseModel):
    """Model metrics response"""
    model_name: str
    metrics: Dict[str, float]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def load_models() -> bool:
    """Load models from disk into memory"""
    try:
        logger.info("Loading models from disk...")
        
        if not MODELS_DIR.exists():
            logger.error(f"Models directory not found: {MODELS_DIR}")
            state.load_error = f"Models directory not found: {MODELS_DIR}"
            return False
        
        # Load Logistic Regression model
        if LR_MODEL_PATH.exists():
            state.lr_model = joblib.load(LR_MODEL_PATH)
            logger.info("✓ Logistic Regression model loaded")
        else:
            logger.warning(f"LR model not found: {LR_MODEL_PATH}")
        
        # Load Random Forest model
        if RF_MODEL_PATH.exists():
            state.rf_model = joblib.load(RF_MODEL_PATH)
            logger.info("✓ Random Forest model loaded")
        else:
            logger.warning(f"RF model not found: {RF_MODEL_PATH}")
        
        # Load scaler
        if SCALER_PATH.exists():
            state.scaler = joblib.load(SCALER_PATH)
            logger.info("✓ Feature scaler loaded")
        else:
            logger.warning(f"Scaler not found: {SCALER_PATH}")
        
        if state.lr_model and state.rf_model and state.scaler:
            state.models_loaded = True
            logger.info("✓ All models loaded successfully")
            return True
        else:
            logger.error("Some models failed to load")
            return False
            
    except Exception as e:
        logger.error(f"Error loading models: {e}")
        state.load_error = str(e)
        return False


def prepare_features(patient: PatientData) -> np.ndarray:
    """Convert PatientData to feature array"""
    features = np.array([[
        patient.age, patient.sex, patient.cp, patient.trestbps,
        patient.chol, patient.fbs, patient.restecg, patient.thalach,
        patient.exang, patient.oldpeak, patient.slope, patient.ca, patient.thal
    ]])
    
    # Scale features
    features_scaled = state.scaler.transform(features)
    return features_scaled


def make_prediction(features: np.ndarray, model_name: str = 'random_forest') -> Dict[str, Any]:
    """Make prediction using specified model"""
    if model_name == 'logistic_regression':
        if state.lr_model is None:
            raise ValueError("Logistic Regression model not loaded")
        model = state.lr_model
    elif model_name == 'random_forest':
        if state.rf_model is None:
            raise ValueError("Random Forest model not loaded")
        model = state.rf_model
    else:
        raise ValueError(f"Unknown model: {model_name}")
    
    # Get prediction
    prediction = model.predict(features)[0]
    probabilities = model.predict_proba(features)[0]
    
    return {
        'prediction': int(prediction),
        'confidence': float(probabilities[int(prediction)]),
        'probabilities': {
            'no_disease': float(probabilities[0]),
            'disease': float(probabilities[1])
        }
    }


# ============================================================================
# LIFECYCLE EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize on application startup"""
    logger.info("Starting Heart Disease Prediction API...")
    load_models()
    if state.models_loaded:
        logger.info("✓ Application ready for predictions")
    else:
        logger.warning("⚠ Application started but models not fully loaded")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("Shutting down Heart Disease Prediction API...")


# ============================================================================
# HEALTH CHECK ENDPOINTS
# ============================================================================

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint"""
    return {
        "message": "Heart Disease Prediction API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "predict": "/predict",
            "predict_batch": "/predict-batch",
            "metrics": "/metrics",
            "docs": "/docs"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy" if state.models_loaded else "degraded",
        timestamp=datetime.now().isoformat(),
        models_loaded=state.models_loaded,
        version="1.0.0"
    )


# ============================================================================
# PREDICTION ENDPOINTS
# ============================================================================

@app.post("/predict", response_model=PredictionResponse, tags=["Predictions"])
async def predict(patient: PatientData, model: str = "random_forest", patient_id: Optional[str] = None):
    """
    Make a single prediction for heart disease classification.
    
    **Parameters:**
    - **patient**: Patient health metrics
    - **model**: Model to use (logistic_regression or random_forest)
    - **patient_id**: Optional patient identifier
    
    **Returns:**
    - **prediction**: 0 (No Disease) or 1 (Disease)
    - **confidence**: Confidence score (0-1)
    - **probabilities**: Probability for each class
    """
    try:
        if not state.models_loaded:
            raise HTTPException(
                status_code=503,
                detail="Models not loaded. Service unavailable."
            )
        
        logger.info(f"Prediction request - Patient: {patient_id}, Model: {model}")
        
        # Prepare features
        features = prepare_features(patient)
        
        # Make prediction
        result = make_prediction(features, model)
        
        response = PredictionResponse(
            patient_id=patient_id,
            prediction=result['prediction'],
            confidence=result['confidence'],
            probabilities=result['probabilities'],
            model_used=model,
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"Prediction: {result['prediction']} (confidence: {result['confidence']:.4f})")
        return response
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/predict-batch", response_model=BatchPredictionResponse, tags=["Predictions"])
async def predict_batch(request: BatchPredictionRequest, model: str = "random_forest"):
    """
    Make batch predictions for multiple patients.
    
    **Parameters:**
    - **request**: Batch of patient data (1-100 samples)
    - **model**: Model to use
    
    **Returns:**
    - List of predictions with confidence scores
    """
    try:
        if not state.models_loaded:
            raise HTTPException(
                status_code=503,
                detail="Models not loaded. Service unavailable."
            )
        
        logger.info(f"Batch prediction request - Samples: {len(request.samples)}, Model: {model}")
        
        predictions = []
        for idx, patient in enumerate(request.samples):
            features = prepare_features(patient)
            result = make_prediction(features, model)
            
            predictions.append(PredictionResponse(
                patient_id=f"batch_{idx}",
                prediction=result['prediction'],
                confidence=result['confidence'],
                probabilities=result['probabilities'],
                model_used=model,
                timestamp=datetime.now().isoformat()
            ))
        
        logger.info(f"Batch processing completed: {len(predictions)} samples")
        
        return BatchPredictionResponse(
            predictions=predictions,
            total_processed=len(predictions),
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================================
# METRICS ENDPOINTS
# ============================================================================

@app.get("/metrics", tags=["Metrics"])
async def get_metrics(model: str = "random_forest"):
    """
    Get model metrics and performance information.
    
    **Parameters:**
    - **model**: Model name (logistic_regression or random_forest)
    """
    try:
        metrics_file = ARTIFACTS_DIR / 'metrics.json'
        
        if not metrics_file.exists():
            raise HTTPException(
                status_code=404,
                detail="Metrics file not found"
            )
        
        with open(metrics_file, 'r') as f:
            all_metrics = json.load(f)
        
        if model == 'logistic_regression':
            model_metrics = all_metrics.get('logistic_regression', {})
        elif model == 'random_forest':
            model_metrics = all_metrics.get('random_forest', {})
        else:
            raise HTTPException(status_code=400, detail=f"Unknown model: {model}")
        
        return MetricsResponse(
            model_name=model,
            metrics=model_metrics
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving metrics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    logger.error(f"HTTP Exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "timestamp": datetime.now().isoformat()
        }
    )


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
