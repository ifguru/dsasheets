"""
Módulo principal da interface gráfica do Data Manager Pro.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from typing import Optional, Dict, Any
from config.settings import WINDOW_SIZE, WINDOW_TITLE
from src.analysis.data_analyzer import DataAnalyzer
from src.ml.model_trainer import ModelTrainer

class DataManagerApp:
    """
    Classe principal da interface gráfica do Data Manager Pro.
    """
    
    def __init__(self):
        """Inicializa a aplicação."""
        self.root = tk.Tk()
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)
        
        self.df: Optional[pd.DataFrame] = None
        self.analyzer: Optional[DataAnalyzer] = None
        self.model_trainer: Optional[ModelTrainer] = None
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Configura os elementos da interface."""
        # Menu principal
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        
        # Menu Arquivo
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Abrir CSV", command=self._load_csv)
        file_menu.add_command(label="Abrir Google Sheets", command=self._load_gsheets)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.root.quit)
        
        # Menu Análise
        analysis_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Análise", menu=analysis_menu)
        analysis_menu.add_command(label="Informações Básicas", command=self._show_basic_info)
        analysis_menu.add_command(label="Resumo Estatístico", command=self._show_statistical_summary)
        analysis_menu.add_command(label="Matriz de Correlação", command=self._show_correlation_matrix)
        
        # Menu Machine Learning
        ml_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Machine Learning", menu=ml_menu)
        ml_menu.add_command(label="Treinar Modelo", command=self._train_model)
        ml_menu.add_command(label="Avaliar Modelo", command=self._evaluate_model)
        ml_menu.add_command(label="Importância das Features", command=self._show_feature_importance)
        
        # Área principal
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Tabela de dados
        self.tree = ttk.Treeview(self.main_frame)
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbars
        vsb = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.main_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.grid(row=0, column=1, sticky=(tk.N, tk.S))
        hsb.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        self.status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.status_var.set("Pronto")
        
    def _load_csv(self):
        """Carrega dados de um arquivo CSV."""
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            try:
                self.df = pd.read_csv(file_path)
                self._update_table()
                self.analyzer = DataAnalyzer(self.df)
                self.model_trainer = ModelTrainer(self.df)
                self.status_var.set(f"Dados carregados: {len(self.df)} linhas")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar arquivo: {str(e)}")
                
    def _load_gsheets(self):
        """Carrega dados do Google Sheets."""
        # Implementar integração com Google Sheets
        pass
        
    def _update_table(self):
        """Atualiza a tabela com os dados do DataFrame."""
        if self.df is None:
            return
            
        # Limpa a tabela
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Configura as colunas
        self.tree["columns"] = list(self.df.columns)
        self.tree["show"] = "headings"
        
        for column in self.df.columns:
            self.tree.heading(column, text=column)
            self.tree.column(column, width=100)
            
        # Adiciona os dados
        for idx, row in self.df.iterrows():
            self.tree.insert("", "end", values=list(row))
            
    def _show_basic_info(self):
        """Mostra informações básicas sobre os dados."""
        if self.analyzer:
            info = self.analyzer.get_basic_info()
            self._show_info_window("Informações Básicas", info)
            
    def _show_statistical_summary(self):
        """Mostra o resumo estatístico dos dados."""
        if self.analyzer:
            summary = self.analyzer.get_statistical_summary()
            self._show_info_window("Resumo Estatístico", summary.to_string())
            
    def _show_correlation_matrix(self):
        """Mostra a matriz de correlação."""
        if self.analyzer:
            corr = self.analyzer.get_correlation_matrix()
            self._show_info_window("Matriz de Correlação", corr.to_string())
            
    def _train_model(self):
        """Treina um modelo de Machine Learning."""
        if self.model_trainer and self.df is not None:
            # Implementar diálogo para seleção de parâmetros
            pass
            
    def _evaluate_model(self):
        """Avalia o modelo treinado."""
        if self.model_trainer and hasattr(self.model_trainer, 'model'):
            # Implementar visualização de métricas
            pass
            
    def _show_feature_importance(self):
        """Mostra a importância das features."""
        if self.model_trainer:
            importance = self.model_trainer.get_feature_importance()
            if importance is not None:
                self._show_info_window("Importância das Features", importance.to_string())
            
    def _show_info_window(self, title: str, info: Any):
        """
        Mostra uma janela com informações.
        
        Args:
            title (str): Título da janela
            info (Any): Informações a serem mostradas
        """
        window = tk.Toplevel(self.root)
        window.title(title)
        
        text = tk.Text(window, wrap=tk.NONE)
        text.insert(tk.END, str(info))
        text.pack(expand=True, fill=tk.BOTH)
        
        # Scrollbars
        vsb = ttk.Scrollbar(window, orient="vertical", command=text.yview)
        hsb = ttk.Scrollbar(window, orient="horizontal", command=text.xview)
        text.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
    def run(self):
        """Inicia a aplicação."""
        self.root.mainloop()
