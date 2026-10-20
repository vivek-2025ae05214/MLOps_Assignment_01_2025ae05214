"""
DEVELOPER GUIDE: Example Usage of Trained Heart Disease Classification Models

This module demonstrates how to:
1. Load pre-trained ML models and preprocessing artifacts
2. Run single-patient predictions with confidence scores
3. Process batch predictions for multiple patients
4. Extract model performance metrics and feature importance

Models are trained via CI/CD pipeline and serialized with joblib.
Artifacts location: ./artifacts/
"""

import joblib
import numpy as np
import pandas as pd
from pathlib import Path


def load_artifacts():
    """
    INSTRUCTION: Load Pre-trained Models and Preprocessing Artifacts
    
    Retrieves serialized models from artifacts directory:
    - logistic_regression_model.pkl: Baseline classifier
    - random_forest_model.pkl: Ensemble classifier
    - scaler.pkl: StandardScaler for feature normalization
    
    REQUIREMENTS:
    - artifacts/ directory must exist
    - All three model files must be present
    
    RETURNS: (lr_model, rf_model, scaler, artifacts_dir) or (None, None, None, None) on error
    """
    artifacts_dir = Path('artifacts')
    
    if not artifacts_dir.exists():
        print("[ERROR] Artifacts directory not found in current path")
        print("INSTRUCTION: Run training pipeline first")
        print("  Command: python scripts/train_models.py")
        print("  Or: python notebooks/MLOps_Assignment_01_Final.ipynb")
        return None, None, None, None
    
    try:
        print("[LOADING] Initializing model artifacts...")
        lr_model = joblib.load(artifacts_dir / 'logistic_regression_model.pkl')
        rf_model = joblib.load(artifacts_dir / 'random_forest_model.pkl')
        scaler = joblib.load(artifacts_dir / 'scaler.pkl')
        
        print("[SUCCESS] Models and scaler loaded into memory")
        return lr_model, rf_model, scaler, artifacts_dir
    
    except FileNotFoundError as e:
        print(f"[ERROR] Failed to load artifacts: {e}")
        print("INSTRUCTION: Ensure all model files are in artifacts/ directory")
        return None, None, None, None


def example_inference():
    """
    INSTRUCTION: Single Patient Prediction Example
    
    Demonstrates prediction workflow:
    1. Load pre-trained models
    2. Prepare patient clinical data (13 features)
    3. Normalize features using fitted scaler
    4. Generate predictions with both models
    5. Display results with confidence scores
    
    INPUT: 13-feature patient data array
    OUTPUT: Predictions, probabilities, and confidence for disease classification
    """
    
    print("\n" + "="*70)
    print("SINGLE PATIENT PREDICTION WORKFLOW")
    print("="*70 + "\n")
    
    # Load Pre-trained Artifacts
    lr_model, rf_model, scaler, artifacts_dir = load_artifacts()
    
    if lr_model is None:
        print("[ABORT] Cannot proceed without trained models")
        return
    
    # Prepare Patient Clinical Data (13 features)
    # Structure: [age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal]
    sample_patient = np.array([[
        55,      # Feature 0: Age (years)
        1,       # Feature 1: Sex (0=Female, 1=Male)
        3,       # Feature 2: Chest pain type (0-3)
        130,     # Feature 3: Resting blood pressure (mmHg)
        250,     # Feature 4: Serum cholesterol (mg/dL)
        0,       # Feature 5: Fasting blood sugar (0/1)
        0,       # Feature 6: Resting ECG (0-2)
        142,     # Feature 7: Max heart rate achieved (bpm)
        1,       # Feature 8: Exercise-induced angina (0/1)
        1.4,     # Feature 9: ST depression induced by exercise
        1,       # Feature 10: ST segment slope (0-2)
        2,       # Feature 11: Number of major vessels (0-4)
        6        # Feature 12: Thalassemia type (3-7)
    ]])
    
    print("INPUT: Patient Clinical Profile")
    print(f"  Age: {sample_patient[0, 0]:.0f} years")
    print(f"  Sex: {'Male' if sample_patient[0, 1] == 1 else 'Female'}")
    print(f"  Chest Pain Type: {sample_patient[0, 2]:.0f} (0=typical, 3=atypical)")
    print(f"  Resting BP: {sample_patient[0, 3]:.0f} mmHg")
    print(f"  Cholesterol: {sample_patient[0, 4]:.0f} mg/dL")
    print()
    
    # Normalize Features Using Fitted Scaler
    print("[PROCESSING] Normalizing features with StandardScaler...")
    sample_scaled = scaler.transform(sample_patient)
    
    # Logistic Regression Prediction
    print("\nOUTPUT: Logistic Regression Model Results")
    print("-" * 70)
    lr_pred = lr_model.predict(sample_scaled)
    lr_proba = lr_model.predict_proba(sample_scaled)
    
    diagnosis_lr = "Disease Detected (Positive)" if lr_pred[0] == 1 else "No Disease (Negative)"
    confidence_lr = lr_proba[0, lr_pred[0]] * 100
    
    print(f"  Clinical Diagnosis: {diagnosis_lr}")
    print(f"  Probability of No Disease: {lr_proba[0, 0]*100:.2f}%")
    print(f"  Probability of Disease: {lr_proba[0, 1]*100:.2f}%")
    print(f"  Model Confidence: {confidence_lr:.2f}%")
    print()
    
    # Random Forest Prediction
    print("OUTPUT: Random Forest Model Results")
    print("-" * 70)
    rf_pred = rf_model.predict(sample_scaled)
    rf_proba = rf_model.predict_proba(sample_scaled)
    
    diagnosis_rf = "Disease Detected (Positive)" if rf_pred[0] == 1 else "No Disease (Negative)"
    confidence_rf = rf_proba[0, rf_pred[0]] * 100
    
    print(f"  Clinical Diagnosis: {diagnosis_rf}")
    print(f"  Probability of No Disease: {rf_proba[0, 0]*100:.2f}%")
    print(f"  Probability of Disease: {rf_proba[0, 1]*100:.2f}%")
    print(f"  Model Confidence: {confidence_rf:.2f}%")
    print()
    
    # Ensemble Voting
    print("OUTPUT: Ensemble Prediction (Model Voting)")
    print("-" * 70)
    ensemble_pred = int(np.round((lr_pred[0] + rf_pred[0]) / 2))
    ensemble_diagnosis = "Disease Detected" if ensemble_pred == 1 else "No Disease"
    print(f"  Combined Diagnosis: {ensemble_diagnosis}")
    print(f"  Voting: LR={lr_pred[0]}, RF={rf_pred[0]} (majority wins)")
    print()
    
    # Feature Importance Analysis
    print("ANALYSIS: Top 5 Most Important Features (Random Forest)")
    print("-" * 70)
    feature_importance = pd.DataFrame({
        'Feature': [f'Feature_{i}' for i in range(13)],
        'Importance': rf_model.feature_importances_
    }).sort_values('Importance', ascending=False)
    
    for idx, (_, row) in enumerate(feature_importance.head().iterrows(), 1):
        print(f"  {idx}. {row['Feature']}: {row['Importance']:.4f}")
    print()


def batch_inference_example():
    """
    INSTRUCTION: Batch Prediction for Multiple Patients
    
    Demonstrates efficient processing of multiple patient records:
    1. Load models once
    2. Prepare batch dataset (multiple patients)
    3. Run vectorized predictions
    4. Generate comparison report
    
    PERFORMANCE: Batch processing is more efficient than individual predictions
    SCALABILITY: Can handle hundreds of patients with minimal latency
    """
    
    print("\n" + "="*70)
    print("BATCH PREDICTION FOR MULTIPLE PATIENTS")
    print("="*70 + "\n")
    
    # Load Pre-trained Models
    lr_model, rf_model, scaler, artifacts_dir = load_artifacts()
    
    if lr_model is None:
        print("[ABORT] Cannot proceed without trained models")
        return
    
    # Prepare Batch Dataset (4 Diverse Patient Cases)
    print("INPUT: Patient Cohort (4 diverse clinical profiles)")
    patients = np.array([
        [55, 1, 3, 130, 250, 0, 0, 142, 1, 1.4, 1, 2, 6],  # Middle-aged male, risk factors
        [45, 0, 1, 120, 200, 0, 0, 130, 0, 0.5, 1, 0, 3],  # Young female, healthy profile
        [65, 1, 2, 150, 300, 1, 1, 100, 1, 2.0, 2, 3, 7],  # Senior male, multiple risks
        [40, 0, 0, 110, 180, 0, 0, 150, 0, 0.0, 1, 0, 3],  # Young female, excellent health
    ])
    
    # Normalize Features
    print("[PROCESSING] Normalizing {0} patient records...".format(len(patients)))
    patients_scaled = scaler.transform(patients)
    
    # Vectorized Predictions
    print("[PROCESSING] Running batch predictions...")
    rf_pred = rf_model.predict(patients_scaled)
    rf_proba = rf_model.predict_proba(patients_scaled)
    
    # Generate Results Dataframe
    results = pd.DataFrame({
        'Patient_ID': [f'Patient_{i+1}' for i in range(len(patients))],
        'Age': patients[:, 0].astype(int),
        'Clinical_Diagnosis': ['Disease (+)' if p == 1 else 'Normal (-)' for p in rf_pred],
        'Prob_No_Disease_%': rf_proba[:, 0] * 100,
        'Prob_Disease_%': rf_proba[:, 1] * 100,
    })
    
    # Display Results
    print("\nOUTPUT: Batch Prediction Results")
    print("-" * 70)
    print(results.to_string(index=False))
    print()
    print(f"Total Patients Processed: {len(results)}")
    print(f"Disease Cases Detected: {(rf_pred == 1).sum()}")
    print(f"Normal Cases: {(rf_pred == 0).sum()}")
    print()


def load_metrics():
    """
    INSTRUCTION: Load and Display Model Performance Metrics
    
    Retrieves evaluation metrics from training phase:
    - Dataset information (samples, features, split ratio)
    - Model performance (accuracy, precision, recall, F1, ROC-AUC)
    - Best model selection
    
    METRICS FILE: ./artifacts/metrics.json
    GENERATED BY: Training pipeline (CI/CD or notebook)
    """
    
    print("\n" + "="*70)
    print("MODEL PERFORMANCE METRICS (FROM TRAINING)")
    print("="*70 + "\n")
    
    metrics_file = Path('artifacts') / 'metrics.json'
    
    if not metrics_file.exists():
        print("[WARNING] Metrics file not found")
        print("INSTRUCTION: Run training pipeline to generate metrics")
        return
    
    import json
    
    print("[LOADING] Reading metrics from training artifacts...")
    with open(metrics_file, 'r') as f:
        metrics = json.load(f)
    
    # Dataset Information
    print("\nDATASET INFORMATION:")
    print("-" * 70)
    print(f"  Timestamp: {metrics['timestamp']}")
    print(f"  Total Samples: {metrics['data_info']['n_samples']}")
    print(f"  Features per Sample: {metrics['data_info']['n_features']}")
    print(f"  Training Set: {metrics['data_info']['train_size']} samples")
    print(f"  Test Set: {metrics['data_info']['test_size']} samples")
    print()
    
    # Logistic Regression Metrics
    print("LOGISTIC REGRESSION MODEL PERFORMANCE:")
    print("-" * 70)
    for metric, value in metrics['logistic_regression'].items():
        print(f"  {metric.capitalize()}: {value:.4f}")
    print()
    
    # Random Forest Metrics
    print("RANDOM FOREST MODEL PERFORMANCE:")
    print("-" * 70)
    for metric, value in metrics['random_forest'].items():
        print(f"  {metric.capitalize()}: {value:.4f}")
    print()
    
    print(f"BEST MODEL FOR PRODUCTION: {metrics['best_model'].upper()}")
    print()


def main():
    """
    INSTRUCTION: Run All Example Demonstrations
    
    Executes complete workflow:
    1. Display model metrics from training
    2. Single patient prediction example
    3. Batch patient predictions
    4. Generate comparison analysis
    
    USAGE: python scripts/example_usage.py
    """
    
    print("\n" + "#"*70)
    print("# TRAINED MODEL USAGE GUIDE")
    print("# MLOps Assignment 01: Heart Disease Classification")
    print("# Developer Examples and Workflow Demonstrations")
    print("#"*70 + "\n")
    
    # Load and display metrics
    load_metrics()
    
    # Single patient inference
    example_inference()
    
    # Batch inference
    batch_inference_example()
    
    print("="*70)
    print("ALL EXAMPLES COMPLETED SUCCESSFULLY")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
