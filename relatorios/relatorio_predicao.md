# 📊 RELATÓRIO DE PREDIÇÃO - ARIMA + RANDOM FOREST

## 📅 Data de Geração
17/11/2025 19:02

## 🎯 Objetivo
Relatório das previsões de demanda de passageiros por linha de ônibus utilizando modelo híbrido ARIMA + Random Forest.

## 🤖 Modelo Utilizado
- **Algoritmo:** ARIMA (1,1,1) + Random Forest Regressor
- **Combinação:** 70% Random Forest + 30% ARIMA
- **Features:** ['hora', 'dia_semana', 'fim_de_semana', 'velocidade_media']
- **Período de Treinamento:** 100 registros temporais
- **Horizonte de Previsão:** 3 períodos à frente

## 📈 Resultados por Linha

### 🚌 Linha 175T-10

| Métrica | Valor | Status |
|---------|-------|--------|
| **Previsão** | 61 passageiros | 🎯 |
| **RMSE** | 6.15 | 📐 |
| **MAE** | 4.95 | 📏 |
| **MAPE** | 9.74% | 🏆 Excelente |
| **Demanda Real** | 64 passageiros | 📊 |

### 🚌 Linha 702U-10

| Métrica | Valor | Status |
|---------|-------|--------|
| **Previsão** | 57 passageiros | 🎯 |
| **RMSE** | 5.79 | 📐 |
| **MAE** | 5.08 | 📏 |
| **MAPE** | 12.5% | 👍 Bom |
| **Demanda Real** | 51 passageiros | 📊 |

### 🚌 Linha 877T-10

| Métrica | Valor | Status |
|---------|-------|--------|
| **Previsão** | 35 passageiros | 🎯 |
| **RMSE** | 6.43 | 📐 |
| **MAE** | 5.49 | 📏 |
| **MAPE** | 14.75% | 👍 Bom |
| **Demanda Real** | 25 passageiros | 📊 |

### 🚌 Linha 701U-10

| Métrica | Valor | Status |
|---------|-------|--------|
| **Previsão** | 38 passageiros | 🎯 |
| **RMSE** | 8.08 | 📐 |
| **MAE** | 6.92 | 📏 |
| **MAPE** | 20.64% | 📉 Melhorável |
| **Demanda Real** | 21 passageiros | 📊 |

## 📊 Análise de Performance

### Ranking por Precisão (MAPE)
1. **175T-10** - 9.74% 🏆
2. **702U-10** - 12.50% 👍  
3. **877T-10** - 14.75% 📊
4. **701U-10** - 20.64% 📉

### Erro Médio por Linha
- **MAE Médio:** 5.61 passageiros
- **RMSE Médio:** 6.61 passageiros
- **MAPE Médio:** 14.41%

## 🎯 Conclusões

1. **Alta Precisão:** Linha 175T-10 com MAPE de 9.74% (excelente)
2. **Performance Consistente:** 3 das 4 linhas com MAPE < 15%
3. **Oportunidade de Melhoria:** Linha 701U-10 precisa de ajustes
4. **Validação do Modelo:** Combinação ARIMA + RF mostrou-se eficaz

## 💡 Recomendações

1. **Implementar em Produção:** Modelo pronto para uso real
2. **Monitorar Continuamente:** Acompanhar performance ao longo do tempo
3. **Expandir para Mais Linhas:** Aplicar modelo para outras rotas
4. **Coletar Mais Dados:** Melhorar precisão com mais histórico

---
*Relatório gerado automaticamente pelo Sistema Inteligente de Transporte Público*
