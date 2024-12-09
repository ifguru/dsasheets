"""
Módulo de análise de dados.
Fornece funcionalidades para análise exploratória e estatística dos dados.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
import seaborn as sns
import matplotlib.pyplot as plt

class DataAnalyzer:
    """
    Classe responsável pela análise exploratória e estatística dos dados.
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        Inicializa o analisador com um DataFrame.
        
        Args:
            df (pd.DataFrame): DataFrame a ser analisado
        """
        self.df = df
        
    def get_basic_info(self) -> Dict[str, Any]:
        """
        Retorna informações básicas sobre o DataFrame.
        
        Returns:
            Dict[str, Any]: Dicionário com informações básicas
        """
        return {
            'shape': self.df.shape,
            'columns': list(self.df.columns),
            'dtypes': self.df.dtypes.to_dict(),
            'missing_values': self.df.isnull().sum().to_dict()
        }
        
    def get_statistical_summary(self) -> pd.DataFrame:
        """
        Retorna um resumo estatístico dos dados numéricos.
        
        Returns:
            pd.DataFrame: Resumo estatístico
        """
        return self.df.describe()
        
    def get_correlation_matrix(self) -> pd.DataFrame:
        """
        Calcula a matriz de correlação para variáveis numéricas.
        
        Returns:
            pd.DataFrame: Matriz de correlação
        """
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        return self.df[numeric_cols].corr()
        
    def plot_correlation_heatmap(self, figsize: Tuple[int, int] = (10, 8)) -> plt.Figure:
        """
        Cria um heatmap de correlação.
        
        Args:
            figsize (Tuple[int, int]): Tamanho da figura
            
        Returns:
            plt.Figure: Figura do matplotlib
        """
        corr_matrix = self.get_correlation_matrix()
        fig, ax = plt.subplots(figsize=figsize)
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', ax=ax)
        return fig
        
    def plot_distribution(self, column: str, figsize: Tuple[int, int] = (10, 6)) -> plt.Figure:
        """
        Plota a distribuição de uma coluna específica.
        
        Args:
            column (str): Nome da coluna
            figsize (Tuple[int, int]): Tamanho da figura
            
        Returns:
            plt.Figure: Figura do matplotlib
        """
        fig, ax = plt.subplots(figsize=figsize)
        if np.issubdtype(self.df[column].dtype, np.number):
            sns.histplot(data=self.df, x=column, ax=ax)
        else:
            sns.countplot(data=self.df, x=column, ax=ax)
        return fig
        
    def get_column_analysis(self, column: str) -> Dict[str, Any]:
        """
        Realiza uma análise detalhada de uma coluna específica.
        
        Args:
            column (str): Nome da coluna
            
        Returns:
            Dict[str, Any]: Dicionário com análise da coluna
        """
        analysis = {
            'dtype': str(self.df[column].dtype),
            'missing_values': self.df[column].isnull().sum(),
            'unique_values': self.df[column].nunique()
        }
        
        if np.issubdtype(self.df[column].dtype, np.number):
            analysis.update({
                'mean': self.df[column].mean(),
                'median': self.df[column].median(),
                'std': self.df[column].std(),
                'min': self.df[column].min(),
                'max': self.df[column].max()
            })
        else:
            analysis.update({
                'most_common': self.df[column].value_counts().head().to_dict()
            })
            
        return analysis
