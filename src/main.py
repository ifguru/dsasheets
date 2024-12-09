"""
Data Manager Pro - Main Application

Este é o ponto de entrada principal do aplicativo Data Manager Pro.
O aplicativo fornece uma interface gráfica para análise de dados,
integração com Google Sheets e recursos de Machine Learning.
"""

import sys
import os

# Adiciona o diretório src ao PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.gui.app import DataManagerApp
from src.utils.debug_monitor import start_monitoring, stop_monitoring, logger
import tkinter as tk

def main():
    """
    Função principal que inicializa a aplicação.
    """
    try:
        # Iniciar monitoramento
        start_monitoring()
        logger.info("Iniciando Data Manager Pro")
        
        # Criar janela principal
        root = tk.Tk()
        
        # Configurar handler para fechamento da janela
        def on_closing():
            logger.info("Finalizando aplicação")
            stop_monitoring()
            root.destroy()
            
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Iniciar aplicação
        app = DataManagerApp(root)
        logger.info("Interface gráfica inicializada com sucesso")
        
        # Iniciar loop principal
        root.mainloop()
        
    except Exception as e:
        logger.error(f"Erro fatal na aplicação: {str(e)}")
        logger.error("Stacktrace:", exc_info=True)
        raise

if __name__ == "__main__":
    main()
