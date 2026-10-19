# CI/CD Pipeline & Automated Testing Guide

## Overview

This document describes the **CI/CD Pipeline & Automated Testing** implementation for the **MLOps Assignment 01: Heart Disease Classification** project. The pipeline automates **linting**, **unit testing**, and **model training** with comprehensive artifacts and logging.

---

## 📋 Table of Contents

1. [Architecture](#architecture)
2. [Unit Tests](#unit-tests)
3. [GitHub Actions Workflow](#github-actions-workflow)
4. [Running Tests Locally](#running-tests-locally)
5. [Artifacts & Logging](#artifacts--logging)
6. [Best Practices](#best-practices)

---

## Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    GitHub Actions CI/CD Pipeline                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │    Linting &   │  │  Unit Tests  │  │  Model Training   │  │
│  │  Code Quality  │─▶│   (Pytest)   │─▶│  & Evaluation     │  │
│  └────────────────┘  └──────────────┘  └───────────────────┘  │
│                                                                  │
│  Artifacts Generated:                                           │
│  • Linting reports (flake8, pylint)                            │
│  • Test coverage (coverage.xml)                                │
│  • Model files (.pkl)                                          │
│  • Metrics (metrics.json)                                      │
│  • Training logs (logs/)                                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Files Structure

```
MLOps_Assignment_01_2025ae05214/
├── .github/
│   └── workflows/
│       └── mlops-pipeline.yml          # Main CI/CD workflow
├── test_data_processing.py              # Data processing unit tests
├── test_model.py                        # Model unit tests
├── train_and_evaluate.py                # Training script (auto-generated)
├── requirements.txt                     # Python dependencies
└── CICD_TESTING_GUIDE.md               # This file
```

---

## Unit Tests

### 1. **test_data_processing.py**

**Purpose:** Test data loading, preprocessing, and validation.

**Test Classes:**

#### `TestDataProcessing`
- `test_dataframe_loaded()` - Verify DataFrame loads correctly
- `test_data_shape()` - Check expected shape (100, 14)
- `test_no_missing_values()` - Ensure no NaN values
- `test_target_binary_conversion()` - Validate binary classification conversion
- `test_feature_scaling()` - Verify StandardScaler output (mean≈0, std≈1)
- `test_feature_scaling_preserves_shape()` - Ensure scaling doesn't change dimensions
- `test_train_test_split()` - Validate stratified split integrity
- `test_class_distribution_balanced()` - Check class balance (no class >90%)
- `test_feature_columns_exist()` - Verify required features present
- `test_data_types_numeric()` - Ensure all columns are numeric
- `test_feature_encoding_consistency()` - Test label encoding stability

#### `TestDataValidation`
- `test_age_range()` - Age must be 0 < age < 150
- `test_blood_pressure_valid()` - BP must be 0 < bp < 300
- `test_cholesterol_valid()` - Cholesterol must be 0 < chol < 500
- `test_target_binary_valid()` - Target must be {0, 1}

**Coverage:** 11 tests covering data integrity, scaling, and validation

---

### 2. **test_model.py**

**Purpose:** Test model training, evaluation, and serialization.

**Test Classes:**

#### `TestLogisticRegression`
- `test_model_initialization()` - Model instantiates correctly
- `test_model_training()` - Model trains without errors
- `test_model_prediction()` - Predictions are valid binary {0, 1}
- `test_model_probability_prediction()` - Probabilities sum to 1.0
- `test_model_accuracy()` - Accuracy > 40% (better than random)
- `test_model_coef_shape()` - Coefficients have correct shape
- `test_model_serialization()` - Model can be pickled/unpickled

#### `TestRandomForest`
- `test_model_initialization()` - Model instantiates correctly
- `test_model_training()` - Model trains without errors
- `test_model_prediction()` - Predictions are valid binary {0, 1}
- `test_model_feature_importance()` - Feature importance sums to ~1.0
- `test_model_accuracy()` - Accuracy > 40%
- `test_model_probability_prediction()` - Probabilities sum to 1.0
- `test_model_serialization()` - Model can be pickled/unpickled

#### `TestModelMetrics`
- `test_accuracy_score()` - Accuracy in [0, 1]
- `test_precision_score()` - Precision in [0, 1]
- `test_recall_score()` - Recall in [0, 1]
- `test_f1_score()` - F1 in [0, 1]

#### `TestModelValidation`
- `test_no_data_leakage()` - Train/test sets don't overlap
- `test_stratified_split_class_distribution()` - Class distributions similar

**Coverage:** 23 tests covering model training, evaluation, and validation

**Total Unit Tests:** 34 comprehensive tests

---

## GitHub Actions Workflow

### Workflow File: `.github/workflows/mlops-pipeline.yml`

The workflow consists of **4 sequential jobs**:

### Job 1: **Linting & Code Quality** (`lint-and-format`)

**Runs on:** Ubuntu Latest
**Purpose:** Static code analysis and style checking

**Tools Used:**
- **Black** - Code formatter check
- **isort** - Import statement sorting
- **Flake8** - PEP8 compliance
- **Pylint** - Advanced static analysis

**Execution:**
```bash
# Black checks code formatting
black --check --verbose . --exclude '\.github|\.ipynb_checkpoints'

# isort checks import ordering
isort --check-only --verbose . --skip-gitignore

# Flake8 checks PEP8 compliance
flake8 . --count --select=E9,F63,F7,F82 --show-source

# Pylint performs deep static analysis
pylint *.py --fail-under=7.0
```

**Artifacts Generated:**
- Linting report (uploaded for reference)
- Retention: 30 days

---

### Job 2: **Unit Tests** (`unit-tests`)

**Depends on:** `lint-and-format`
**Runs on:** Ubuntu Latest
**Purpose:** Execute unit tests with coverage analysis

**Test Execution:**
```bash
pytest -v --tb=short \
  --cov=. --cov-report=xml --cov-report=term-missing \
  test_data_processing.py test_model.py
```

**Coverage Metrics:**
- XML report generated for CodeCov integration
- Terminal report shows missing line coverage
- Coverage threshold: Aim for >80%

**Artifacts Generated:**
- `.coverage` - Binary coverage database
- `coverage.xml` - XML coverage report
- Test execution summary

**Retention:** 30 days

---

### Job 3: **Model Training & Evaluation** (`model-training`)

**Depends on:** `unit-tests`
**Runs on:** Ubuntu Latest
**Purpose:** Train models and generate production artifacts

**Steps:**

1. **Data Preparation**
   - Load/create heart disease dataset (303 samples, 13 features)
   - Stratified 80/20 train-test split
   - Feature scaling with StandardScaler

2. **Model 1: Logistic Regression**
   - Linear baseline classifier
   - Metrics: Accuracy, Precision, Recall, F1
   - Saved to: `artifacts/logistic_regression_model.pkl`

3. **Model 2: Random Forest**
   - Ensemble learning model
   - Feature importance analysis
   - Metrics: Accuracy, Precision, Recall, F1
   - Saved to: `artifacts/random_forest_model.pkl`

4. **Model Comparison & Selection**
   - Compare F1 scores
   - Select best performing model
   - Generate comprehensive metrics report

**Artifacts Generated:**
```
artifacts/
├── logistic_regression_model.pkl    # Trained LR model
├── random_forest_model.pkl          # Trained RF model
├── scaler.pkl                       # Feature scaler
└── metrics.json                     # Performance metrics

logs/
└── training_YYYYMMDD_HHMMSS.log    # Detailed training log
```

**Metrics JSON Example:**
```json
{
  "timestamp": "20240115_143022",
  "data_info": {
    "n_samples": 303,
    "n_features": 13,
    "train_size": 242,
    "test_size": 61,
    "class_distribution": {"0": 164, "1": 139}
  },
  "logistic_regression": {
    "accuracy": 0.8361,
    "precision": 0.8235,
    "recall": 0.8571,
    "f1": 0.8400
  },
  "random_forest": {
    "accuracy": 0.9016,
    "precision": 0.9130,
    "recall": 0.8929,
    "f1": 0.9028
  },
  "best_model": "Random Forest"
}
```

**Retention:** 90 days

---

### Job 4: **Pipeline Status** (`build-status`)

**Depends on:** All previous jobs
**Purpose:** Final status check and summary

**Output:**
- GitHub Step Summary with results table
- Overall pipeline success/failure

---

## Running Tests Locally

### Prerequisites

```bash
# Install Python 3.9+
python --version

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Unit Tests

```bash
# Run all tests
pytest -v

# Run data processing tests only
pytest test_data_processing.py -v

# Run model tests only
pytest test_model.py -v

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test
pytest test_data_processing.py::TestDataProcessing::test_dataframe_loaded -v
```

### Run Linting

```bash
# Black check
black --check .

# Black format (auto-fix)
black .

# isort check
isort --check-only .

# isort format (auto-fix)
isort .

# Flake8
flake8 .

# Pylint
pylint test_*.py
```

### Run Full Training Pipeline

```bash
python train_and_evaluate.py
```

---

## Artifacts & Logging

### Artifact Types

#### 1. **Model Artifacts** (`artifacts/`)

| File | Purpose | Size | Usage |
|------|---------|------|-------|
| `logistic_regression_model.pkl` | Trained LR classifier | ~5KB | Production inference |
| `random_forest_model.pkl` | Trained RF classifier | ~50KB | Production inference |
| `scaler.pkl` | Feature standardization | ~2KB | Preprocessing pipeline |
| `metrics.json` | Performance metrics | ~1KB | Model evaluation |

#### 2. **Test Artifacts** (GitHub Actions)

| File | Purpose | Retention |
|------|---------|-----------|
| `test-results/` | Coverage reports, test logs | 30 days |
| `linting-report/` | Code quality metrics | 30 days |
| `model-artifacts/` | Models, logs, metrics | 90 days |

#### 3. **Logging** (`logs/`)

**Format:** `logs/training_YYYYMMDD_HHMMSS.log`

**Contents:**
```
=== Training Started: 2024-01-15 14:30:22 ===

STEP 1: DATA PREPARATION
Dataset shape: (303, 13)
Target distribution: [164 139]
Class balance: [0.54091576 0.45908424]
Train set size: 242
Test set size: 61
Scaler saved to artifacts/scaler.pkl

STEP 2: LOGISTIC REGRESSION
Logistic Regression Results:
  Accuracy:  0.8361
  Precision: 0.8235
  Recall:    0.8571
  F1 Score:  0.8400
Model saved: artifacts/logistic_regression_model.pkl

STEP 3: RANDOM FOREST CLASSIFIER
Random Forest Results:
  Accuracy:  0.9016
  Precision: 0.9130
  Recall:    0.8929
  F1 Score:  0.9028

Top 5 Important Features:
  Feature_0: 0.1561
  Feature_2: 0.1423
  Feature_5: 0.1198
  Feature_7: 0.0987
  Feature_9: 0.0856

Model saved: artifacts/random_forest_model.pkl

STEP 4: MODEL COMPARISON
Logistic Regression F1:  0.8400
Random Forest F1:        0.9028

✓ Best Model: Random Forest

Metrics saved to artifacts/metrics.json

=== Training Completed: 2024-01-15 14:35:45 ===
```

---

## Best Practices

### 1. **Code Quality**
- ✅ All code must pass Flake8 and Pylint checks
- ✅ Use Black formatter for consistent style
- ✅ Keep line length ≤127 characters
- ✅ Use meaningful variable names

### 2. **Testing**
- ✅ Target test coverage >80%
- ✅ Write tests for both happy path and edge cases
- ✅ Use fixtures for setup/teardown
- ✅ Test data validation rules

### 3. **Model Development**
- ✅ Always stratify train-test splits for imbalanced data
- ✅ Scale features before model training
- ✅ Log all hyperparameters
- ✅ Compare multiple models
- ✅ Document feature importance

### 4. **CI/CD Pipeline**
- ✅ Keep workflow jobs modular and sequential
- ✅ Generate artifacts for every run
- ✅ Use consistent logging format
- ✅ Store metrics for trend analysis
- ✅ Set appropriate retention policies

### 5. **Reproducibility**
- ✅ Pin dependency versions in `requirements.txt`
- ✅ Use fixed random seeds (e.g., `random_state=42`)
- ✅ Document data preprocessing steps
- ✅ Version control all code and config files

---

## Integration Steps

### Step 1: Initialize Git Repository

```bash
git init
git add .
git commit -m "Initial MLOps Assignment submission"
```

### Step 2: Create GitHub Repository

1. Create new repo on GitHub
2. Push local code:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/MLOps_Assignment_01.git
   git branch -M main
   git push -u origin main
   ```

### Step 3: Trigger Pipeline

Push any change to trigger the workflow:
```bash
git push origin main
```

### Step 4: Monitor Pipeline

Visit: `https://github.com/YOUR_USERNAME/MLOps_Assignment_01/actions`

---

## Troubleshooting

### Pipeline Failures

| Issue | Solution |
|-------|----------|
| Linting fails | Run `black . && isort .` locally, then push |
| Tests fail | Check test output in GitHub Actions logs |
| Model training fails | Verify dataset availability, check memory |
| Coverage too low | Add more edge case tests |

### Performance Optimization

- Use `pytest -n auto` for parallel test execution
- Cache pip dependencies: Already configured in workflow
- Use GitHub-provided runners for faster builds

---

## Summary

This CI/CD pipeline provides:

✅ **Automated Code Quality:** Linting with Black, Flake8, Pylint  
✅ **Comprehensive Testing:** 34 unit tests with coverage reporting  
✅ **Model Training:** Automated training with artifact generation  
✅ **Detailed Logging:** Training logs for every run  
✅ **Reproducibility:** Consistent environment with pinned dependencies  
✅ **Best Practices:** Following MLOps standards for production ML  

---

**Status:** Production-ready  
**Last Updated:** January 2025  
**Coverage Target:** >80%  
**Test Count:** 34 unit tests
