"""
Módulo de validação de dados para o Data Manager Pro.
"""

import pandas as pd
import numpy as np
from typing import Tuple, List, Dict, Any
from .exceptions import DataValidationError
from .logger import get_logger
import os
import datetime

logger = get_logger(__name__)

class DataVersion:
    def __init__(self, df: pd.DataFrame, description: str, timestamp: datetime = None):
        self.df = df.copy()
        self.description = description
        self.timestamp = timestamp or datetime.datetime.now()
        self.changes = []
        
    def add_change(self, column: str, operation: str, details: dict):
        self.changes.append({
            'column': column,
            'operation': operation,
            'details': details,
            'timestamp': datetime.datetime.now()
        })
        
    def get_change_summary(self) -> str:
        summary = [f"Alterações realizadas em {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}:"]
        for change in self.changes:
            summary.append(f"- Coluna '{change['column']}': {change['operation']}")
            for key, value in change['details'].items():
                summary.append(f"  • {key}: {value}")
        return "\n".join(summary)

class ValidationResult:
    def __init__(self):
        self.passed = True
        self.messages = []
        self.details = {}
        
    def add_error(self, message: str, details: dict = None):
        self.passed = False
        self.messages.append({"type": "error", "message": message})
        if details:
            self.details.update(details)
            
    def add_warning(self, message: str, details: dict = None):
        self.messages.append({"type": "warning", "message": message})
        if details:
            self.details.update(details)
            
    def add_info(self, message: str, details: dict = None):
        self.messages.append({"type": "info", "message": message})
        if details:
            self.details.update(details)
            
    def merge(self, other: 'ValidationResult'):
        self.passed = self.passed and other.passed
        self.messages.extend(other.messages)
        self.details.update(other.details)
        
    def get_formatted_messages(self) -> List[str]:
        formatted = []
        for msg in self.messages:
            prefix = {
                "error": "❌ Erro",
                "warning": "⚠️ Aviso",
                "info": "ℹ️ Info"
            }.get(msg["type"], "")
            formatted.append(f"{prefix}: {msg['message']}")
        return formatted

class DataValidator:
    """
    Classe para validação de dados.
    Implementa verificações de qualidade e sanidade dos dados.
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        Inicializa o validador.
        
        Args:
            df: DataFrame a ser validado
        """
        self.df = df.copy()
        self.versions = []
        self._save_version("Versão original")
        
    def _save_version(self, description: str) -> None:
        self.versions.append(DataVersion(self.df, description))
        
    def get_versions(self) -> List[DataVersion]:
        return self.versions
        
    def export_data(self, filepath: str, version_idx: int = -1, format: str = 'csv') -> None:
        """
        Exporta os dados para o formato especificado.
        
        Args:
            filepath: Caminho para salvar o arquivo
            version_idx: Índice da versão a ser exportada (-1 para última versão)
            format: Formato de exportação ('csv', 'excel', 'parquet', 'pickle')
        """
        version = self.versions[version_idx]
        df = version.df
        
        # Criar diretório se não existir
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Adicionar timestamp ao nome do arquivo
        filename, ext = os.path.splitext(filepath)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        new_filepath = f"{filename}_{timestamp}{ext}"
        
        try:
            if format == 'csv':
                df.to_csv(new_filepath, index=False, encoding='utf-8-sig')
            elif format == 'excel':
                df.to_excel(new_filepath, index=False, engine='openpyxl')
            elif format == 'parquet':
                df.to_parquet(new_filepath, index=False)
            elif format == 'pickle':
                df.to_pickle(new_filepath)
            else:
                raise ValueError(f"Formato não suportado: {format}")
                
            # Gerar relatório de alterações
            report_path = f"{filename}_changes_{timestamp}.txt"
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(version.get_change_summary())
                
            logger.info(f"Dados exportados com sucesso para {new_filepath}")
            logger.info(f"Relatório de alterações salvo em {report_path}")
            
        except Exception as e:
            logger.error(f"Erro ao exportar dados: {str(e)}", exc_info=True)
            raise DataValidationError(f"Erro ao exportar dados: {str(e)}")

    def validate_all(self) -> ValidationResult:
        """
        Executa todas as validações disponíveis.
        
        Returns:
            ValidationResult: Resultado completo das validações
        """
        logger.info("Iniciando validação completa dos dados")
        result = ValidationResult()
        
        try:
            # 1. Validação básica
            result.merge(self._validate_basic_structure())
            
            # 2. Validação de tipos de dados
            result.merge(self._validate_data_types())
            
            # 3. Validação de valores ausentes
            result.merge(self._validate_missing_values())
            
            # 4. Validação de outliers
            result.merge(self._validate_outliers())
            
            # 5. Validação de cardinalidade
            result.merge(self._validate_cardinality())
            
            logger.info("Validação completa finalizada")
            return result
            
        except Exception as e:
            logger.error(f"Erro durante validação: {str(e)}", exc_info=True)
            result.add_error(f"Erro durante validação: {str(e)}")
            return result
            
    def _validate_basic_structure(self) -> ValidationResult:
        """Valida a estrutura básica do DataFrame."""
        result = ValidationResult()
        
        try:
            # Verificar se há dados
            if self.df.empty:
                result.add_error("DataFrame está vazio")
                return result
                
            # Verificar número de linhas
            if len(self.df) < 1:
                result.add_error("DataFrame não contém registros")
            else:
                result.add_info(f"DataFrame contém {len(self.df)} registros")
                
            # Verificar número de colunas
            if len(self.df.columns) < 1:
                result.add_error("DataFrame não contém colunas")
            else:
                result.add_info(f"DataFrame contém {len(self.df.columns)} colunas")
                
            # Verificar nomes de colunas duplicados
            duplicated_cols = self.df.columns[self.df.columns.duplicated()].tolist()
            if duplicated_cols:
                result.add_error(f"Colunas duplicadas encontradas: {duplicated_cols}")
                
            return result
            
        except Exception as e:
            logger.error(f"Erro na validação básica: {str(e)}", exc_info=True)
            result.add_error(f"Erro na validação básica: {str(e)}")
            return result
            
    def _validate_data_types(self) -> ValidationResult:
        """Valida os tipos de dados das colunas."""
        result = ValidationResult()
        
        try:
            for col in self.df.columns:
                dtype = self.df[col].dtype
                unique_count = self.df[col].nunique()
                total_count = len(self.df)
                
                # Verificar tipos numéricos
                if pd.api.types.is_numeric_dtype(dtype):
                    if unique_count / total_count < 0.01:  # Menos de 1% de valores únicos
                        result.add_warning(
                            f"Coluna '{col}' pode ser categorical (baixa cardinalidade)",
                            {"coluna": col, "valores_unicos": unique_count, "total": total_count}
                        )
                
                # Verificar tipos object (string)
                elif pd.api.types.is_object_dtype(dtype):
                    numeric_ratio = pd.to_numeric(self.df[col], errors='coerce').notna().mean()
                    if numeric_ratio > 0.8:  # Mais de 80% dos valores podem ser convertidos para número
                        result.add_warning(
                            f"Coluna '{col}' pode ser numérica",
                            {"coluna": col, "ratio_numerico": numeric_ratio}
                        )
                
                # Verificar tipos datetime
                elif pd.api.types.is_datetime64_any_dtype(dtype):
                    invalid_dates = self.df[col].isna().sum()
                    if invalid_dates > 0:
                        result.add_warning(
                            f"Coluna '{col}' contém {invalid_dates} datas inválidas",
                            {"coluna": col, "datas_invalidas": invalid_dates}
                        )
                
            return result
            
        except Exception as e:
            logger.error(f"Erro na validação de tipos: {str(e)}", exc_info=True)
            result.add_error(f"Erro na validação de tipos: {str(e)}")
            return result
            
    def _validate_missing_values(self) -> ValidationResult:
        """Valida valores ausentes no DataFrame."""
        result = ValidationResult()
        
        try:
            missing_info = self.df.isna().sum()
            missing_cols = missing_info[missing_info > 0]
            
            if len(missing_cols) > 0:
                for col, count in missing_cols.items():
                    percent = (count / len(self.df)) * 100
                    if percent > 20:
                        result.add_error(
                            f"Coluna '{col}' tem {percent:.1f}% de valores ausentes",
                            {"coluna": col, "missing_count": count, "missing_percent": percent}
                        )
                    else:
                        result.add_warning(
                            f"Coluna '{col}' tem {percent:.1f}% de valores ausentes",
                            {"coluna": col, "missing_count": count, "missing_percent": percent}
                        )
            else:
                result.add_info("Nenhum valor ausente encontrado")
                
            return result
            
        except Exception as e:
            logger.error(f"Erro na validação de valores ausentes: {str(e)}", exc_info=True)
            result.add_error(f"Erro na validação de valores ausentes: {str(e)}")
            return result
            
    def _validate_outliers(self) -> ValidationResult:
        """Valida outliers em colunas numéricas."""
        result = ValidationResult()
        
        try:
            numeric_cols = self.df.select_dtypes(include=['int64', 'float64']).columns
            
            for col in numeric_cols:
                Q1 = self.df[col].quantile(0.25)
                Q3 = self.df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = self.df[(self.df[col] < lower_bound) | (self.df[col] > upper_bound)][col]
                outliers_count = len(outliers)
                
                if outliers_count > 0:
                    percent = (outliers_count / len(self.df)) * 100
                    if percent > 10:
                        result.add_error(
                            f"Coluna '{col}' tem {percent:.1f}% de outliers",
                            {
                                "coluna": col,
                                "outliers_count": outliers_count,
                                "outliers_percent": percent,
                                "limite_inferior": lower_bound,
                                "limite_superior": upper_bound
                            }
                        )
                    else:
                        result.add_warning(
                            f"Coluna '{col}' tem {percent:.1f}% de outliers",
                            {
                                "coluna": col,
                                "outliers_count": outliers_count,
                                "outliers_percent": percent,
                                "limite_inferior": lower_bound,
                                "limite_superior": upper_bound
                            }
                        )
                        
            return result
            
        except Exception as e:
            logger.error(f"Erro na validação de outliers: {str(e)}", exc_info=True)
            result.add_error(f"Erro na validação de outliers: {str(e)}")
            return result
            
    def _validate_cardinality(self) -> ValidationResult:
        """Valida a cardinalidade das colunas categóricas."""
        result = ValidationResult()
        
        try:
            categorical_cols = self.df.select_dtypes(include=['category', 'object']).columns
            
            for col in categorical_cols:
                unique_count = self.df[col].nunique()
                total_count = len(self.df)
                
                # Alta cardinalidade
                if unique_count / total_count > 0.5:
                    result.add_warning(
                        f"Coluna '{col}' tem alta cardinalidade ({unique_count} valores únicos)",
                        {"coluna": col, "valores_unicos": unique_count, "total": total_count}
                    )
                
                # Valores raros
                value_counts = self.df[col].value_counts()
                rare_values = value_counts[value_counts < len(self.df) * 0.01]
                if len(rare_values) > 0:
                    result.add_warning(
                        f"Coluna '{col}' tem {len(rare_values)} valores raros (<1% dos dados)",
                        {"coluna": col, "valores_raros": len(rare_values)}
                    )
                    
            return result
            
        except Exception as e:
            logger.error(f"Erro na validação de cardinalidade: {str(e)}", exc_info=True)
            result.add_error(f"Erro na validação de cardinalidade: {str(e)}")
            return result

    def auto_fix_problems(self) -> pd.DataFrame:
        """
        Tenta corrigir automaticamente os problemas encontrados nos dados.
        
        Returns:
            pd.DataFrame: DataFrame com as correções aplicadas
        """
        logger.info("Iniciando correção automática dos dados")
        df_fixed = self.df.copy()
        version = DataVersion(df_fixed, "Correção automática")
        
        try:
            # 1. Converter colunas para categorical
            for col in df_fixed.columns:
                if pd.api.types.is_object_dtype(df_fixed[col]):
                    unique_count = df_fixed[col].nunique()
                    if unique_count / len(df_fixed) < 0.5:  # Mais de 50% de valores repetidos
                        logger.info(f"Convertendo coluna {col} para categorical")
                        df_fixed[col] = df_fixed[col].astype('category')
                        version.add_change(col, "Conversão para categoria", {
                            "valores_únicos": unique_count,
                            "total_linhas": len(df_fixed)
                        })
            
            # 2. Tratar outliers em colunas numéricas
            numeric_cols = df_fixed.select_dtypes(include=['int64', 'float64']).columns
            for col in numeric_cols:
                Q1 = df_fixed[col].quantile(0.25)
                Q3 = df_fixed[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                mask = (df_fixed[col] < lower_bound) | (df_fixed[col] > upper_bound)
                if mask.any():
                    outliers_count = mask.sum()
                    median = df_fixed[col].median()
                    df_fixed.loc[mask, col] = median
                    logger.info(f"Tratando {outliers_count} outliers na coluna {col}")
                    version.add_change(col, "Tratamento de outliers", {
                        "outliers_encontrados": outliers_count,
                        "limite_inferior": lower_bound,
                        "limite_superior": upper_bound,
                        "valor_substituição": median
                    })
            
            # 3. Tratar valores raros em colunas categóricas
            categorical_cols = df_fixed.select_dtypes(include=['category', 'object']).columns
            for col in categorical_cols:
                value_counts = df_fixed[col].value_counts()
                rare_values = value_counts[value_counts < len(df_fixed) * 0.01].index
                if len(rare_values) > 0:
                    df_fixed[col] = df_fixed[col].replace(rare_values, 'Outros')
                    logger.info(f"Agrupando {len(rare_values)} valores raros na coluna {col}")
                    version.add_change(col, "Agrupamento de valores raros", {
                        "valores_agrupados": len(rare_values),
                        "novo_valor": "Outros"
                    })
            
            # 4. Tratar valores ausentes
            for col in df_fixed.columns:
                missing_count = df_fixed[col].isna().sum()
                if missing_count > 0:
                    if pd.api.types.is_numeric_dtype(df_fixed[col]):
                        median = df_fixed[col].median()
                        df_fixed[col] = df_fixed[col].fillna(median)
                        logger.info(f"Preenchendo {missing_count} valores ausentes na coluna {col} com mediana")
                        version.add_change(col, "Preenchimento de valores ausentes", {
                            "valores_preenchidos": missing_count,
                            "método": "mediana",
                            "valor": median
                        })
                    else:
                        mode = df_fixed[col].mode()[0]
                        df_fixed[col] = df_fixed[col].fillna(mode)
                        logger.info(f"Preenchendo {missing_count} valores ausentes na coluna {col} com moda")
                        version.add_change(col, "Preenchimento de valores ausentes", {
                            "valores_preenchidos": missing_count,
                            "método": "moda",
                            "valor": mode
                        })
            
            self.df = df_fixed
            self.versions.append(version)
            logger.info("Correção automática concluída com sucesso")
            return df_fixed
            
        except Exception as e:
            logger.error(f"Erro durante a correção automática: {str(e)}", exc_info=True)
            raise DataValidationError(f"Erro durante a correção automática: {str(e)}")
            
    def get_data_quality_report(self) -> Dict[str, Any]:
        """
        Gera um relatório completo sobre a qualidade dos dados.
        
        Returns:
            Dict[str, Any]: Relatório de qualidade
        """
        try:
            logger.info("Gerando relatório de qualidade dos dados")
            
            report = {
                'basic_info': {
                    'rows': len(self.df),
                    'columns': len(self.df.columns),
                    'memory_usage': self.df.memory_usage(deep=True).sum() / 1024 / 1024,  # MB
                    'dtypes': self.df.dtypes.to_dict()
                },
                'missing_values': self.validate_missing_values()[1],
                'numerical_stats': {},
                'categorical_stats': {}
            }
            
            # Estatísticas para colunas numéricas
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                report['numerical_stats'][col] = {
                    'mean': self.df[col].mean(),
                    'std': self.df[col].std(),
                    'min': self.df[col].min(),
                    'max': self.df[col].max(),
                    'skewness': self.df[col].skew()
                }
                
            # Estatísticas para colunas categóricas
            categorical_cols = self.df.select_dtypes(include=['object', 'category']).columns
            for col in categorical_cols:
                report['categorical_stats'][col] = {
                    'unique_values': self.df[col].nunique(),
                    'most_common': self.df[col].value_counts().head().to_dict()
                }
                
            logger.info("Relatório de qualidade gerado com sucesso")
            return report
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório de qualidade: {str(e)}")
            raise DataValidationError(f"Erro ao gerar relatório de qualidade: {str(e)}")
            
def validate_model_data(X: pd.DataFrame, y: pd.Series) -> Tuple[bool, List[str]]:
    """
    Valida dados para treinamento de modelo.
    
    Args:
        X: Features
        y: Target
        
    Returns:
        Tuple[bool, List[str]]: (válido, lista de problemas)
    """
    try:
        logger.info("Validando dados para treinamento do modelo")
        problems = []
        
        # Verificar dimensões
        if len(X) != len(y):
            problems.append("Número de amostras diferente entre features e target")
            
        # Verificar valores ausentes
        if X.isnull().any().any():
            problems.append("Features contêm valores ausentes")
            
        if y.isnull().any():
            problems.append("Target contém valores ausentes")
            
        # Verificar variância zero
        zero_var_cols = X.columns[X.var() == 0]
        if not zero_var_cols.empty:
            problems.append(f"Features com variância zero: {list(zero_var_cols)}")
            
        # Verificar correlações muito altas
        corr_matrix = X.corr().abs()
        high_corr = np.where(np.triu(corr_matrix, 1) > 0.95)
        if len(high_corr[0]) > 0:
            problems.append("Existem features altamente correlacionadas")
            
        valid = len(problems) == 0
        if valid:
            logger.info("Dados validados para treinamento")
        else:
            logger.warning(f"Problemas encontrados nos dados de treinamento: {problems}")
            
        return valid, problems
        
    except Exception as e:
        logger.error(f"Erro ao validar dados de treinamento: {str(e)}")
        raise DataValidationError(f"Erro ao validar dados de treinamento: {str(e)}")
