"""
Módulo principal da interface gráfica do Data Manager Pro.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from typing import Optional, Dict, Any
import os
from config.settings import WINDOW_SIZE, WINDOW_TITLE
from src.analysis.data_analyzer import DataAnalyzer
from src.ml.model_trainer import ModelTrainer
from src.utils.logger import get_logger
from src.utils.validation import DataValidator, validate_model_data
from src.utils.exceptions import (
    DataManagerError,
    DataLoadError,
    DataValidationError,
    ModelError,
    UIError
)
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ..utils.data_loader import DataLoader

logger = get_logger(__name__)

class DataManagerApp:
    """
    Classe principal da interface gráfica do Data Manager Pro.
    """
    
    def __init__(self, root: tk.Tk):
        """Inicializa a aplicação."""
        try:
            logger.info("Iniciando Data Manager Pro")
            self.root = root
            self.root.title(WINDOW_TITLE)
            self.root.geometry(WINDOW_SIZE)
            
            # Configurar o tema
            self.style = ttk.Style()
            self.style.theme_use('clam')
            
            # Variáveis
            self.df: Optional[pd.DataFrame] = None
            self.analyzer: Optional[DataAnalyzer] = None
            self.model_trainer: Optional[ModelTrainer] = None
            self.validator: Optional[DataValidator] = None
            self.current_file = None
            self.data_loader = DataLoader()
            
            try:
                # Tentar carregar credenciais do Google
                credentials_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'google_credentials.json')
                if os.path.exists(credentials_path):
                    self.data_loader = DataLoader(credentials_path)
                    logger.info("Credenciais do Google carregadas com sucesso")
            except Exception as e:
                logger.warning(f"Não foi possível carregar credenciais do Google: {str(e)}")
            
            self._setup_ui()
            logger.info("Interface inicializada com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar aplicação: {str(e)}", exc_info=True)
            raise UIError(f"Erro ao inicializar aplicação: {str(e)}")
            
    def _setup_ui(self):
        """Configura os elementos da interface."""
        try:
            logger.debug("Configurando interface gráfica")
            
            # Menu principal
            self.menu_bar = tk.Menu(self.root)
            self.root.config(menu=self.menu_bar)
            
            # Menu Arquivo
            file_menu = tk.Menu(self.menu_bar, tearoff=0)
            self.menu_bar.add_cascade(label="Arquivo", menu=file_menu)
            file_menu.add_command(label="Carregar Dados", command=self._load_file)
            file_menu.add_separator()
            file_menu.add_command(label="Validar Dados", command=self._validate_data)
            file_menu.add_command(label="Corrigir Dados", command=self._auto_fix_data)
            file_menu.add_separator()
            
            # Submenu Exportar
            export_menu = tk.Menu(file_menu, tearoff=0)
            file_menu.add_cascade(label="Exportar", menu=export_menu)
            export_menu.add_command(label="CSV", command=lambda: self._export_data('csv'))
            export_menu.add_command(label="Excel", command=lambda: self._export_data('excel'))
            export_menu.add_command(label="Parquet", command=lambda: self._export_data('parquet'))
            export_menu.add_command(label="Pickle", command=lambda: self._export_data('pickle'))
            
            file_menu.add_separator()
            file_menu.add_command(label="Sair", command=self.root.quit)
            
            # Menu Visualizar
            view_menu = tk.Menu(self.menu_bar, tearoff=0)
            self.menu_bar.add_cascade(label="Visualizar", menu=view_menu)
            view_menu.add_command(label="Histórico de Alterações", command=self._show_version_history)
            
            # Menu Análise
            analysis_menu = tk.Menu(self.menu_bar, tearoff=0)
            self.menu_bar.add_cascade(label="Análise", menu=analysis_menu)
            analysis_menu.add_command(label="Relatório de Qualidade", command=self._show_quality_report)
            
            # Frame principal
            self.main_frame = ttk.Frame(self.root, padding="10")
            self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            # Configurar expansão do grid
            self.root.columnconfigure(0, weight=1)
            self.root.rowconfigure(0, weight=1)
            self.main_frame.columnconfigure(0, weight=1)
            self.main_frame.rowconfigure(0, weight=1)
            
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
            
            logger.debug("Interface configurada com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao configurar interface: {str(e)}", exc_info=True)
            raise UIError(f"Erro ao configurar interface: {str(e)}")
            
    def _load_file(self):
        """Carrega dados de diferentes formatos."""
        try:
            # Criar janela de seleção
            load_window = tk.Toplevel(self.root)
            load_window.title("Carregar Dados")
            load_window.geometry("500x200")
            
            # Frame para opções
            options_frame = ttk.LabelFrame(load_window, text="Fonte de Dados")
            options_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            
            # Variável para opção selecionada
            source_var = tk.StringVar(value="file")
            
            # Opções de fonte
            ttk.Radiobutton(
                options_frame,
                text="Arquivo Local",
                variable=source_var,
                value="file"
            ).pack(anchor=tk.W, padx=10, pady=5)
            
            ttk.Radiobutton(
                options_frame,
                text="Google Sheets",
                variable=source_var,
                value="sheets"
            ).pack(anchor=tk.W, padx=10, pady=5)
            
            # Frame para URL do Google Sheets
            sheets_frame = ttk.Frame(options_frame)
            sheets_frame.pack(fill=tk.X, padx=10, pady=5)
            
            ttk.Label(sheets_frame, text="URL:").pack(side=tk.LEFT)
            url_entry = ttk.Entry(sheets_frame, width=50)
            url_entry.pack(side=tk.LEFT, padx=5)
            
            def load_data():
                try:
                    if source_var.get() == "file":
                        # Obter formatos suportados
                        formats = self.data_loader.get_supported_formats()
                        filetypes = [(name, pattern) for name, pattern in formats.items()]
                        filetypes.append(("Todos os arquivos", "*.*"))
                        
                        file_path = filedialog.askopenfilename(
                            title="Selecione o arquivo",
                            filetypes=filetypes
                        )
                        
                        if not file_path:
                            return
                            
                    else:  # Google Sheets
                        url = url_entry.get().strip()
                        if not url:
                            messagebox.showwarning("Aviso", "Por favor, insira a URL do Google Sheets")
                            return
                        file_path = url
                    
                    # Carregar dados
                    logger.info(f"Carregando dados de: {file_path}")
                    self.df = self.data_loader.load_file(file_path)
                    self.current_file = file_path
                    
                    # Validar dados
                    self.validator = DataValidator(self.df)
                    validation_result = self.validator.validate_all()
                    
                    # Fechar janela de seleção
                    load_window.destroy()
                    
                    # Mostrar resultados
                    self._show_validation_results(validation_result)
                    self._update_table()
                    
                    # Mostrar mensagem de sucesso
                    messagebox.showinfo(
                        "Sucesso",
                        f"Dados carregados com sucesso!\n" +
                        f"Linhas: {len(self.df)}\n" +
                        f"Colunas: {len(self.df.columns)}"
                    )
                    
                except Exception as e:
                    logger.error(f"Erro ao carregar dados: {str(e)}", exc_info=True)
                    messagebox.showerror("Erro", f"Erro ao carregar dados: {str(e)}")
                    
            # Botões
            button_frame = ttk.Frame(load_window)
            button_frame.pack(fill=tk.X, padx=10, pady=5)
            
            ttk.Button(
                button_frame,
                text="Carregar",
                command=load_data
            ).pack(side=tk.LEFT, padx=5)
            
            ttk.Button(
                button_frame,
                text="Cancelar",
                command=load_window.destroy
            ).pack(side=tk.RIGHT, padx=5)
            
        except Exception as e:
            logger.error(f"Erro ao abrir janela de carregamento: {str(e)}", exc_info=True)
            messagebox.showerror("Erro", f"Erro ao abrir janela de carregamento: {str(e)}")
            
    def _validate_data(self):
        """Valida os dados carregados."""
        try:
            if self.df is None:
                messagebox.showwarning("Aviso", "Por favor, carregue os dados primeiro.")
                return
                
            if self.validator is None:
                self.validator = DataValidator(self.df)
            
            logger.info("Iniciando validação dos dados")
            validation_result = self.validator.validate_all()
            self._show_validation_results(validation_result)
            
            # Se não houver erros, apenas avisos
            if validation_result.passed:
                if any(msg["type"] == "warning" for msg in validation_result.messages):
                    if messagebox.askyesno(
                        "Avisos Encontrados",
                        "Foram encontrados alguns avisos nos dados.\n" +
                        "Deseja aplicar correções automáticas?"
                    ):
                        self._auto_fix_data()
                else:
                    messagebox.showinfo(
                        "Sucesso",
                        "Dados validados com sucesso!\nNenhum problema encontrado."
                    )
            
        except Exception as e:
            logger.error(f"Erro na validação manual: {str(e)}", exc_info=True)
            messagebox.showerror("Erro", f"Erro na validação: {str(e)}")
            
    def _auto_fix_data(self):
        """Aplica correções automáticas nos dados."""
        try:
            if self.df is None:
                messagebox.showwarning("Aviso", "Por favor, carregue os dados primeiro.")
                return
                
            if self.validator is None:
                self.validator = DataValidator(self.df)
            
            # Confirmar com o usuário
            if not messagebox.askyesno(
                "Confirmar Correção",
                "Isso irá aplicar correções automáticas nos dados, incluindo:\n\n" +
                "- Conversão de colunas para categorical\n" +
                "- Tratamento de outliers\n" +
                "- Agrupamento de valores raros\n" +
                "- Preenchimento de valores ausentes\n\n" +
                "Deseja continuar?"
            ):
                return
            
            # Aplicar correções
            logger.info("Iniciando correção automática dos dados")
            self.df = self.validator.auto_fix_problems()
            
            # Atualizar validador com os dados corrigidos
            self.validator = DataValidator(self.df)
            
            # Atualizar tabela
            self._update_table()
            
            # Mostrar resultados da validação após correção
            results = self.validator.validate_all()
            self._show_validation_results(results)
            
            # Perguntar se deseja exportar os dados corrigidos
            if messagebox.askyesno(
                "Exportar Dados",
                "Dados corrigidos com sucesso!\n\n" +
                "Deseja exportar os dados corrigidos agora?"
            ):
                self._export_data('csv')
            
        except Exception as e:
            logger.error(f"Erro ao corrigir dados: {str(e)}", exc_info=True)
            messagebox.showerror("Erro", f"Erro ao corrigir dados: {str(e)}")
            
    def _export_data(self, format: str):
        """Exporta os dados no formato especificado."""
        try:
            if self.df is None or self.validator is None:
                messagebox.showwarning("Aviso", "Por favor, carregue os dados primeiro.")
                return
                
            # Sugerir o mesmo diretório do arquivo original
            initial_dir = os.path.dirname(self.current_file) if self.current_file else "."
            initial_file = os.path.splitext(os.path.basename(self.current_file))[0] if self.current_file else "dados_corrigidos"
            
            extensions = {
                'csv': '.csv',
                'excel': '.xlsx',
                'parquet': '.parquet',
                'pickle': '.pkl'
            }
            
            filepath = filedialog.asksaveasfilename(
                initialdir=initial_dir,
                initialfile=initial_file,
                defaultextension=extensions[format],
                filetypes=[(format.upper(), f"*{extensions[format]}")]
            )
            
            if filepath:
                self.validator.export_data(filepath, format=format)
                messagebox.showinfo(
                    "Sucesso",
                    f"Dados exportados com sucesso!\n" +
                    f"Um relatório de alterações também foi salvo no mesmo diretório."
                )
                
        except Exception as e:
            logger.error(f"Erro ao exportar dados: {str(e)}", exc_info=True)
            messagebox.showerror("Erro", f"Erro ao exportar dados: {str(e)}")
            
    def _show_version_history(self):
        """Mostra o histórico de alterações."""
        try:
            if self.validator is None:
                messagebox.showwarning("Aviso", "Por favor, carregue os dados primeiro.")
                return
                
            versions = self.validator.get_versions()
            if not versions:
                messagebox.showinfo("Histórico", "Nenhuma alteração registrada.")
                return
                
            # Criar janela de histórico
            history_window = tk.Toplevel(self.root)
            history_window.title("Histórico de Alterações")
            history_window.geometry("600x400")
            
            # Área de texto com scroll
            text_frame = ttk.Frame(history_window)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            text_widget = tk.Text(text_frame, wrap=tk.WORD, width=70, height=20)
            scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Inserir histórico
            for i, version in enumerate(versions, 1):
                text_widget.insert(tk.END, f"\n=== Versão {i} ===\n")
                text_widget.insert(tk.END, version.get_change_summary())
                text_widget.insert(tk.END, "\n")
            
            text_widget.configure(state='disabled')
            
        except Exception as e:
            logger.error(f"Erro ao mostrar histórico: {str(e)}", exc_info=True)
            messagebox.showerror("Erro", f"Erro ao mostrar histórico: {str(e)}")
            
    def _show_quality_report(self):
        """Mostra o relatório de qualidade dos dados."""
        try:
            if self.df is None:
                messagebox.showwarning("Aviso", "Por favor, carregue os dados primeiro.")
                return
                
            if self.validator is None:
                self.validator = DataValidator(self.df)
            
            results = self.validator.validate_all()
            self._show_validation_results(results)
            
        except Exception as e:
            logger.error(f"Erro ao mostrar relatório de qualidade: {str(e)}", exc_info=True)
            messagebox.showerror("Erro", f"Erro ao mostrar relatório de qualidade: {str(e)}")
            
    def _show_validation_results(self, result):
        """Mostra os resultados da validação em uma janela."""
        try:
            # Criar janela de resultados
            results_window = tk.Toplevel(self.root)
            results_window.title("Resultados da Validação")
            results_window.geometry("800x600")
            
            # Criar notebook para diferentes tipos de mensagens
            notebook = ttk.Notebook(results_window)
            notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Separar mensagens por tipo
            errors = [msg for msg in result.messages if msg["type"] == "error"]
            warnings = [msg for msg in result.messages if msg["type"] == "warning"]
            infos = [msg for msg in result.messages if msg["type"] == "info"]
            
            # Função para criar uma aba
            def create_tab(title, messages, icon):
                frame = ttk.Frame(notebook)
                notebook.add(frame, text=f"{icon} {title} ({len(messages)})")
                
                # Área de texto com scroll
                text_frame = ttk.Frame(frame)
                text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
                
                text_widget = tk.Text(text_frame, wrap=tk.WORD, width=70, height=20)
                scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
                text_widget.configure(yscrollcommand=scrollbar.set)
                
                text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                
                # Inserir mensagens
                for msg in messages:
                    text_widget.insert(tk.END, f"{msg['message']}\n\n")
                
                text_widget.configure(state='disabled')
                return frame
            
            # Criar abas para cada tipo de mensagem
            if errors:
                create_tab("Erros", errors, "❌")
            if warnings:
                create_tab("Avisos", warnings, "⚠️")
            if infos:
                create_tab("Informações", infos, "ℹ️")
            
            # Adicionar botões de ação
            button_frame = ttk.Frame(results_window)
            button_frame.pack(fill=tk.X, padx=10, pady=5)
            
            if not result.passed:
                ttk.Button(
                    button_frame,
                    text="Corrigir Problemas",
                    command=lambda: [results_window.destroy(), self._auto_fix_data()]
                ).pack(side=tk.LEFT, padx=5)
                
            ttk.Button(
                button_frame,
                text="Exportar Relatório",
                command=lambda: self._export_validation_report(result)
            ).pack(side=tk.LEFT, padx=5)
            
            ttk.Button(
                button_frame,
                text="Fechar",
                command=results_window.destroy
            ).pack(side=tk.RIGHT, padx=5)
            
        except Exception as e:
            logger.error(f"Erro ao mostrar resultados da validação: {str(e)}", exc_info=True)
            messagebox.showerror("Erro", f"Erro ao mostrar resultados: {str(e)}")
            
    def _export_validation_report(self, result):
        """Exporta o relatório de validação para um arquivo."""
        try:
            # Sugerir o mesmo diretório do arquivo original
            initial_dir = os.path.dirname(self.current_file) if self.current_file else "."
            initial_file = "relatorio_validacao.txt"
            
            filepath = filedialog.asksaveasfilename(
                initialdir=initial_dir,
                initialfile=initial_file,
                defaultextension=".txt",
                filetypes=[("Arquivo de Texto", "*.txt")]
            )
            
            if filepath:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write("=== Relatório de Validação ===\n\n")
                    
                    # Escrever resumo
                    f.write("Resumo:\n")
                    f.write(f"- Status: {'✅ Passou' if result.passed else '❌ Falhou'}\n")
                    f.write(f"- Total de mensagens: {len(result.messages)}\n")
                    f.write(f"  • Erros: {len([m for m in result.messages if m['type'] == 'error'])}\n")
                    f.write(f"  • Avisos: {len([m for m in result.messages if m['type'] == 'warning'])}\n")
                    f.write(f"  • Informações: {len([m for m in result.messages if m['type'] == 'info'])}\n\n")
                    
                    # Escrever mensagens detalhadas
                    f.write("Detalhes:\n")
                    for msg in result.messages:
                        prefix = {
                            "error": "❌ Erro",
                            "warning": "⚠️ Aviso",
                            "info": "ℹ️ Info"
                        }.get(msg["type"], "")
                        f.write(f"\n{prefix}: {msg['message']}")
                    
                    # Escrever detalhes técnicos
                    if result.details:
                        f.write("\n\nDetalhes Técnicos:\n")
                        for key, value in result.details.items():
                            f.write(f"\n{key}: {value}")
                    
                messagebox.showinfo(
                    "Sucesso",
                    f"Relatório de validação exportado com sucesso para:\n{filepath}"
                )
                
        except Exception as e:
            logger.error(f"Erro ao exportar relatório: {str(e)}", exc_info=True)
            messagebox.showerror("Erro", f"Erro ao exportar relatório: {str(e)}")
            
    def _update_table(self):
        """Atualiza a tabela com os dados do DataFrame."""
        if self.df is None:
            return
            
        try:
            logger.debug("Atualizando tabela de dados")
            
            # Limpar tabela atual
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            # Configurar colunas
            self.tree["columns"] = list(self.df.columns)
            self.tree["show"] = "headings"
            
            for column in self.df.columns:
                self.tree.heading(column, text=column)
                # Ajustar largura da coluna baseado no conteúdo
                max_width = max(
                    len(str(column)),
                    self.df[column].astype(str).str.len().max()
                ) * 10
                self.tree.column(column, width=min(max_width, 300))
                
            # Adicionar dados
            for idx, row in self.df.iterrows():
                self.tree.insert("", "end", values=list(row))
                
            logger.debug("Tabela atualizada com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao atualizar tabela: {str(e)}", exc_info=True)
            raise UIError(f"Erro ao atualizar tabela: {str(e)}")
            
    pass
