import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
from statsmodels.tsa.arima.model import ARIMA
import warnings
warnings.filterwarnings('ignore')

def criar_dados_demanda():
    """Cria dados de demanda realistas para demonstração"""
    np.random.seed(42)
    
    # Criar dados temporais realistas
    dates = pd.date_range('2024-01-01', periods=100, freq='H')
    linhas = ['175T-10', '701U-10', '702U-10', '877T-10']
    
    dados = []
    for i, date in enumerate(dates):
        linha = np.random.choice(linhas)
        hora = date.hour
        
        # Demanda base + variação por horário
        demanda_base = np.random.randint(20, 60)
        
        # Aumentar demanda nos horários de pico
        if 7 <= hora <= 9:   
            demanda_base += 30
        elif 17 <= hora <= 19:  
            demanda_base += 25
        elif 12 <= hora <= 14:  
            demanda_base += 15
            
        # Variação por linha
        if linha == '175T-10':  
            demanda_base += 10
        elif linha == '877T-10':  
            demanda_base -= 5
            
        dados.append({
            'timestamp': date,
            'linha': linha,
            'hora': hora,
            'dia_semana': date.weekday(),
            'fim_de_semana': 1 if date.weekday() >= 5 else 0,
            'demanda_passageiros': max(10, min(100, demanda_base)),
            'velocidade_media': np.random.randint(15, 40)
        })
    
    return pd.DataFrame(dados)

def modelo_arima_previsao(serie_temporal, steps=1):
    """Modelo ARIMA para previsão de séries temporais"""
    try:
        model = ARIMA(serie_temporal, order=(1, 1, 1))
        fitted_model = model.fit()
        previsao = fitted_model.forecast(steps=steps)
        return previsao
    except Exception as e:
        print(f"❌ ARIMA falhou: {e}")
        # Fallback: média móvel
        return [np.mean(serie_temporal[-5:])] * steps

def calcular_mape(y_true, y_pred):
    """Calcula Mean Absolute Percentage Error"""
    return np.mean(np.abs((y_true - y_pred) / np.maximum(np.abs(y_true), 1))) * 100

def main():
    print("🤖 MODELO ARIMA + RANDOM FOREST")
    print("=" * 50)
    
    # Criar dados de demanda
    df = criar_dados_demanda()
    print(f"📊 Dados criados: {len(df)} registros")
    print(f"📅 Período: {df['timestamp'].min()} até {df['timestamp'].max()}")
    
    # Features para Random Forest
    features_rf = ['hora', 'dia_semana', 'fim_de_semana', 'velocidade_media']
    
    # Preparar dados por linha para ARIMA
    linhas = df['linha'].unique()
    resultados = {}
    
    for linha in linhas:
        print(f"\n📈 Processando linha {linha}...")
        
        # Dados da linha específica
        df_linha = df[df['linha'] == linha].copy()
        df_linha = df_linha.sort_values('timestamp')
        
        if len(df_linha) < 10:
            continue
            
        # 1. MODELO RANDOM FOREST
        X = df_linha[features_rf]
        y = df_linha['demanda_passageiros']
        
        # Treinar RF
        rf_model = RandomForestRegressor(n_estimators=50, random_state=42)
        rf_model.fit(X, y)
        y_pred_rf = rf_model.predict(X)
        
        # 2. MODELO ARIMA (série temporal)
        serie_demanda = df_linha['demanda_passageiros'].values
        previsao_arima = modelo_arima_previsao(serie_demanda, steps=3)  # Prever 3 períodos
        
        # 3. COMBINAÇÃO DOS MODELOS
        # Peso maior para RF (70%), ARIMA (30%)
        previsao_combinada = (y_pred_rf[-1] * 0.7 + previsao_arima[0] * 0.3)
        
        # Métricas
        rmse = np.sqrt(mean_squared_error(y, y_pred_rf))
        mae = mean_absolute_error(y, y_pred_rf)
        mape = calcular_mape(y, y_pred_rf)
        
        resultados[linha] = {
            'rf_previsao': y_pred_rf[-1],
            'arima_previsao': previsao_arima[0],
            'combinada': previsao_combinada,
            'rmse': rmse,
            'mae': mae,
            'mape': mape,
            'ultima_demanda': serie_demanda[-1]
        }
    
    # RELATÓRIO FINAL
    print("\n" + "="*60)
    print("📊 RELATÓRIO DE PREDIÇÃO - ARIMA + RANDOM FOREST")
    print("="*60)
    
    for linha, metrics in resultados.items():
        print(f"\n🚌 LINHA {linha}:")
        print(f"   📈 Última demanda real: {metrics['ultima_demanda']:.0f} passageiros")
        print(f"   🤖 Random Forest: {metrics['rf_previsao']:.0f} passageiros")
        print(f"   📊 ARIMA: {metrics['arima_previsao']:.0f} passageiros")
        print(f"   🎯 Combinação: {metrics['combinada']:.0f} passageiros")
        print(f"   📐 RMSE: {metrics['rmse']:.2f}")
        print(f"   📏 MAE: {metrics['mae']:.2f}")
        print(f"   📊 MAPE: {metrics['mape']:.2f}%")
    
    # Salvar modelo
    joblib.dump(rf_model, 'dados/modelo_final.pkl')
    joblib.dump(features_rf, 'dados/features_finais.pkl')
    
    print(f"\n✅ Modelo treinado para {len(resultados)} linhas!")
    print("💾 Salvo em: dados/modelo_final.pkl")

if __name__ == "__main__":
    main()