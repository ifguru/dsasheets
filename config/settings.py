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
WINDOW_SIZE = "1200x800"
WINDOW_TITLE = "Data Manager Pro"
DEFAULT_PADDING = "10"
TABLE_ROW_HEIGHT = 25
MAX_TABLE_ROWS = 10000

# Configurações de Análise
MAX_CORRELATION_DISPLAY = 20
DECIMAL_PLACES = 2
DEFAULT_PLOT_SIZE = (10, 6)
DEFAULT_PLOT_STYLE = 'seaborn'

# Configurações de Machine Learning
TEST_SIZE = 0.2
RANDOM_STATE = 42
DEFAULT_MODEL_PARAMS = {
    'n_estimators': 100,
    'max_depth': 6,
    'learning_rate': 0.1
}

# Configurações de Log
LOG_FILE = os.path.join(ROOT_DIR, 'logs', 'app.log')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = 'INFO'
