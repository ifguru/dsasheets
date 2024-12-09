"""
Script para testar as funcionalidades básicas do Data Manager Pro.
"""

import pandas as pd
from src.analysis.data_analyzer import DataAnalyzer
from src.ml.model_trainer import ModelTrainer

def main():
    # Carregar dados
    print("Carregando dados...")
    df = pd.read_csv('data/exemplo_vendas.csv')
    
    # Criar instância do analisador
    print("\nIniciando análise de dados...")
    analyzer = DataAnalyzer(df)
    
    # Obter informações básicas
    print("\nInformações básicas do dataset:")
    info = analyzer.get_basic_info()
    print(info)
    
    # Obter resumo estatístico
    print("\nResumo estatístico:")
    stats = analyzer.get_statistical_summary()
    print(stats)
    
    # Obter matriz de correlação
    print("\nMatriz de correlação:")
    corr = analyzer.get_correlation_matrix()
    print(corr)
    
    # Treinar modelo de Machine Learning
    print("\nTreinando modelo de Machine Learning...")
    model = ModelTrainer(df)
    
    # Preparar dados para previsão de valor_total
    X_train, X_test, y_train, y_test = model.prepare_data(target_column='valor_total')
    
    # Treinar modelo
    print("\nTreinando modelo...")
    model.train_model(X_train, y_train)
    
    # Avaliar modelo
    print("\nAvaliando modelo...")
    metrics = model.evaluate_model(X_test, y_test)
    print("Métricas de avaliação:", metrics)
    
    # Mostrar importância das features
    print("\nImportância das features:")
    importance = model.get_feature_importance()
    print(importance)
    
    print("\nTeste concluído com sucesso!")

if __name__ == "__main__":
    main()
