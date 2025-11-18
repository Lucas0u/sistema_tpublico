# Sistema Inteligente de Transporte Público

Sistema de IA para otimização do transporte público com previsão de lotação e dashboard interativo.

## Objetivo

Otimizar rotas e prever demanda de transporte público usando Machine Learning e Processamento de Linguagem Natural.

## Funcionalidades

- **Previsão de lotação** em tempo real -**Chat inteligente** para consultas -**Dashboard interativo** com gráficos -**Monitoramento** de ônibus em tempo real

## Tecnologias

- **Python** + **Dash** (Dashboard)
- **Scikit-learn** (Machine Learning)
- **NLP** (Processamento de Linguagem Natural)
- **API SPTrans** (Dados em tempo real)

## Como Executar

### 1. Configurar Ambiente Virtual

```bash

# Criar ambiente virtual
python -m venv .venv

# Ativar no Windows
.\.venv\Scripts\Activate.ps1

# Ativar no Linux/Mac
source .venv/bin/activate

# Se tiver requirements.txt
pip install -r requirements.txt

# OU instalar manualmente (recomendado)
pip install pandas matplotlib scikit-learn dash plotly requests joblib numpy flask statsmodels dash

# Executar
python src/main.py
```
