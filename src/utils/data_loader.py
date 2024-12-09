import pandas as pd
import numpy as np
from typing import Optional, Dict, Any
import json
import os
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import gspread
import openpyxl
import pyarrow.parquet as pq
from .logger import get_logger
from .exceptions import DataLoadError

logger = get_logger(__name__)

class DataLoader:
    """Classe para carregar dados de diferentes fontes."""
    
    def __init__(self, credentials_path: Optional[str] = None):
        """
        Inicializa o DataLoader.
        
        Args:
            credentials_path: Caminho para o arquivo de credenciais do Google.
                            Se None, tentará usar 'config/google_credentials.json'
        """
        if credentials_path is None:
            self.credentials_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'config',
                'google_credentials.json'
            )
        else:
            self.credentials_path = credentials_path
            
        self.gspread_client = None
        self.sheets_service = None
        
    def _init_google_services(self):
        """Inicializa serviços do Google se as credenciais estiverem disponíveis."""
        try:
            if not os.path.exists(self.credentials_path):
                raise DataLoadError(
                    f"Arquivo de credenciais não encontrado em: {self.credentials_path}"
                )
                
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=[
                    'https://www.googleapis.com/auth/spreadsheets.readonly',
                    'https://www.googleapis.com/auth/drive.readonly'
                ]
            )
            
            # Inicializa os clientes apenas se ainda não foram inicializados
            if self.gspread_client is None:
                self.gspread_client = gspread.authorize(credentials)
            if self.sheets_service is None:
                self.sheets_service = build('sheets', 'v4', credentials=credentials)
                
            logger.info("Serviços Google inicializados com sucesso")
            
        except Exception as e:
            error_msg = f"Erro ao inicializar serviços Google: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise DataLoadError(error_msg)
            
    def load_file(self, file_path: str) -> pd.DataFrame:
        """
        Carrega dados de diferentes tipos de arquivo.
        
        Args:
            file_path: Caminho do arquivo ou URL do Google Sheets
            
        Returns:
            pd.DataFrame: DataFrame com os dados carregados
        """
        try:
            # Verificar se é URL do Google Sheets
            if file_path.startswith(('https://docs.google.com/spreadsheets', 'https://drive.google.com')):
                return self.load_google_sheets(file_path)
                
            # Verificar extensão do arquivo
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext == '.csv':
                # Tentar diferentes encodings
                encodings = ['utf-8', 'latin1', 'iso-8859-1']
                for encoding in encodings:
                    try:
                        return pd.read_csv(file_path, encoding=encoding)
                    except UnicodeDecodeError:
                        continue
                raise DataLoadError(f"Não foi possível ler o arquivo CSV com os encodings: {encodings}")
                
            elif ext in ['.xlsx', '.xls']:
                return pd.read_excel(file_path, engine='openpyxl')
                
            elif ext == '.parquet':
                return pd.read_parquet(file_path)
                
            elif ext == '.json':
                return pd.read_json(file_path)
                
            elif ext == '.feather':
                return pd.read_feather(file_path)
                
            elif ext == '.pickle' or ext == '.pkl':
                return pd.read_pickle(file_path)
                
            else:
                raise DataLoadError(f"Formato de arquivo não suportado: {ext}")
                
        except Exception as e:
            logger.error(f"Erro ao carregar arquivo: {str(e)}", exc_info=True)
            raise DataLoadError(f"Erro ao carregar arquivo: {str(e)}")
            
    def load_google_sheets(self, url: str) -> pd.DataFrame:
        """
        Carrega dados de uma planilha do Google Sheets.
        
        Args:
            url: URL da planilha do Google Sheets
            
        Returns:
            pd.DataFrame: DataFrame com os dados carregados
        """
        try:
            if not self.gspread_client:
                self._init_google_services()
                
            # Extrair ID da planilha da URL
            if '/d/' in url:
                spreadsheet_id = url.split('/d/')[1].split('/')[0]
            else:
                raise DataLoadError("URL do Google Sheets inválida")
                
            # Abrir planilha
            worksheet = self.gspread_client.open_by_key(spreadsheet_id).sheet1
            
            # Obter dados
            data = worksheet.get_all_values()
            if not data:
                raise DataLoadError("Planilha vazia")
                
            # Converter para DataFrame
            df = pd.DataFrame(data[1:], columns=data[0])
            
            # Converter tipos de dados automaticamente
            for col in df.columns:
                # Tentar converter para numérico
                if df[col].dtype == object:
                    try:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                    except:
                        pass
                        
                # Tentar converter para datetime
                if df[col].dtype == object:
                    try:
                        df[col] = pd.to_datetime(df[col], errors='coerce')
                    except:
                        pass
                        
            logger.info(f"Dados carregados com sucesso do Google Sheets: {len(df)} linhas")
            return df
            
        except Exception as e:
            logger.error(f"Erro ao carregar Google Sheets: {str(e)}", exc_info=True)
            raise DataLoadError(f"Erro ao carregar Google Sheets: {str(e)}")
            
    def get_supported_formats(self) -> Dict[str, str]:
        """Retorna os formatos de arquivo suportados."""
        return {
            "CSV": "*.csv",
            "Excel": "*.xlsx;*.xls",
            "Parquet": "*.parquet",
            "JSON": "*.json",
            "Feather": "*.feather",
            "Pickle": "*.pkl;*.pickle",
            "Google Sheets": "URL"
        }
