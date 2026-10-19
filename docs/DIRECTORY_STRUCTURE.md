# Project Directory Structure - Organization Guide

## 📁 Current vs Recommended Structure

### ❌ Current Issues
- Documentation files scattered in root directory
- Test files in root instead of dedicated folder
- No clear separation of concerns
- Hard to navigate
- Difficult to maintain

### ✅ Recommended Structure
```
MLOps_Assignment_01_2025ae05214/
├── README.md                           # Project overview
├── requirements.txt                    # Python dependencies
├── docker-compose.yml                  # Docker Compose config
├── Dockerfile                          # Docker configuration
├── pytest.ini                          # Pytest configuration
├── .flake8                             # Flake8 linting config
├── .dockerignore                       # Docker exclusions
│
├── src/                                # Source code
│   ├── __init__.py
│   ├── app.py                          # FastAPI application
│   └── test_api.py                     # API test client
│
├── tests/                              # Unit tests
│   ├── __init__.py
│   ├── test_data_processing.py         # Data processing tests
│   ├── test_model.py                   # Model tests
│   └── conftest.py                     # Pytest fixtures (optional)
│
├── artifacts/                          # Generated outputs
│   ├── models/                         # Trained model files
│   │   ├── logistic_regression_model.pkl
│   │   ├── random_forest_model.pkl
│   │   └── scaler.pkl
│   ├── metrics.json                    # Model performance metrics
│   ├── logs/                           # Runtime logs
│   └── reproducibility_report.json     # Reproducibility info
│
├── data/                               # Data directory
│   ├── raw/                            # Raw dataset
│   │   └── heart.csv
│   └── processed/                      # Processed dataset
│       └── heart_cleaned.csv
│
├── deploy/                             # Deployment configs
│   ├── kubernetes/                     # K8s manifests
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── configmap.yaml
│   └── docker-compose-prod.yml         # Production compose
│
├── .github/                            # GitHub configuration
│   └── workflows/                      # CI/CD workflows
│       └── mlops-pipeline.yml          # GitHub Actions workflow
│
├── docs/                               # Documentation
│   ├── README.md                       # Getting started
│   ├── DOCKER_GUIDE.md                 # Docker documentation
│   ├── DOCKER_QUICK_REFERENCE.md       # Docker cheat sheet
│   ├── DOCKER_TROUBLESHOOTING.md       # Troubleshooting
│   ├── DOCKER_STEP_BY_STEP.md          # Step-by-step guide
│   ├── DOCKER_IMPLEMENTATION_SUMMARY.md # Implementation details
│   ├── DOCKER_FIX_SUMMARY.md           # Build fix explanation
│   ├── CICD_TESTING_GUIDE.md           # CI/CD documentation
│   ├── NOTEBOOK_IMPROVEMENTS.md        # Notebook enhancements
│   ├── NOTEBOOK_REVIEW_SUMMARY.md      # Code review notes
│   ├── BEFORE_AFTER_EXAMPLES.md        # Code comparisons
│   ├── IMPROVEMENT_VISUAL_GUIDE.md     # Visual improvements
│   ├── QUICK_IMPROVEMENTS_REFERENCE.md # Quick reference
│   ├── README_IMPROVEMENTS.md          # Guide index
│   ├── REVIEW_FINAL_SUMMARY.md         # Final summary
│   └── IMPLEMENTATION_CHECKLIST.md     # Completion checklist
│
├── notebooks/                          # Jupyter notebooks
│   ├── MLOps_Assignment.ipynb          # Working notebook
│   └── MLOps_Assignment_01_Final.ipynb # Final notebook
│
├── scripts/                            # Utility scripts
│   ├── setup_docker.sh                 # Docker setup (Linux/Mac)
│   ├── setup_docker.bat                # Docker setup (Windows)
│   ├── example_usage.py                # Example API usage
│   └── train_and_evaluate.py           # Model training (optional)
│
├── monitoring/                         # Monitoring configs
│   └── prometheus/                     # Prometheus setup (optional)
│       └── prometheus.yml
│
└── .gitignore                          # Git exclusions
```

---

## 📂 Folder Organization Details

### 1. **Root Level** (Configuration & Entry Points)
Essential files for running the project:
- `README.md` - Main project documentation
- `requirements.txt` - All Python dependencies
- `docker-compose.yml` - Main Docker Compose
- `Dockerfile` - Main container definition
- `pytest.ini` - Test configuration
- `.flake8`, `.dockerignore` - Tool configurations

### 2. **src/** (Application Code)
The actual FastAPI application:
- `app.py` - FastAPI server with all endpoints
- `test_api.py` - API client for testing
- `__init__.py` - Package initialization

### 3. **tests/** (Unit Tests)
Test files separate from source:
- `test_data_processing.py` - Data validation tests
- `test_model.py` - Model training tests
- `conftest.py` - Shared fixtures (optional)

### 4. **artifacts/** (Generated Outputs)
Files created during training/execution:
- `models/` - Trained model files (.pkl)
- `metrics.json` - Model performance
- `logs/` - Runtime logs
- `reproducibility_report.json` - Environment info

### 5. **data/** (Datasets)
Training and processed data:
- `raw/` - Original UCI dataset
- `processed/` - Cleaned/preprocessed data

### 6. **docs/** (Documentation)
All markdown documentation grouped:
- Docker guides
- Code review documents
- Implementation notes
- Quick references

### 7. **notebooks/** (Jupyter Notebooks)
Jupyter notebooks for interactive analysis:
- Main assignment notebook
- Final submission notebook

### 8. **scripts/** (Helper Scripts)
Utility and setup scripts:
- `setup_docker.sh/bat` - Automated Docker setup
- `example_usage.py` - API usage examples
- Training scripts

### 9. **deploy/** (Deployment Configs)
Production deployment files:
- Kubernetes manifests
- Production Docker Compose
- Deployment instructions

### 10. **.github/** (CI/CD)
GitHub Actions workflows:
- `workflows/mlops-pipeline.yml` - CI/CD pipeline

---

## 🚀 Migration Steps

### Step 1: Create Directory Structure
```bash
mkdir -p src tests artifacts/models artifacts/logs data/raw data/processed
mkdir -p docs notebooks scripts deploy/kubernetes monitoring/prometheus
mkdir -p .github/workflows
```

### Step 2: Move Files
```bash
# Move source code
mv src/app.py src/app.py (already in place)
mv src/test_api.py src/test_api.py (already in place)

# Move tests
mv test_data_processing.py tests/
mv test_model.py tests/

# Move documentation
mkdir -p docs/
mv DOCKER_*.md docs/
mv NOTEBOOK_*.md docs/
mv BEFORE_AFTER_EXAMPLES.md docs/
mv IMPROVEMENT_VISUAL_GUIDE.md docs/
mv QUICK_IMPROVEMENTS_REFERENCE.md docs/
mv README_IMPROVEMENTS.md docs/
mv REVIEW_FINAL_SUMMARY.md docs/
mv CICD_TESTING_GUIDE.md docs/
mv CI_CD_SUMMARY.md docs/
mv IMPLEMENTATION_CHECKLIST.md docs/

# Move notebooks
mkdir -p notebooks/
mv MLOps_Assignment.ipynb notebooks/
mv MLOps_Assignment_01_Final.ipynb notebooks/

# Move scripts
mkdir -p scripts/
mv setup_docker.sh scripts/
mv setup_docker.bat scripts/
mv example_usage.py scripts/
```

### Step 3: Add Missing Files
Create placeholder/init files:
```bash
touch src/__init__.py
touch tests/__init__.py
touch tests/conftest.py
echo "# Getting Started" > docs/README.md
touch notebooks/.gitkeep
touch data/raw/.gitkeep
touch data/processed/.gitkeep
touch artifacts/logs/.gitkeep
```

---

## 📋 File Classification

### 🔧 Configuration Files
```
Dockerfile
docker-compose.yml
.dockerignore
.flake8
pytest.ini
requirements.txt
```

### 📝 Documentation Files
```
docs/DOCKER_GUIDE.md
docs/DOCKER_QUICK_REFERENCE.md
docs/DOCKER_TROUBLESHOOTING.md
docs/DOCKER_STEP_BY_STEP.md
docs/DOCKER_IMPLEMENTATION_SUMMARY.md
docs/DOCKER_FIX_SUMMARY.md
docs/CICD_TESTING_GUIDE.md
docs/NOTEBOOK_IMPROVEMENTS.md
... (all other markdown files)
```

### 💻 Source Code
```
src/app.py
src/test_api.py
src/__init__.py
```

### 🧪 Test Code
```
tests/test_data_processing.py
tests/test_model.py
tests/conftest.py
tests/__init__.py
```

### 📊 Data Files
```
data/raw/heart.csv
data/processed/heart_cleaned.csv
```

### 🎯 Generated Artifacts
```
artifacts/models/logistic_regression_model.pkl
artifacts/models/random_forest_model.pkl
artifacts/models/scaler.pkl
artifacts/metrics.json
artifacts/logs/training_*.log
```

### 📖 Notebooks
```
notebooks/MLOps_Assignment.ipynb
notebooks/MLOps_Assignment_01_Final.ipynb
```

### 🚀 Scripts
```
scripts/setup_docker.sh
scripts/setup_docker.bat
scripts/example_usage.py
```

### ⚙️ GitHub
```
.github/workflows/mlops-pipeline.yml
```

---

## ✅ Benefits of This Structure

1. **Clarity** - Easy to find what you need
2. **Maintainability** - Clear separation of concerns
3. **Scalability** - Easy to add more tests, docs, models
4. **Professionalism** - Industry-standard layout
5. **CI/CD Friendly** - Works well with automated pipelines
6. **Documentation** - Easy to navigate and maintain
7. **Testing** - Proper test organization
8. **Deployment** - Clear separation of dev/prod configs

---

## 📖 How to Use This Structure

### Running Tests
```bash
pytest tests/
pytest tests/test_data_processing.py -v
pytest tests/test_model.py -v
```

### Running Application
```bash
# Using Docker Compose
docker-compose up --build

# Using Python directly
python -m uvicorn src.app:app --reload
```

### Building Docker Image
```bash
docker build -t heart-disease-api:latest .
```

### Documentation
```bash
# All docs in docs/ folder
# Start with: docs/README.md
# For Docker: docs/DOCKER_GUIDE.md
# For troubleshooting: docs/DOCKER_TROUBLESHOOTING.md
```

---

## 🔄 Git Ignore Template

Create `.gitignore` in root:
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environments
venv/
ENV/
env/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Testing
.pytest_cache/
.coverage
htmlcov/

# MLflow
mlruns/
.mlflow/

# Data
data/raw/*
data/processed/*
!data/raw/.gitkeep
!data/processed/.gitkeep

# Artifacts
artifacts/models/*
artifacts/logs/*
!artifacts/models/.gitkeep
!artifacts/logs/.gitkeep

# Environment
.env
.env.local

# Notebooks
.ipynb_checkpoints/

# OS
.DS_Store
Thumbs.db
```

---

## 📊 Before & After Comparison

### ❌ Before (Current)
```
Project Root/
├── 25+ markdown files scattered
├── Tests in root directory
├── Config files mixed with docs
├── Hard to navigate
├── Confusing for new users
```

### ✅ After (Organized)
```
Project Root/
├── Clean root with only essential files
├── Organized folders by purpose
├── Tests properly located
├── Documentation grouped
├── Easy to navigate
├── Professional structure
```

---

## 🎯 Implementation Checklist

- [ ] Create all directories
- [ ] Move test files to `tests/`
- [ ] Move docs to `docs/`
- [ ] Move notebooks to `notebooks/`
- [ ] Move scripts to `scripts/`
- [ ] Create `__init__.py` files
- [ ] Add `.gitkeep` files
- [ ] Create `.gitignore`
- [ ] Update import paths in code
- [ ] Update documentation paths
- [ ] Verify everything works
- [ ] Update README with new structure

---

## 📝 Notes

- This structure is based on Python packaging best practices
- It follows the structure recommended by major ML projects
- It's compatible with PyPI packaging (if you want to publish)
- It scales well as the project grows
- Clear separation between dev and production configs

---

**Status:** Organization plan ready for implementation  
**Complexity:** Low (just moving files)  
**Benefits:** High (professional, maintainable, scalable)
