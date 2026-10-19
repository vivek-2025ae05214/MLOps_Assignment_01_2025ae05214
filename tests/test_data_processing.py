"""
Unit tests for data processing module.
Tests data loading, preprocessing, scaling, and transformations.
"""

import pytest
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from pathlib import Path
import tempfile
import os


class TestDataProcessing:
    """Test suite for data processing functions."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample heart disease dataset for testing."""
        np.random.seed(42)
        data = {
            'age': np.random.randint(30, 80, 100),
            'sex': np.random.choice([0, 1], 100),
            'cp': np.random.choice([0, 1, 2, 3], 100),
            'trestbps': np.random.randint(90, 200, 100),
            'chol': np.random.randint(100, 400, 100),
            'fbs': np.random.choice([0, 1], 100),
            'restecg': np.random.choice([0, 1, 2], 100),
            'thalach': np.random.randint(60, 200, 100),
            'exang': np.random.choice([0, 1], 100),
            'oldpeak': np.random.uniform(0, 6, 100),
            'slope': np.random.choice([0, 1, 2], 100),
            'ca': np.random.choice([0, 1, 2, 3], 100),
            'thal': np.random.choice([3, 6, 7], 100),
            'target': np.random.choice([0, 1, 2, 3, 4], 100),
        }
        return pd.DataFrame(data)
    
    def test_dataframe_loaded(self, sample_data):
        """Test that DataFrame is loaded correctly."""
        assert isinstance(sample_data, pd.DataFrame)
        assert len(sample_data) == 100
        assert 'target' in sample_data.columns
    
    def test_data_shape(self, sample_data):
        """Test DataFrame shape."""
        assert sample_data.shape == (100, 14)
    
    def test_no_missing_values(self, sample_data):
        """Test that there are no missing values in critical columns."""
        assert not sample_data.isnull().any().any()
    
    def test_target_binary_conversion(self, sample_data):
        """Test conversion of target to binary classification."""
        df = sample_data.copy()
        # Convert target to binary: 0 = no disease, 1 = disease present
        df['target'] = (df['target'] > 0).astype(int)
        
        assert df['target'].isin([0, 1]).all()
        assert len(df['target'].unique()) <= 2
    
    def test_feature_scaling(self, sample_data):
        """Test feature scaling with StandardScaler."""
        df = sample_data.copy()
        features = df.drop('target', axis=1)
        
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(features)
        scaled_df = pd.DataFrame(scaled_features, columns=features.columns)
        
        # Check that scaled features have mean ~0 and std ~1
        assert np.allclose(scaled_df.mean(), 0, atol=1e-6)
        assert np.allclose(scaled_df.std(), 1, atol=1e-6)
    
    def test_feature_scaling_preserves_shape(self, sample_data):
        """Test that scaling preserves DataFrame shape."""
        df = sample_data.copy()
        features = df.drop('target', axis=1)
        original_shape = features.shape
        
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(features)
        
        assert scaled_features.shape == original_shape
    
    def test_train_test_split(self, sample_data):
        """Test train-test split with stratification."""
        df = sample_data.copy()
        df['target'] = (df['target'] > 0).astype(int)
        
        from sklearn.model_selection import train_test_split
        X = df.drop('target', axis=1)
        y = df['target']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        assert len(X_train) + len(X_test) == len(X)
        assert len(y_train) + len(y_test) == len(y)
        assert len(X_train) == len(y_train)
        assert len(X_test) == len(y_test)
    
    def test_class_distribution_balanced(self, sample_data):
        """Test that class distribution is reasonably balanced."""
        df = sample_data.copy()
        df['target'] = (df['target'] > 0).astype(int)
        
        class_dist = df['target'].value_counts()
        # Check that neither class is more than 90% of data
        assert (class_dist / len(df) < 0.9).all()
    
    def test_feature_columns_exist(self, sample_data):
        """Test that required feature columns exist."""
        required_features = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs',
                           'restecg', 'thalach', 'exang', 'oldpeak', 'slope',
                           'ca', 'thal']
        for feature in required_features:
            assert feature in sample_data.columns
    
    def test_data_types_numeric(self, sample_data):
        """Test that all features are numeric."""
        for col in sample_data.columns:
            assert pd.api.types.is_numeric_dtype(sample_data[col])
    
    def test_feature_encoding_consistency(self, sample_data):
        """Test that label encoding is consistent."""
        df = sample_data.copy()
        col = 'sex'
        
        encoder = LabelEncoder()
        encoded = encoder.fit_transform(df[col])
        
        assert len(encoded) == len(df)
        assert len(encoder.classes_) >= 1


class TestDataValidation:
    """Test suite for data validation rules."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample heart disease dataset."""
        np.random.seed(42)
        data = {
            'age': np.random.randint(30, 80, 100),
            'sex': np.random.choice([0, 1], 100),
            'cp': np.random.choice([0, 1, 2, 3], 100),
            'trestbps': np.random.randint(90, 200, 100),
            'chol': np.random.randint(100, 400, 100),
            'target': np.random.choice([0, 1], 100),
        }
        return pd.DataFrame(data)
    
    def test_age_range(self, sample_data):
        """Test that age is within reasonable range."""
        assert (sample_data['age'] > 0).all()
        assert (sample_data['age'] < 150).all()
    
    def test_blood_pressure_valid(self, sample_data):
        """Test that blood pressure values are reasonable."""
        assert (sample_data['trestbps'] > 0).all()
        assert (sample_data['trestbps'] < 300).all()
    
    def test_cholesterol_valid(self, sample_data):
        """Test that cholesterol values are reasonable."""
        assert (sample_data['chol'] > 0).all()
        assert (sample_data['chol'] < 500).all()
    
    def test_target_binary_valid(self, sample_data):
        """Test that target is valid binary classification."""
        assert sample_data['target'].isin([0, 1]).all()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
