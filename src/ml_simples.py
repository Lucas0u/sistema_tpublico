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

        # Garantir colunas adicionais do contexto
        contexto_defaults = {
            'em_periodo_pico': 0,
            'rodizio_ativo': 0,
            'tem_evento_relevante': 0,
        }
        for coluna, default in contexto_defaults.items():
            if coluna not in df.columns:
                df[coluna] = default

        if 'feriado_nome' in df.columns:
            df['feriado_flag'] = df['feriado_nome'].notna().astype(int)
        else:
            df['feriado_flag'] = 0

        mapa_periodos = {'morning': 1, 'midday': 2, 'afternoon': 3}
        if 'periodo_pico' in df.columns:
            df['periodo_pico_codigo'] = df['periodo_pico'].map(mapa_periodos).fillna(0)
        else:
            df['periodo_pico_codigo'] = 0
        
        # Simular lotação
        np.random.seed(42)
        df['lotacao'] = np.random.randint(20, 100, len(df))
        df.loc[df['hora'].between(7, 9), 'lotacao'] += 20
        df.loc[df['hora'].between(17, 19), 'lotacao'] += 15
        df['lotacao'] = df['lotacao'].clip(0, 100)
        
        # Features para ML
        features = [
            'hora',
            'dia_semana',
            'velocidade',
            'fim_de_semana',
            'em_periodo_pico',
            'rodizio_ativo',
            'feriado_flag',
            'tem_evento_relevante',
            'periodo_pico_codigo',
        ]
        
        # Adicionar features climáticas se disponíveis
        features_climaticas = [
            'temperatura',
            'umidade',
            'precipitacao',
            'tem_chuva',
            'temperatura_categoria_codigo',
            'umidade_alta',
        ]
        
        for feat in features_climaticas:
            if feat in df.columns:
                features.append(feat)
            else:
                # Criar valores padrão se não existir
                if feat == 'temperatura':
                    df['temperatura'] = 22.0  # Temperatura média SP
                elif feat == 'umidade':
                    df['umidade'] = 65.0  # Umidade média SP
                elif feat == 'precipitacao':
                    df['precipitacao'] = 0.0
                elif feat == 'tem_chuva':
                    df['tem_chuva'] = 0
                elif feat == 'temperatura_categoria_codigo':
                    df['temperatura_categoria_codigo'] = 2  # Moderado
                elif feat == 'umidade_alta':
                    df['umidade_alta'] = 0
                features.append(feat)
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