# Data Manager Pro

<div align="center">
  <img src="docs/images/logo.png" alt="Data Manager Pro Logo" width="200"/>
  
  ![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
  ![License](https://img.shields.io/badge/license-MIT-green)
  [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
</div>

## Visão Geral

Data Manager Pro é uma solução profissional para análise de dados e machine learning, integrando perfeitamente com Google Sheets e oferecendo uma interface gráfica intuitiva. Ideal para cientistas de dados, analistas e profissionais que precisam de uma ferramenta robusta para manipulação e análise de dados.

### Principais Recursos

- **Análise Exploratória de Dados (EDA)**
  - Estatísticas descritivas automatizadas
  - Visualizações interativas
  - Detecção de outliers e valores ausentes

- **Machine Learning Integrado**
  - Modelos de classificação e regressão
  - Avaliação automática de modelos
  - Análise de importância de features

- **Integração com Google Sheets**
  - Sincronização em tempo real
  - Controle de versão de dados
  - Colaboração em equipe

- **Interface Gráfica Moderna**
  - Design responsivo
  - Temas personalizáveis
  - Experiência do usuário intuitiva

## Screenshots

<div align="center">
  <img src="docs/images/dashboard.png" alt="Dashboard" width="600"/>
  <p><em>Dashboard principal mostrando análise de dados em tempo real</em></p>
</div>

<div align="center">
  <img src="docs/images/analysis.png" alt="Análise" width="600"/>
  <p><em>Visualização detalhada de análises estatísticas</em></p>
</div>

## Instalação

```bash
# Clone o repositório
git clone https://github.com/ifguru/dsasheets.git

# Entre no diretório
cd dsasheets

# Instale as dependências
pip install -r requirements.txt

# Execute o aplicativo
python src/main.py
```

## Exemplo de Uso

```python
from src.analysis import DataAnalyzer
from src.ml import ModelTrainer

# Carregue seus dados
data = DataAnalyzer.load_data("seu_arquivo.csv")

# Análise exploratória
analysis = data.get_statistical_summary()
correlations = data.get_correlation_matrix()

# Treine um modelo
model = ModelTrainer(data)
results = model.train_and_evaluate(target="vendas")

# Visualize os resultados
data.plot_insights()
model.plot_feature_importance()
```

## Casos de Uso

### Análise de Vendas
```python
# Carregue dados de vendas do Google Sheets
vendas_data = DataAnalyzer.from_gsheets("ID_DA_PLANILHA")

# Análise temporal
vendas_data.analyze_trends(
    time_column="data",
    metric="receita",
    groupby="produto"
)

# Previsão de vendas futuras
model = ModelTrainer(vendas_data)
previsoes = model.forecast_sales(horizon=30)
```

### Segmentação de Clientes
```python
# Análise de comportamento
clientes = DataAnalyzer.load_data("clientes.csv")
segmentos = clientes.cluster_analysis(
    features=["recencia", "frequencia", "valor"],
    n_clusters=4
)

# Visualização de segmentos
clientes.plot_segments(labels=segmentos)
```

## Roadmap

- [ ] Integração com mais fontes de dados
- [ ] Dashboards personalizáveis
- [ ] Modelos de deep learning
- [ ] API REST
- [ ] Exportação para múltiplos formatos
- [ ] Suporte a processamento distribuído

## Autor

**Data Scientist & ML Engineer**

Especialista em análise de dados e machine learning, com foco em soluções práticas e escaláveis para problemas complexos.

### Contato

- **Telegram**: [@bigdsta](https://t.me/bigdsta)
- **GitHub**: [ifguru](https://github.com/ifguru)
- **Projeto**: [Data Manager Pro](https://github.com/ifguru/dsasheets)

## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

<div align="center">
  <sub>Built with ❤️ by Data Manager Pro Team</sub>
</div>
