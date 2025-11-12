def main():
    """Função principal chamada pelo main.py"""
    print("🤖 Iniciando treinamento do modelo de ML...")
    
    try:
        from modelo_arima_rf import main as arima_main
        print("🚀 Usando modelo ARIMA + Random Forest...")
        arima_main()
    except ImportError:
        print("📢 Instale: pip install statsmodels")
        print("🔄 Usando modelo Random Forest básico...")
        
        import pandas as pd
        from sklearn.ensemble import RandomForestRegressor
        import numpy as np
        import joblib
        import os

        # Carregar dados
        df = pd.read_csv('dados/dados_onibus.csv')
        
        # Criar features
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hora'] = df['timestamp'].dt.hour
        df['dia_semana'] = df['timestamp'].dt.dayofweek
        df['fim_de_semana'] = (df['dia_semana'] >= 5).astype(int)
        
        # Simular lotação
        np.random.seed(42)
        df['lotacao'] = np.random.randint(20, 100, len(df))
        df.loc[df['hora'].between(7, 9), 'lotacao'] += 20
        df.loc[df['hora'].between(17, 19), 'lotacao'] += 15
        df['lotacao'] = df['lotacao'].clip(0, 100)
        
        # Features para ML
        features = ['hora', 'dia_semana', 'velocidade']
        X = df[features]
        y = df['lotacao']
        
        # Treinar modelo
        modelo = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
        modelo.fit(X, y)
        
        # Garantir que a pasta dados existe
        os.makedirs('dados', exist_ok=True)
        
        # Salvar modelo
        joblib.dump(modelo, 'dados/modelo_lotacao.pkl')
        joblib.dump(features, 'dados/features.pkl')
        
        print("✅ Modelo Random Forest básico treinado!")
        print(f"📊 Dados utilizados: {len(df)} registros")
        print(f"🎯 Features: {features}")

if __name__ == "__main__":
    main()