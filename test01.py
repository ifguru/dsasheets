import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import gspread
from google.oauth2.service_account import Credentials
from tkinter import font as tkfont
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb
from datetime import datetime

class DataManagerApp:
    def __init__(self, root):
        self.root = root
        self.df = None  # DataFrame principal
        self.df_copy = None  # Cópia para modificações
        self.setup_window()
        self.create_styles()
        self.create_widgets()
        
    def setup_window(self):
        self.root.title("Data Manager Pro")
        self.root.geometry("1200x800")  # Aumentado para acomodar gráficos
        # Configurar grid
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
    def create_styles(self):
        # Configurar estilo
        self.style = ttk.Style()
        self.style.configure('Header.TLabel', font=('Segoe UI', 24, 'bold'))
        self.style.configure('Status.TLabel', background='#f0f0f0', padding=5)
        self.style.configure('Action.TButton', font=('Segoe UI', 11), padding=10)
        
    def create_widgets(self):
        # Header
        self.create_header()
        # Main Content
        self.create_main_content()
        # Analysis Menu
        self.create_analysis_menu()
        # Status Bar
        self.create_status_bar()
        
    def create_header(self):
        header_frame = ttk.Frame(self.root)
        header_frame.grid(row=0, column=0, sticky='ew', padx=20, pady=10)
        
        header_label = ttk.Label(
            header_frame, 
            text="Data Manager Pro",
            style='Header.TLabel'
        )
        header_label.pack(side='left')
        
    def create_main_content(self):
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.grid(row=1, column=0, sticky='nsew', padx=20, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(2, weight=1)
        
        # Frame de ações
        actions_frame = ttk.LabelFrame(main_frame, text="Ações", padding=15)
        actions_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        
        # Botões de ação
        ttk.Button(
            actions_frame,
            text="Carregar Arquivo",
            command=self.upload_file,
            style='Action.TButton'
        ).pack(side='left', padx=5)
        
        # Frame para URL do Google Sheets
        sheets_frame = ttk.Frame(actions_frame)
        sheets_frame.pack(side='left', padx=5, fill='x', expand=True)
        
        # Entry para URL
        self.sheets_url = ttk.Entry(sheets_frame, width=50)
        self.sheets_url.pack(side='left', padx=(0, 5))
        self.sheets_url.insert(0, "Cole a URL do Google Sheets aqui")
        self.sheets_url.bind('<FocusIn>', lambda e: self.sheets_url.selection_range(0, tk.END))
        
        ttk.Button(
            sheets_frame,
            text="Acessar Google Sheets",
            command=self.access_google_sheet,
            style='Action.TButton'
        ).pack(side='left')
        
        # Frame de informações
        info_frame = ttk.LabelFrame(main_frame, text="Informações do Arquivo", padding=15)
        info_frame.grid(row=1, column=0, sticky='ew', pady=(0, 10))
        
        self.info_text = tk.Text(info_frame, height=5, wrap='word')
        self.info_text.pack(fill='both', expand=True)
        self.info_text.config(state='disabled')
        
        # Frame de visualização
        preview_frame = ttk.LabelFrame(main_frame, text="Visualização", padding=15)
        preview_frame.grid(row=2, column=0, sticky='nsew')
        
        self.preview_text = tk.Text(preview_frame, wrap='none')
        self.preview_text.pack(fill='both', expand=True)
        self.preview_text.config(state='disabled')
        
    def create_analysis_menu(self):
        # Frame de análise
        analysis_frame = ttk.LabelFrame(self.root, text="Análise de Dados", padding=15)
        analysis_frame.grid(row=1, column=1, sticky='nsew', padx=10, pady=10)
        
        # Botões de análise
        ttk.Button(
            analysis_frame,
            text="Análise Exploratória",
            command=self.show_exploratory_analysis,
            style='Action.TButton'
        ).pack(fill='x', pady=5)
        
        ttk.Button(
            analysis_frame,
            text="Gráficos",
            command=self.show_visualization_options,
            style='Action.TButton'
        ).pack(fill='x', pady=5)
        
        ttk.Button(
            analysis_frame,
            text="Machine Learning",
            command=self.show_ml_options,
            style='Action.TButton'
        ).pack(fill='x', pady=5)
        
        ttk.Button(
            analysis_frame,
            text="Salvar Modificações",
            command=self.save_modifications,
            style='Action.TButton'
        ).pack(fill='x', pady=5)
        
    def create_status_bar(self):
        status_frame = ttk.Frame(self.root)
        status_frame.grid(row=2, column=0, sticky='ew')
        
        self.status_label = ttk.Label(
            status_frame,
            text="Pronto",
            style='Status.TLabel'
        )
        self.status_label.pack(fill='x')
        
    def update_info(self, text):
        self.info_text.config(state='normal')
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, text)
        self.info_text.config(state='disabled')
        
    def update_preview(self, text):
        self.preview_text.config(state='normal')
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(tk.END, text)
        self.preview_text.config(state='disabled')
        
    def update_status(self, text):
        self.status_label.config(text=text)
        
    def upload_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Todos os arquivos suportados", "*.csv;*.xml;*.doc;*.txt"),
                ("CSV files", "*.csv"),
                ("XML files", "*.xml"),
                ("DOC files", "*.doc"),
                ("Text files", "*.txt")
            ]
        )
        if file_path:
            try:
                file_name = os.path.basename(file_path)
                file_size = os.path.getsize(file_path)
                
                info_text = f"Arquivo: {file_name}\n"
                info_text += f"Tamanho: {file_size/1024:.2f} KB\n"
                
                if file_path.endswith('.csv'):
                    self.df = pd.read_csv(file_path)
                    self.df_copy = self.df.copy()
                    info_text += f"Linhas: {len(self.df)}\n"
                    info_text += f"Colunas: {len(self.df.columns)}"
                    
                    # Mostrar preview dos dados
                    preview = self.df.head().to_string()
                    self.update_preview(preview)
                else:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read(1000)  # Primeiros 1000 caracteres
                        self.update_preview(content + "\n...")
                
                self.update_info(info_text)
                self.update_status(f"Arquivo {file_name} carregado com sucesso")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao ler arquivo: {str(e)}")
                self.update_status("Erro ao carregar arquivo")
                
    def authenticate_google_sheets(self):
        try:
            # Define the required scopes
            SCOPES = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive',
                'https://spreadsheets.google.com/feeds'
            ]
            
            # Load credentials and create client
            credentials = Credentials.from_service_account_file(
                'F:/testepanilha/panilhatest-4ef7602af4b3.json',
                scopes=SCOPES
            )
            
            # Connect to Google Sheets
            client = gspread.authorize(credentials)
            
            # Test the connection
            try:
                client.list_spreadsheet_files()
                return client
            except gspread.exceptions.APIError as api_e:
                if "API has not been used in project" in str(api_e):
                    messagebox.showerror("Erro de API", 
                        "A API do Google Sheets não está ativada. Por favor:\n\n" +
                        "1. Acesse: https://console.cloud.google.com\n" +
                        "2. Selecione o projeto 'panilhatest'\n" +
                        "3. Vá para 'APIs & Services' > 'Library'\n" +
                        "4. Procure e ative 'Google Sheets API' e 'Google Drive API'\n\n" +
                        "Após ativar as APIs, tente novamente.")
                else:
                    messagebox.showerror("Erro de API", 
                        "Erro ao conectar com Google Sheets. Verifique se:\n" +
                        "1. As APIs necessárias estão ativadas no Google Cloud Console\n" +
                        "2. A planilha foi compartilhada com:\n" +
                        "   minha-conta-sheets@panilhatest.iam.gserviceaccount.com\n\n" +
                        f"Erro: {str(api_e)}")
                return None
            except Exception as e:
                messagebox.showerror("Connection Error", f"Erro ao conectar com Google Sheets: {str(e)}")
                return None
                
        except Exception as e:
            messagebox.showerror("Authentication Error", 
                "Erro na autenticação. Verifique se:\n" +
                "1. O arquivo de credenciais está correto\n" +
                "2. Você tem permissão para acessar o Google Sheets\n\n" +
                f"Erro: {str(e)}")
            return None
            
    def extract_sheet_id_from_url(self, url):
        """Extrai o ID da planilha da URL do Google Sheets."""
        try:
            if '/d/' in url:
                # Format: https://docs.google.com/spreadsheets/d/SHEET_ID/edit
                sheet_id = url.split('/d/')[1].split('/')[0]
                return sheet_id.strip()
            raise ValueError("URL inválida. Use o formato: https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/")
        except Exception:
            raise ValueError("Não foi possível extrair o ID da planilha da URL. Verifique se a URL está correta.")
            
    def access_google_sheet(self):
        try:
            # Get and validate URL
            url = self.sheets_url.get().strip()
            if not url or url == "Cole a URL do Google Sheets aqui":
                messagebox.showwarning("Aviso", "Por favor, insira a URL do Google Sheets")
                return
            
            # Update status
            self.update_status("Conectando ao Google Sheets...")
            
            # Authenticate
            client = self.authenticate_google_sheets()
            if not client:
                self.update_status("Falha na autenticação")
                return
            
            try:
                # Extract sheet ID and open spreadsheet
                sheet_id = self.extract_sheet_id_from_url(url)
                self.update_status(f"Abrindo planilha {sheet_id}...")
                
                try:
                    spreadsheet = client.open_by_key(sheet_id)
                    worksheet = spreadsheet.sheet1
                    
                    # Get data
                    self.update_status("Carregando dados...")
                    data = worksheet.get_all_records()
                    
                    # Update interface
                    info_text = "Conexão com Google Sheets estabelecida\n"
                    info_text += f"Planilha: {spreadsheet.title}\n"
                    info_text += f"Registros encontrados: {len(data)}"
                    self.update_info(info_text)
                    
                    # Create preview
                    if data:
                        self.df = pd.DataFrame(data)
                        self.df_copy = self.df.copy()
                        preview = f"Primeiras 5 linhas de {len(self.df)} registros:\n\n"
                        preview += self.df.head().to_string()
                        self.update_preview(preview)
                    else:
                        self.update_preview("Nenhum dado encontrado na planilha")
                    
                    self.update_status("Dados do Google Sheets carregados com sucesso")
                    
                except gspread.exceptions.APIError as api_e:
                    if "API has not been used in project" in str(api_e):
                        messagebox.showerror("Erro de API", 
                            "A API do Google Sheets não está ativada. Por favor:\n\n" +
                            "1. Acesse: https://console.cloud.google.com\n" +
                            "2. Selecione o projeto 'panilhatest'\n" +
                            "3. Vá para 'APIs & Services' > 'Library'\n" +
                            "4. Procure e ative 'Google Sheets API' e 'Google Drive API'\n\n" +
                            "Após ativar as APIs, tente novamente.")
                    elif "permission denied" in str(api_e).lower():
                        messagebox.showerror("Erro de Permissão", 
                            "Sem permissão para acessar a planilha. Por favor:\n\n" +
                            "1. Abra a planilha no Google Sheets\n" +
                            "2. Clique em 'Compartilhar' no canto superior direito\n" +
                            "3. Adicione este email como editor:\n" +
                            "   minha-conta-sheets@panilhatest.iam.gserviceaccount.com\n\n" +
                            "Após compartilhar, tente novamente.")
                    else:
                        messagebox.showerror("Erro de API", 
                            "Erro ao acessar a planilha. Verifique se:\n" +
                            "1. A planilha existe\n" +
                            "2. Você tem permissão de acesso\n" +
                            f"Erro: {str(api_e)}")
                    self.update_status("Erro de acesso à planilha")
                    
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao acessar a planilha: {str(e)}")
                    self.update_status("Erro ao acessar planilha")
                
            except ValueError as ve:
                messagebox.showerror("Erro", str(ve))
                self.update_status("URL inválida do Google Sheets")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {str(e)}")
            self.update_status("Erro ao processar a solicitação")
            
    def show_exploratory_analysis(self):
        if self.df is None:
            messagebox.showwarning("Aviso", "Carregue os dados primeiro!")
            return
            
        # Criar janela de análise
        analysis_window = tk.Toplevel(self.root)
        analysis_window.title("Análise Exploratória")
        analysis_window.geometry("800x600")
        
        # Notebook para diferentes análises
        notebook = ttk.Notebook(analysis_window)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Aba de Resumo Estatístico
        stats_frame = ttk.Frame(notebook)
        notebook.add(stats_frame, text="Resumo Estatístico")
        
        stats_text = tk.Text(stats_frame, wrap='none')
        stats_text.pack(fill='both', expand=True)
        
        # Adicionar scrollbar
        scrollbar = ttk.Scrollbar(stats_frame, orient='vertical', command=stats_text.yview)
        scrollbar.pack(side='right', fill='y')
        stats_text.configure(yscrollcommand=scrollbar.set)
        
        # Adicionar informações estatísticas
        stats_text.insert('1.0', "Informações do DataFrame:\n\n")
        stats_text.insert('end', self.df.info(buf=None, max_cols=None))
        stats_text.insert('end', "\n\nResumo Estatístico:\n\n")
        stats_text.insert('end', self.df.describe().to_string())
        stats_text.insert('end', "\n\nCorrelações:\n\n")
        stats_text.insert('end', self.df.corr().to_string())
        stats_text.configure(state='disabled')
        
    def show_visualization_options(self):
        if self.df is None:
            messagebox.showwarning("Aviso", "Carregue os dados primeiro!")
            return
            
        # Criar janela de visualização
        viz_window = tk.Toplevel(self.root)
        viz_window.title("Visualização de Dados")
        viz_window.geometry("1000x800")
        
        # Frame para opções
        options_frame = ttk.LabelFrame(viz_window, text="Opções de Visualização", padding=10)
        options_frame.pack(fill='x', padx=10, pady=5)
        
        # Seleção de tipo de gráfico
        ttk.Label(options_frame, text="Tipo de Gráfico:").pack(side='left', padx=5)
        plot_type = ttk.Combobox(options_frame, values=[
            "Histograma", "Dispersão", "Boxplot", "Barras", "Correlação"
        ])
        plot_type.pack(side='left', padx=5)
        plot_type.set("Histograma")
        
        # Frame para o gráfico
        plot_frame = ttk.Frame(viz_window)
        plot_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        def update_plot():
            plot_frame.destroy()
            new_plot_frame = ttk.Frame(viz_window)
            new_plot_frame.pack(fill='both', expand=True, padx=10, pady=5)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            if plot_type.get() == "Histograma":
                numeric_cols = self.df.select_dtypes(include=[np.number]).columns
                for col in numeric_cols:
                    sns.histplot(data=self.df, x=col, ax=ax)
                    
            elif plot_type.get() == "Correlação":
                sns.heatmap(self.df.corr(), annot=True, cmap='coolwarm', ax=ax)
                
            elif plot_type.get() == "Boxplot":
                numeric_cols = self.df.select_dtypes(include=[np.number]).columns
                self.df.boxplot(column=numeric_cols, ax=ax)
                
            canvas = FigureCanvasTkAgg(fig, new_plot_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
            
        ttk.Button(options_frame, text="Atualizar Gráfico", command=update_plot).pack(side='left', padx=5)
        
    def show_ml_options(self):
        if self.df is None:
            messagebox.showwarning("Aviso", "Carregue os dados primeiro!")
            return
            
        # Criar janela de ML
        ml_window = tk.Toplevel(self.root)
        ml_window.title("Análise de Machine Learning")
        ml_window.geometry("1000x800")
        
        # Frame para opções
        options_frame = ttk.LabelFrame(ml_window, text="Configurações do Modelo", padding=10)
        options_frame.pack(fill='x', padx=10, pady=5)
        
        # Seleção de variável alvo
        ttk.Label(options_frame, text="Variável Alvo:").pack(side='left', padx=5)
        target_var = ttk.Combobox(options_frame, values=list(self.df.columns))
        target_var.pack(side='left', padx=5)
        
        def run_ml_analysis():
            target = target_var.get()
            if not target:
                messagebox.showwarning("Aviso", "Selecione uma variável alvo!")
                return
                
            # Preparar dados
            X = self.df.drop(columns=[target])
            y = self.df[target]
            
            # Codificar variáveis categóricas
            le = LabelEncoder()
            for col in X.select_dtypes(include=['object']):
                X[col] = le.fit_transform(X[col])
            
            # Dividir dados
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
            
            # Treinar modelo
            if y.dtype == np.number:
                model = xgb.XGBRegressor()
            else:
                model = xgb.XGBClassifier()
            
            model.fit(X_train, y_train)
            
            # Mostrar resultados
            results_text.config(state='normal')
            results_text.delete('1.0', tk.END)
            results_text.insert('1.0', f"Análise de Machine Learning para {target}\n\n")
            results_text.insert('end', f"Score no conjunto de teste: {model.score(X_test, y_test):.4f}\n\n")
            results_text.insert('end', "Importância das Features:\n")
            
            feature_importance = pd.DataFrame({
                'feature': X.columns,
                'importance': model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            results_text.insert('end', feature_importance.to_string())
            results_text.config(state='disabled')
            
        ttk.Button(options_frame, text="Executar Análise", command=run_ml_analysis).pack(side='left', padx=5)
        
        # Frame para resultados
        results_frame = ttk.LabelFrame(ml_window, text="Resultados", padding=10)
        results_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        results_text = tk.Text(results_frame, wrap='none')
        results_text.pack(fill='both', expand=True)
        
    def save_modifications(self):
        if self.df_copy is None:
            messagebox.showwarning("Aviso", "Não há modificações para salvar!")
            return
            
        # Opções de salvamento
        save_window = tk.Toplevel(self.root)
        save_window.title("Salvar Modificações")
        save_window.geometry("400x200")
        
        ttk.Label(save_window, text="Escolha o local para salvar:").pack(pady=10)
        
        def save_local():
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")]
            )
            if file_path:
                if file_path.endswith('.csv'):
                    self.df_copy.to_csv(file_path, index=False)
                else:
                    self.df_copy.to_excel(file_path, index=False)
                messagebox.showinfo("Sucesso", "Arquivo salvo com sucesso!")
                save_window.destroy()
                
        def save_google_drive():
            try:
                # Criar novo arquivo no Google Sheets
                client = self.authenticate_google_sheets()
                if not client:
                    return
                    
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                spreadsheet = client.create(f'Análise_DataManager_{timestamp}')
                
                # Converter DataFrame para lista de listas
                data = [self.df_copy.columns.values.tolist()] + self.df_copy.values.tolist()
                
                # Atualizar planilha
                worksheet = spreadsheet.sheet1
                worksheet.clear()
                worksheet.update('A1', data)
                
                messagebox.showinfo("Sucesso", 
                    f"Dados salvos no Google Sheets!\nID da planilha: {spreadsheet.id}")
                save_window.destroy()
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar no Google Drive: {str(e)}")
                
        ttk.Button(save_window, text="Salvar Localmente", command=save_local).pack(pady=10)
        ttk.Button(save_window, text="Salvar no Google Drive", command=save_google_drive).pack(pady=10)
        
if __name__ == "__main__":
    root = tk.Tk()
    app = DataManagerApp(root)
    root.mainloop()