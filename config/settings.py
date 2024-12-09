"""
Configurações globais do aplicativo.
"""

import os
from pathlib import Path

# Diretório raiz do projeto
ROOT_DIR = Path(__file__).parent.parent

# Configurações do Google Sheets
GOOGLE_CREDENTIALS_FILE = os.path.join(ROOT_DIR, 'panilhatest-4ef7602af4b3.json')
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
    'https://spreadsheets.google.com/feeds'
]

# Configurações da Interface
WINDOW_SIZE = "800x600"
WINDOW_TITLE = "Data Manager Pro"
DEFAULT_PADDING = "10"
TABLE_ROW_HEIGHT = 25
MAX_TABLE_ROWS = 10000

# Configurações de Logging
LOG_DIR = os.path.join(ROOT_DIR, 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'app.log')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s'
LOG_FILE_MAX_BYTES = 10 * 1024 * 1024  # 10MB
LOG_FILE_BACKUP_COUNT = 5
LOG_LEVEL = 'INFO'

# Configurações de Análise
MAX_CORRELATION_DISPLAY = 20
DECIMAL_PLACES = 2
DEFAULT_PLOT_SIZE = (10, 6)
DEFAULT_PLOT_STYLE = 'seaborn'

# Configurações de Validação de Dados
MAX_CATEGORICAL_UNIQUE_PCT = 0.5  # Máximo de valores únicos para considerar uma coluna categórica
MAX_CORRELATION_THRESHOLD = 0.95  # Limite para considerar correlação alta
MAX_MISSING_PCT = 0.2  # Máximo de valores ausentes permitidos
OUTLIER_STD_THRESHOLD = 3  # Número de desvios padrão para considerar outlier

# Configurações de Machine Learning
TEST_SIZE = 0.2
TEST_SIZE_DEFAULT = 0.2
RANDOM_STATE = 42
N_JOBS = -1  # Usar todos os cores disponíveis
DEFAULT_MODEL_PARAMS = {
    'n_estimators': 100,
    'max_depth': 6,
    'learning_rate': 0.1
}
