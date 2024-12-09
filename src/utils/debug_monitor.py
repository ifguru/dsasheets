"""
Módulo para monitoramento e debug do Data Manager Pro.
Fornece funcionalidades para logging, medição de performance e verificações de sanidade.
"""

import logging
import time
import functools
import traceback
import psutil
import os
from typing import Any, Callable, Dict
from datetime import datetime
import pandas as pd
import numpy as np

# Configuração do logging
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, f'app_debug_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('DataManagerPro')

class PerformanceMonitor:
    """Monitora o desempenho da aplicação."""
    
    def __init__(self):
        self.process = psutil.Process()
        self.start_time = time.time()
        self.function_times: Dict[str, float] = {}
        
    def get_memory_usage(self) -> float:
        """Retorna o uso de memória em MB."""
        return self.process.memory_info().rss / 1024 / 1024
        
    def get_cpu_usage(self) -> float:
        """Retorna o uso de CPU em porcentagem."""
        return self.process.cpu_percent()
        
    def log_performance(self):
        """Registra métricas de performance no log."""
        memory_usage = self.get_memory_usage()
        cpu_usage = self.get_cpu_usage()
        uptime = time.time() - self.start_time
        
        logger.info(f"Performance Metrics:")
        logger.info(f"Memory Usage: {memory_usage:.2f} MB")
        logger.info(f"CPU Usage: {cpu_usage:.2f}%")
        logger.info(f"Uptime: {uptime:.2f} seconds")
        
        if self.function_times:
            logger.info("Function Execution Times:")
            for func_name, exec_time in self.function_times.items():
                logger.info(f"{func_name}: {exec_time:.4f} seconds")

def time_it(func: Callable) -> Callable:
    """Decorator para medir o tempo de execução de funções."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.debug(f"Function {func.__name__} executed in {execution_time:.4f} seconds")
            monitor.function_times[func.__name__] = execution_time
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Error in {func.__name__}: {str(e)}")
            logger.error(f"Execution time until error: {execution_time:.4f} seconds")
            logger.error(traceback.format_exc())
            raise
    return wrapper

def check_data_sanity(df: pd.DataFrame) -> bool:
    """
    Verifica a sanidade dos dados carregados.
    
    Args:
        df: DataFrame a ser verificado
        
    Returns:
        bool: True se os dados passarem nas verificações
    """
    try:
        # Verificar se há dados
        if df.empty:
            logger.error("DataFrame está vazio")
            return False
            
        # Verificar tipos de dados
        for col in df.columns:
            dtype = df[col].dtype
            logger.info(f"Coluna {col}: tipo {dtype}")
            
        # Verificar valores ausentes
        missing = df.isnull().sum()
        if missing.any():
            logger.warning("Valores ausentes encontrados:")
            for col, count in missing[missing > 0].items():
                logger.warning(f"{col}: {count} valores ausentes")
                
        # Verificar valores infinitos em colunas numéricas
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        inf_count = np.isinf(df[numeric_cols]).sum()
        if inf_count.any():
            logger.warning("Valores infinitos encontrados:")
            for col, count in inf_count[inf_count > 0].items():
                logger.warning(f"{col}: {count} valores infinitos")
                
        # Verificar memória utilizada pelo DataFrame
        memory_usage = df.memory_usage(deep=True).sum() / 1024 / 1024  # MB
        logger.info(f"Uso de memória do DataFrame: {memory_usage:.2f} MB")
        
        return True
        
    except Exception as e:
        logger.error(f"Erro na verificação de sanidade: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def check_model_sanity(model: Any, X: pd.DataFrame, y: pd.Series) -> bool:
    """
    Verifica a sanidade do modelo de Machine Learning.
    
    Args:
        model: Modelo de ML
        X: Features
        y: Target
        
    Returns:
        bool: True se o modelo passar nas verificações
    """
    try:
        # Verificar se o modelo existe
        if model is None:
            logger.error("Modelo não foi inicializado")
            return False
            
        # Verificar dimensões dos dados
        logger.info(f"Dimensões dos dados de treino - X: {X.shape}, y: {y.shape}")
        
        # Verificar se há features com variância zero
        zero_var = X.var() == 0
        if zero_var.any():
            logger.warning("Features com variância zero encontradas:")
            for col in X.columns[zero_var]:
                logger.warning(f"Feature {col} tem variância zero")
                
        # Verificar correlações muito altas entre features
        corr_matrix = X.corr().abs()
        high_corr = np.where(np.triu(corr_matrix, 1) > 0.95)
        if len(high_corr[0]) > 0:
            logger.warning("Features altamente correlacionadas encontradas:")
            for i, j in zip(*high_corr):
                logger.warning(f"{X.columns[i]} e {X.columns[j]}: {corr_matrix.iloc[i, j]:.3f}")
                
        return True
        
    except Exception as e:
        logger.error(f"Erro na verificação do modelo: {str(e)}")
        logger.error(traceback.format_exc())
        return False

# Criar instância global do monitor de performance
monitor = PerformanceMonitor()

# Função para iniciar o monitoramento
def start_monitoring():
    """Inicia o monitoramento da aplicação."""
    logger.info("Iniciando monitoramento do Data Manager Pro")
    monitor.log_performance()
    
# Função para finalizar o monitoramento
def stop_monitoring():
    """Finaliza o monitoramento e registra estatísticas finais."""
    logger.info("Finalizando monitoramento do Data Manager Pro")
    monitor.log_performance()
