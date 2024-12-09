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
import tkinter as tk

def main():
    """
    Função principal que inicializa a aplicação.
    """
    root = tk.Tk()
    app = DataManagerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
