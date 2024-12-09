"""
Módulo de Machine Learning.
Fornece funcionalidades para treinamento e avaliação de modelos.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report
import xgboost as xgb

class ModelTrainer:
    """
    Classe responsável pelo treinamento e avaliação de modelos de Machine Learning.
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        Inicializa o treinador com um DataFrame.
        
        Args:
            df (pd.DataFrame): DataFrame para treinamento
        """
        self.df = df
        self.model = None
        self.label_encoders = {}
        self.feature_importance = None
        
    def prepare_data(self, target_column: str, test_size: float = 0.2) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Prepara os dados para treinamento.
        
        Args:
            target_column (str): Nome da coluna alvo
            test_size (float): Proporção do conjunto de teste
            
        Returns:
            Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]: X_train, X_test, y_train, y_test
        """
        # Separar features e target
        X = self.df.drop(columns=[target_column])
        y = self.df[target_column]
        
        # Codificar variáveis categóricas
        for column in X.select_dtypes(include=['object']):
            le = LabelEncoder()
            X[column] = le.fit_transform(X[column])
            self.label_encoders[column] = le
            
        # Dividir dados
        return train_test_split(X, y, test_size=test_size, random_state=42)
        
    def train_model(self, X_train: np.ndarray, y_train: np.ndarray, is_regression: bool = True) -> None:
        """
        Treina o modelo.
        
        Args:
            X_train (np.ndarray): Dados de treino
            y_train (np.ndarray): Labels de treino
            is_regression (bool): Se True, usa regressão, se False, classificação
        """
        if is_regression:
            self.model = xgb.XGBRegressor(random_state=42)
        else:
            self.model = xgb.XGBClassifier(random_state=42)
            
        self.model.fit(X_train, y_train)
        self.feature_importance = pd.DataFrame({
            'feature': X_train.columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
    def evaluate_model(self, X_test: np.ndarray, y_test: np.ndarray, is_regression: bool = True) -> Dict[str, Any]:
        """
        Avalia o modelo.
        
        Args:
            X_test (np.ndarray): Dados de teste
            y_test (np.ndarray): Labels de teste
            is_regression (bool): Se True, usa métricas de regressão, se False, classificação
            
        Returns:
            Dict[str, Any]: Dicionário com métricas de avaliação
        """
        if self.model is None:
            raise ValueError("Modelo não treinado ainda!")
            
        y_pred = self.model.predict(X_test)
        
        if is_regression:
            return {
                'mse': mean_squared_error(y_test, y_pred),
                'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
                'r2': self.model.score(X_test, y_test)
            }
        else:
            return {
                'accuracy': accuracy_score(y_test, y_pred),
                'classification_report': classification_report(y_test, y_pred)
            }
            
    def get_feature_importance(self) -> Optional[pd.DataFrame]:
        """
        Retorna a importância das features.
        
        Returns:
            Optional[pd.DataFrame]: DataFrame com importância das features
        """
        return self.feature_importance
        
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Faz predições com o modelo treinado.
        
        Args:
            X (pd.DataFrame): Dados para predição
            
        Returns:
            np.ndarray: Predições
        """
        if self.model is None:
            raise ValueError("Modelo não treinado ainda!")
            
        # Codificar variáveis categóricas
        X_encoded = X.copy()
        for column, le in self.label_encoders.items():
            if column in X_encoded.columns:
                X_encoded[column] = le.transform(X_encoded[column])
                
        return self.model.predict(X_encoded)
