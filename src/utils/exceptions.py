"""
Exceções personalizadas para o Data Manager Pro.
"""

class DataManagerError(Exception):
    """Classe base para exceções do Data Manager Pro."""
    pass

class DataLoadError(DataManagerError):
    """Erro ao carregar dados."""
    pass

class DataValidationError(DataManagerError):
    """Erro na validação dos dados."""
    pass

class ModelError(DataManagerError):
    """Erro relacionado ao modelo de ML."""
    pass

class ConfigurationError(DataManagerError):
    """Erro de configuração."""
    pass

class UIError(DataManagerError):
    """Erro na interface do usuário."""
    pass

class GoogleSheetsError(DataManagerError):
    """Erro na integração com Google Sheets."""
    pass
