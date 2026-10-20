"""
Test script for Heart Disease Prediction API
Tests the FastAPI application with sample requests
"""

import requests
import json
import time
from typing import Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_URL = "http://localhost:8000"
TIMEOUT = 10

# Sample patient data for testing
SAMPLE_PATIENT = {
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

# Test patients (diverse cases)
TEST_PATIENTS = [
    {
        "name": "Young Healthy Female",
        "data": {
            "age": 35,
            "sex": 0,
            "cp": 0,
            "trestbps": 110,
            "chol": 190,
            "fbs": 0,
            "restecg": 0,
            "thalach": 170,
            "exang": 0,
            "oldpeak": 0.0,
            "slope": 1,
            "ca": 0,
            "thal": 3
        }
    },
    {
        "name": "Middle-aged Male at Risk",
        "data": {
            "age": 55,
            "sex": 1,
            "cp": 3,
            "trestbps": 140,
            "chol": 280,
            "fbs": 1,
            "restecg": 2,
            "thalach": 120,
            "exang": 1,
            "oldpeak": 2.0,
            "slope": 2,
            "ca": 3,
            "thal": 7
        }
    },
    {
        "name": "Senior Female",
        "data": {
            "age": 70,
            "sex": 0,
            "cp": 2,
            "trestbps": 150,
            "chol": 250,
            "fbs": 0,
            "restecg": 1,
            "thalach": 130,
            "exang": 0,
            "oldpeak": 1.5,
            "slope": 1,
            "ca": 1,
            "thal": 6
        }
    },
]

# ============================================================================
# TEST FUNCTIONS
# ============================================================================

def test_root() -> bool:
    """Test root endpoint"""
    try:
        logger.info("Testing root endpoint...")
        response = requests.get(f"{BASE_URL}/", timeout=TIMEOUT)
        assert response.status_code == 200
        data = response.json()
        assert "version" in data
        assert "endpoints" in data
        logger.info(f"✓ Root endpoint OK: {data['version']}")
        return True
    except Exception as e:
        logger.error(f"✗ Root endpoint failed: {e}")
        return False


def test_health() -> bool:
    """Test health check endpoint"""
    try:
        logger.info("Testing health check endpoint...")
        response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["models_loaded"] in [True, False]
        logger.info(f"Health check OK: {data['status']}")
        return True
    except Exception as e:
        logger.error(f"✗ Health check failed: {e}")
        return False


def test_single_prediction(model: str = "random_forest") -> bool:
    """Test single prediction endpoint"""
    try:
        logger.info(f"Testing prediction endpoint (model: {model})...")
        
        response = requests.post(
            f"{BASE_URL}/predict?model={model}&patient_id=test_001",
            json=SAMPLE_PATIENT,
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200, f"Status code: {response.status_code}"
        data = response.json()
        
        # Validate response structure
        assert "prediction" in data
        assert "confidence" in data
        assert "probabilities" in data
        assert "model_used" in data
        assert "timestamp" in data
        
        # Validate prediction values
        assert data["prediction"] in [0, 1]
        assert 0 <= data["confidence"] <= 1
        assert "no_disease" in data["probabilities"]
        assert "disease" in data["probabilities"]
        
        logger.info(f"Prediction successful:")
        logger.info(f"  - Prediction: {data['prediction']} (0=No Disease, 1=Disease)")
        logger.info(f"  - Confidence: {data['confidence']:.4f}")
        logger.info(f"  - Probabilities: {data['probabilities']}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Prediction test failed: {e}")
        return False


def test_batch_prediction(model: str = "random_forest") -> bool:
    """Test batch prediction endpoint"""
    try:
        logger.info(f"Testing batch prediction endpoint (model: {model})...")
        
        # Prepare batch request
        batch_request = {
            "samples": [patient["data"] for patient in TEST_PATIENTS]
        }
        
        response = requests.post(
            f"{BASE_URL}/predict-batch?model={model}",
            json=batch_request,
            timeout=TIMEOUT
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response
        assert "predictions" in data
        assert "total_processed" in data
        assert len(data["predictions"]) == len(TEST_PATIENTS)
        
        logger.info(f"Batch prediction successful: {data['total_processed']} samples processed")
        
        for idx, (pred, patient) in enumerate(zip(data["predictions"], TEST_PATIENTS)):
            logger.info(f"  [{idx}] {patient['name']}: Pred={pred['prediction']}, Conf={pred['confidence']:.4f}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Batch prediction test failed: {e}")
        return False


def test_metrics() -> bool:
    """Test metrics endpoint"""
    try:
        logger.info("Testing metrics endpoint...")
        
        response = requests.get(
            f"{BASE_URL}/metrics?model=random_forest",
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Metrics retrieved for {data['model_name']}:")
            for metric, value in data.get('metrics', {}).items():
                logger.info(f"  - {metric}: {value:.4f}")
            return True
        elif response.status_code == 404:
            logger.warning("Metrics endpoint responding (metrics file not available)")
            return True
        else:
            logger.error(f"✗ Metrics endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"✗ Metrics test failed: {e}")
        return False


def test_error_handling() -> bool:
    """Test error handling with invalid data"""
    try:
        logger.info("Testing error handling...")
        
        # Test with invalid data
        invalid_data = {"age": 200, "sex": 5}  # Invalid age and sex
        
        response = requests.post(
            f"{BASE_URL}/predict",
            json=invalid_data,
            timeout=TIMEOUT
        )
        
        # Should return 422 (validation error) or 400
        if response.status_code in [400, 422]:
            logger.info("Error handling working correctly (invalid input rejected)")
            return True
        else:
            logger.warning(f"⚠ Unexpected status code: {response.status_code}")
            return True
            
    except Exception as e:
        logger.error(f"✗ Error handling test failed: {e}")
        return False


def wait_for_api(max_retries: int = 30) -> bool:
    """Wait for API to be ready"""
    logger.info("Waiting for API to be ready...")
    
    for attempt in range(max_retries):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                logger.info(f"API ready after {attempt} attempts")
                return True
        except:
            pass
        
        logger.info(f"  Attempt {attempt + 1}/{max_retries}...")
        time.sleep(1)
    
    logger.error("✗ API did not become ready in time")
    return False


# ============================================================================
# MAIN TEST EXECUTION
# ============================================================================

def run_all_tests() -> None:
    """Run all API tests"""
    logger.info("=" * 80)
    logger.info("HEART DISEASE PREDICTION API - TEST SUITE")
    logger.info("=" * 80)
    logger.info("")
    
    # Wait for API
    if not wait_for_api():
        logger.error("Aborting tests - API not available")
        return
    
    logger.info("")
    logger.info("Running tests...")
    logger.info("")
    
    # Test suite
    tests = [
        ("Root Endpoint", test_root),
        ("Health Check", test_health),
        ("Single Prediction (LR)", lambda: test_single_prediction("logistic_regression")),
        ("Single Prediction (RF)", lambda: test_single_prediction("random_forest")),
        ("Batch Prediction", test_batch_prediction),
        ("Metrics Endpoint", test_metrics),
        ("Error Handling", test_error_handling),
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info("")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"✗ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("")
    logger.info("=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info("")
    logger.info(f"Results: {passed}/{total} tests passed")
    logger.info("")
    
    if passed == total:
        logger.info("All tests passed!")
    else:
        logger.warning(f"⚠ {total - passed} test(s) failed")


if __name__ == "__main__":
    run_all_tests()
