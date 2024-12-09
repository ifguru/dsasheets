"""
Módulo centralizado de logging para o Data Manager Pro.
Implementa um sistema de logging robusto com rotação de arquivos e diferentes níveis de log.
"""

import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
import sys
import traceback

class DataManagerLogger:
    """
    Gerenciador centralizado de logs do Data Manager Pro.
    Implementa um sistema de logging com:
    - Rotação de arquivos
    - Diferentes níveis de log
    - Formatação consistente
    - Captura de exceções não tratadas
    """
    
    _instance: Optional['DataManagerLogger'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
        
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self._setup_logging()
            
    def _setup_logging(self):
        """Configura o sistema de logging."""
        # Criar diretório de logs se não existir
        log_dir = Path(__file__).parent.parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        # Nome do arquivo de log com timestamp
        log_file = log_dir / f'app_debug_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        
        # Configurar formatador
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s'
        )
        
        # Remover handlers existentes para evitar duplicação
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Handler para arquivo com rotação
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # Configurar logger raiz
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        # Configurar captura de exceções não tratadas
        sys.excepthook = self._handle_uncaught_exception
        
    def _handle_uncaught_exception(self, exc_type, exc_value, exc_traceback):
        """Handler para exceções não tratadas."""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
            
        self.logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
        
    def get_logger(self) -> logging.Logger:
        """Retorna a instância do logger."""
        return logging.getLogger('DataManagerPro')
        
class LoggerAdapter(logging.LoggerAdapter):
    """
    Adapter para adicionar contexto extra aos logs.
    """
    def process(self, msg, kwargs):
        # Adicionar informações de memória e CPU quando relevante
        from src.utils.debug_monitor import monitor
        if kwargs.get('extra', {}).get('performance', False):
            mem_usage = monitor.get_memory_usage()
            cpu_usage = monitor.get_cpu_usage()
            msg = f"{msg} [Memory: {mem_usage:.1f}MB, CPU: {cpu_usage:.1f}%]"
        return msg, kwargs

def get_logger(name: str = None) -> LoggerAdapter:
    """
    Obtém um logger configurado com o adapter.
    
    Args:
        name: Nome do logger (opcional)
        
    Returns:
        LoggerAdapter: Logger configurado
    """
    logger = logging.getLogger('DataManagerPro')
    if name:
        logger = logger.getChild(name)
    return LoggerAdapter(logger, {})
