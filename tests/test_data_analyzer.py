"""
Testes unitários para o módulo de análise de dados.
"""

import pytest
import pandas as pd
import numpy as np
from src.analysis.data_analyzer import DataAnalyzer

@pytest.fixture
def sample_dataframe():
    """Cria um DataFrame de exemplo para testes."""
    return pd.DataFrame({
        'numeric': [1, 2, 3, 4, 5],
        'categorical': ['A', 'B', 'A', 'C', 'B'],
        'values': [10.5, 20.5, 30.5, 40.5, 50.5]
    })

@pytest.fixture
def analyzer(sample_dataframe):
    """Cria uma instância do DataAnalyzer com o DataFrame de exemplo."""
    return DataAnalyzer(sample_dataframe)

def test_get_basic_info(analyzer):
    """Testa a função get_basic_info."""
    info = analyzer.get_basic_info()
    assert info['shape'] == (5, 3)
    assert set(info['columns']) == {'numeric', 'categorical', 'values'}
    assert 'dtypes' in info
    assert 'missing_values' in info

def test_get_statistical_summary(analyzer):
    """Testa a função get_statistical_summary."""
    summary = analyzer.get_statistical_summary()
    assert isinstance(summary, pd.DataFrame)
    assert 'numeric' in summary.columns
    assert 'values' in summary.columns

def test_get_correlation_matrix(analyzer):
    """Testa a função get_correlation_matrix."""
    corr = analyzer.get_correlation_matrix()
    assert isinstance(corr, pd.DataFrame)
    assert 'numeric' in corr.columns
    assert 'values' in corr.columns

def test_get_column_analysis(analyzer):
    """Testa a função get_column_analysis."""
    # Teste para coluna numérica
    num_analysis = analyzer.get_column_analysis('numeric')
    assert 'mean' in num_analysis
    assert 'median' in num_analysis
    assert 'std' in num_analysis
    
    # Teste para coluna categórica
    cat_analysis = analyzer.get_column_analysis('categorical')
    assert 'most_common' in cat_analysis
    assert 'unique_values' in cat_analysis
