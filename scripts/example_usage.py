"""
Example usage of trained models from CI/CD pipeline.
Shows how to load and use models for inference.
"""

import joblib
import numpy as np
import pandas as pd
from pathlib import Path


def load_artifacts():
    """Load trained models and scaler from artifacts directory."""
    artifacts_dir = Path('artifacts')
    
    if not artifacts_dir.exists():
        print("❌ Artifacts directory not found. Please run training first.")
        print("   Command: python train_and_evaluate.py")
        return None, None, None, None
    
    try:
        lr_model = joblib.load(artifacts_dir / 'logistic_regression_model.pkl')
        rf_model = joblib.load(artifacts_dir / 'random_forest_model.pkl')
        scaler = joblib.load(artifacts_dir / 'scaler.pkl')
        
        print("✓ Successfully loaded trained models and scaler")
        return lr_model, rf_model, scaler, artifacts_dir
    
    except FileNotFoundError as e:
        print(f"❌ Error loading artifacts: {e}")
        return None, None, None, None


def example_inference():
    """Example inference with trained models."""
    
    print("\n" + "="*60)
    print("MODEL INFERENCE EXAMPLE")
    print("="*60 + "\n")
    
    # Load artifacts
    lr_model, rf_model, scaler, artifacts_dir = load_artifacts()
    
    if lr_model is None:
        print("Cannot proceed without trained models.")
        return
    
    # Create sample patient data (13 features)
    sample_patient = np.array([[
        55,      # age
        1,       # sex (1=male, 0=female)
        3,       # cp (chest pain type, 0-3)
        130,     # trestbps (resting blood pressure)
        250,     # chol (cholesterol)
        0,       # fbs (fasting blood sugar)
        0,       # restecg (resting ECG)
        142,     # thalach (max heart rate)
        1,       # exang (exercise induced angina)
        1.4,     # oldpeak (ST depression)
        1,       # slope (ST segment slope)
        2,       # ca (major vessels colored)
        6        # thal (thalassemia)
    ]])
    
    print("Patient Data:")
    print(f"  Age: {sample_patient[0, 0]:.0f}")
    print(f"  Sex: {'Male' if sample_patient[0, 1] == 1 else 'Female'}")
    print(f"  Chest Pain Type: {sample_patient[0, 2]:.0f}")
    print(f"  Resting BP: {sample_patient[0, 3]:.0f} mmHg")
    print(f"  Cholesterol: {sample_patient[0, 4]:.0f} mg/dL")
    print()
    
    # Scale features
    sample_scaled = scaler.transform(sample_patient)
    
    # Logistic Regression Prediction
    print("LOGISTIC REGRESSION PREDICTION:")
    lr_pred = lr_model.predict(sample_scaled)
    lr_proba = lr_model.predict_proba(sample_scaled)
    
    diagnosis_lr = "Disease Detected" if lr_pred[0] == 1 else "No Disease"
    confidence_lr = lr_proba[0, lr_pred[0]] * 100
    
    print(f"  Diagnosis: {diagnosis_lr}")
    print(f"  Probability of No Disease: {lr_proba[0, 0]*100:.2f}%")
    print(f"  Probability of Disease: {lr_proba[0, 1]*100:.2f}%")
    print(f"  Confidence: {confidence_lr:.2f}%")
    print()
    
    # Random Forest Prediction
    print("RANDOM FOREST PREDICTION:")
    rf_pred = rf_model.predict(sample_scaled)
    rf_proba = rf_model.predict_proba(sample_scaled)
    
    diagnosis_rf = "Disease Detected" if rf_pred[0] == 1 else "No Disease"
    confidence_rf = rf_proba[0, rf_pred[0]] * 100
    
    print(f"  Diagnosis: {diagnosis_rf}")
    print(f"  Probability of No Disease: {rf_proba[0, 0]*100:.2f}%")
    print(f"  Probability of Disease: {rf_proba[0, 1]*100:.2f}%")
    print(f"  Confidence: {confidence_rf:.2f}%")
    print()
    
    # Model comparison
    print("ENSEMBLE PREDICTION (Voting):")
    ensemble_pred = int(np.round((lr_pred[0] + rf_pred[0]) / 2))
    ensemble_diagnosis = "Disease Detected" if ensemble_pred == 1 else "No Disease"
    print(f"  Diagnosis: {ensemble_diagnosis}")
    print(f"  (Logical voting from both models)")
    print()
    
    # Feature importance
    print("TOP 5 MOST IMPORTANT FEATURES (Random Forest):")
    feature_importance = pd.DataFrame({
        'Feature': [f'Feature_{i}' for i in range(13)],
        'Importance': rf_model.feature_importances_
    }).sort_values('Importance', ascending=False)
    
    for idx, (_, row) in enumerate(feature_importance.head().iterrows(), 1):
        print(f"  {idx}. {row['Feature']}: {row['Importance']:.4f}")
    print()


def batch_inference_example():
    """Example of batch inference with multiple patients."""
    
    print("\n" + "="*60)
    print("BATCH INFERENCE EXAMPLE")
    print("="*60 + "\n")
    
    # Load artifacts
    lr_model, rf_model, scaler, artifacts_dir = load_artifacts()
    
    if lr_model is None:
        print("Cannot proceed without trained models.")
        return
    
    # Create multiple patient data
    patients = np.array([
        [55, 1, 3, 130, 250, 0, 0, 142, 1, 1.4, 1, 2, 6],  # Patient 1
        [45, 0, 1, 120, 200, 0, 0, 130, 0, 0.5, 1, 0, 3],  # Patient 2
        [65, 1, 2, 150, 300, 1, 1, 100, 1, 2.0, 2, 3, 7],  # Patient 3
        [40, 0, 0, 110, 180, 0, 0, 150, 0, 0.0, 1, 0, 3],  # Patient 4
    ])
    
    # Scale features
    patients_scaled = scaler.transform(patients)
    
    # Make predictions
    rf_pred = rf_model.predict(patients_scaled)
    rf_proba = rf_model.predict_proba(patients_scaled)
    
    # Create results dataframe
    results = pd.DataFrame({
        'Patient': [f'Patient_{i+1}' for i in range(len(patients))],
        'Age': patients[:, 0],
        'Diagnosis': ['Disease' if p == 1 else 'No Disease' for p in rf_pred],
        'Probability_No_Disease': rf_proba[:, 0] * 100,
        'Probability_Disease': rf_proba[:, 1] * 100,
    })
    
    print(results.to_string(index=False))
    print()
    print(f"Total Patients: {len(results)}")
    print(f"Disease Cases: {(rf_pred == 1).sum()}")
    print(f"Healthy Cases: {(rf_pred == 0).sum()}")
    print()


def load_metrics():
    """Load and display metrics from training."""
    
    print("\n" + "="*60)
    print("TRAINING METRICS")
    print("="*60 + "\n")
    
    metrics_file = Path('artifacts') / 'metrics.json'
    
    if not metrics_file.exists():
        print("❌ Metrics file not found.")
        return
    
    import json
    
    with open(metrics_file, 'r') as f:
        metrics = json.load(f)
    
    print(f"Training Timestamp: {metrics['timestamp']}")
    print(f"Dataset Shape: {metrics['data_info']['n_samples']} samples, "
          f"{metrics['data_info']['n_features']} features")
    print(f"Train/Test Split: {metrics['data_info']['train_size']} / "
          f"{metrics['data_info']['test_size']}")
    print()
    
    print("LOGISTIC REGRESSION PERFORMANCE:")
    for metric, value in metrics['logistic_regression'].items():
        print(f"  {metric.capitalize()}: {value:.4f}")
    print()
    
    print("RANDOM FOREST PERFORMANCE:")
    for metric, value in metrics['random_forest'].items():
        print(f"  {metric.capitalize()}: {value:.4f}")
    print()
    
    print(f"Best Model: {metrics['best_model']}")
    print()


def main():
    """Run all examples."""
    
    print("\n" + "#"*60)
    print("# TRAINED MODEL USAGE EXAMPLES")
    print("# MLOps Assignment 01: Heart Disease Classification")
    print("#"*60 + "\n")
    
    # Load and display metrics
    load_metrics()
    
    # Single patient inference
    example_inference()
    
    # Batch inference
    batch_inference_example()
    
    print("="*60)
    print("EXAMPLES COMPLETED")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
