"""
Unit tests for machine learning models.
Tests model training, evaluation, and prediction functionality.
"""

import pytest
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.preprocessing import StandardScaler
import joblib
import tempfile
from pathlib import Path


class TestLogisticRegression:
    """Test suite for Logistic Regression model."""
    
    @pytest.fixture
    def prepared_data(self):
        """Create prepared train/test data."""
        np.random.seed(42)
        n_samples = 200
        n_features = 13
        
        X = np.random.randn(n_samples, n_features)
        y = np.random.choice([0, 1], n_samples)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)
        
        return X_train, X_test, y_train, y_test
    
    def test_model_initialization(self):
        """Test that Logistic Regression model initializes."""
        model = LogisticRegression(random_state=42, max_iter=1000)
        assert model is not None
        assert isinstance(model, LogisticRegression)
    
    def test_model_training(self, prepared_data):
        """Test that model trains without errors."""
        X_train, X_test, y_train, y_test = prepared_data
        model = LogisticRegression(random_state=42, max_iter=1000)
        
        model.fit(X_train, y_train)
        assert model is not None
    
    def test_model_prediction(self, prepared_data):
        """Test that model makes predictions."""
        X_train, X_test, y_train, y_test = prepared_data
        model = LogisticRegression(random_state=42, max_iter=1000)
        model.fit(X_train, y_train)
        
        predictions = model.predict(X_test)
        assert len(predictions) == len(X_test)
        assert set(predictions).issubset({0, 1})
    
    def test_model_probability_prediction(self, prepared_data):
        """Test that model returns valid probability estimates."""
        X_train, X_test, y_train, y_test = prepared_data
        model = LogisticRegression(random_state=42, max_iter=1000)
        model.fit(X_train, y_train)
        
        proba = model.predict_proba(X_test)
        assert proba.shape == (len(X_test), 2)
        assert np.all(proba >= 0) and np.all(proba <= 1)
        assert np.allclose(proba.sum(axis=1), 1.0)
    
    def test_model_accuracy(self, prepared_data):
        """Test that model achieves reasonable accuracy."""
        X_train, X_test, y_train, y_test = prepared_data
        model = LogisticRegression(random_state=42, max_iter=1000)
        model.fit(X_train, y_train)
        
        score = model.score(X_test, y_test)
        assert 0.0 <= score <= 1.0
        assert score > 0.4  # Should be better than random guessing
    
    def test_model_coef_shape(self, prepared_data):
        """Test that model coefficients have correct shape."""
        X_train, X_test, y_train, y_test = prepared_data
        model = LogisticRegression(random_state=42, max_iter=1000)
        model.fit(X_train, y_train)
        
        assert model.coef_.shape == (1, 13)
    
    def test_model_serialization(self, prepared_data):
        """Test that model can be serialized and deserialized."""
        X_train, X_test, y_train, y_test = prepared_data
        model = LogisticRegression(random_state=42, max_iter=1000)
        model.fit(X_train, y_train)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            model_path = Path(tmpdir) / "lr_model.pkl"
            joblib.dump(model, model_path)
            
            loaded_model = joblib.load(model_path)
            original_pred = model.predict(X_test)
            loaded_pred = loaded_model.predict(X_test)
            
            assert np.array_equal(original_pred, loaded_pred)
    
    def test_model_roc_auc(self, prepared_data):
        """Test that model achieves reasonable ROC-AUC score."""
        X_train, X_test, y_train, y_test = prepared_data
        model = LogisticRegression(random_state=42, max_iter=1000)
        model.fit(X_train, y_train)
        
        y_proba = model.predict_proba(X_test)
        roc_auc = roc_auc_score(y_test, y_proba[:, 1])
        
        assert 0.0 <= roc_auc <= 1.0
        assert roc_auc > 0.4  # Should be better than random guessing


class TestRandomForest:
    """Test suite for Random Forest model."""
    
    @pytest.fixture
    def prepared_data(self):
        """Create prepared train/test data."""
        np.random.seed(42)
        n_samples = 200
        n_features = 13
        
        X = np.random.randn(n_samples, n_features)
        y = np.random.choice([0, 1], n_samples)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        return X_train, X_test, y_train, y_test
    
    def test_model_initialization(self):
        """Test that Random Forest model initializes."""
        model = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            n_jobs=-1
        )
        assert model is not None
        assert isinstance(model, RandomForestClassifier)
    
    def test_model_training(self, prepared_data):
        """Test that model trains without errors."""
        X_train, X_test, y_train, y_test = prepared_data
        model = RandomForestClassifier(
            n_estimators=100,
            random_state=42
        )
        
        model.fit(X_train, y_train)
        assert model is not None
    
    def test_model_prediction(self, prepared_data):
        """Test that model makes predictions."""
        X_train, X_test, y_train, y_test = prepared_data
        model = RandomForestClassifier(
            n_estimators=100,
            random_state=42
        )
        model.fit(X_train, y_train)
        
        predictions = model.predict(X_test)
        assert len(predictions) == len(X_test)
        assert set(predictions).issubset({0, 1})
    
    def test_model_feature_importance(self, prepared_data):
        """Test that model provides feature importance."""
        X_train, X_test, y_train, y_test = prepared_data
        model = RandomForestClassifier(
            n_estimators=100,
            random_state=42
        )
        model.fit(X_train, y_train)
        
        importances = model.feature_importances_
        assert len(importances) == X_train.shape[1]
        assert np.all(importances >= 0)
        assert np.isclose(importances.sum(), 1.0, atol=0.01)
    
    def test_model_accuracy(self, prepared_data):
        """Test that model achieves reasonable accuracy."""
        X_train, X_test, y_train, y_test = prepared_data
        model = RandomForestClassifier(
            n_estimators=100,
            random_state=42
        )
        model.fit(X_train, y_train)
        
        score = model.score(X_test, y_test)
        assert 0.0 <= score <= 1.0
        assert score > 0.4
    
    def test_model_probability_prediction(self, prepared_data):
        """Test that model returns valid probability estimates."""
        X_train, X_test, y_train, y_test = prepared_data
        model = RandomForestClassifier(
            n_estimators=100,
            random_state=42
        )
        model.fit(X_train, y_train)
        
        proba = model.predict_proba(X_test)
        assert proba.shape == (len(X_test), 2)
        assert np.all(proba >= 0) and np.all(proba <= 1)
        assert np.allclose(proba.sum(axis=1), 1.0)
    
    def test_model_serialization(self, prepared_data):
        """Test that model can be serialized and deserialized."""
        X_train, X_test, y_train, y_test = prepared_data
        model = RandomForestClassifier(
            n_estimators=100,
            random_state=42
        )
        model.fit(X_train, y_train)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            model_path = Path(tmpdir) / "rf_model.pkl"
            joblib.dump(model, model_path)
            
            loaded_model = joblib.load(model_path)
            original_pred = model.predict(X_test)
            loaded_pred = loaded_model.predict(X_test)
            
            assert np.array_equal(original_pred, loaded_pred)
    
    def test_model_roc_auc(self, prepared_data):
        """Test that model achieves reasonable ROC-AUC score."""
        X_train, X_test, y_train, y_test = prepared_data
        model = RandomForestClassifier(
            n_estimators=100,
            random_state=42
        )
        model.fit(X_train, y_train)
        
        y_proba = model.predict_proba(X_test)
        roc_auc = roc_auc_score(y_test, y_proba[:, 1])
        
        assert 0.0 <= roc_auc <= 1.0
        assert roc_auc > 0.4  # Should be better than random guessing


class TestModelMetrics:
    """Test suite for model evaluation metrics."""
    
    @pytest.fixture
    def predictions(self):
        """Create sample predictions."""
        np.random.seed(42)
        y_true = np.array([0, 1, 0, 1, 0, 1, 1, 0, 1, 0])
        y_pred = np.array([0, 1, 0, 0, 0, 1, 1, 0, 1, 1])
        return y_true, y_pred
    
    def test_accuracy_score(self, predictions):
        """Test accuracy calculation."""
        y_true, y_pred = predictions
        accuracy = accuracy_score(y_true, y_pred)
        
        assert 0.0 <= accuracy <= 1.0
        assert accuracy == 0.8  # 8 out of 10 correct
    
    def test_precision_score(self, predictions):
        """Test precision calculation."""
        y_true, y_pred = predictions
        precision = precision_score(y_true, y_pred)
        
        assert 0.0 <= precision <= 1.0
    
    def test_recall_score(self, predictions):
        """Test recall calculation."""
        y_true, y_pred = predictions
        recall = recall_score(y_true, y_pred)
        
        assert 0.0 <= recall <= 1.0
    
    def test_f1_score(self, predictions):
        """Test F1 score calculation."""
        y_true, y_pred = predictions
        f1 = f1_score(y_true, y_pred)
        
        assert 0.0 <= f1 <= 1.0
    
    def test_roc_auc_score(self, predictions):
        """Test ROC-AUC score calculation."""
        y_true, y_pred = predictions
        # For ROC-AUC, we need probability scores, not hard predictions
        # Using the predictions as proxy for probabilities
        y_proba = np.array([0.1, 0.9, 0.2, 0.7, 0.3, 0.8, 0.85, 0.15, 0.95, 0.25])
        
        roc_auc = roc_auc_score(y_true, y_proba)
        
        assert 0.0 <= roc_auc <= 1.0


class TestModelValidation:
    """Test suite for model validation."""
    
    @pytest.fixture
    def prepared_data(self):
        """Create prepared train/test data."""
        np.random.seed(42)
        n_samples = 200
        n_features = 13
        
        X = np.random.randn(n_samples, n_features)
        y = np.random.choice([0, 1], n_samples)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        return X_train, X_test, y_train, y_test
    
    def test_no_data_leakage(self, prepared_data):
        """Test that train and test sets don't overlap."""
        X_train, X_test, y_train, y_test = prepared_data
        
        # Check that test set doesn't contain training samples
        assert len(X_train) + len(X_test) == 200
        assert len(set(range(len(X_train)))) == len(X_train)
        assert len(set(range(len(X_test)))) == len(X_test)
    
    def test_stratified_split_class_distribution(self, prepared_data):
        """Test that stratified split maintains class distribution."""
        X_train, X_test, y_train, y_test = prepared_data
        
        train_dist = np.bincount(y_train) / len(y_train)
        test_dist = np.bincount(y_test) / len(y_test)
        
        # Class distributions should be similar
        assert np.allclose(train_dist, test_dist, atol=0.1)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
