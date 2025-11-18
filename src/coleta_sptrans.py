import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import pickle
from math import radians, cos, sin, asin, sqrt

from contexto_planejamento import ContextoPlanejamento
from clima_openmeteo import ClimaOpenMeteo

def haversine(lon1, lat1, lon2, lat2):
    """Calcula distância entre dois pontos em km usando fórmula de Haversine"""
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6371 * c
    return km

def calcular_velocidade_historico(df_atual, historico_anterior):
    """Calcula velocidade baseado em posições anteriores"""
    if historico_anterior is None or len(historico_anterior) == 0:
        return df_atual
    
    df_resultado = df_atual.copy()
    velocidades_calculadas = []
    
    for idx, row in df_resultado.iterrows():
        # Buscar veículo no histórico (mesmo na mesma linha)
        veiculo_historico = historico_anterior[
            (historico_anterior['linha'] == row['linha'])
        ]
        
        if len(veiculo_historico) > 0:
            # Pegar posição mais recente deste veículo
            ultimo = veiculo_historico.iloc[-1]
            
            # Calcular distância percorrida
            dist_km = haversine(ultimo['lon'], ultimo['lat'], row['lon'], row['lat'])
            
            # Calcular tempo decorrido (em horas)
            tempo_diff = (row['timestamp'] - ultimo['timestamp']).total_seconds() / 3600
            
            # Calcular velocidade (km/h)
            if tempo_diff > 0 and dist_km > 0.001:  # Mínimo 1 metro
                velocidade = dist_km / tempo_diff
                # Limitar velocidade a valores realísticos (0-100 km/h)
                velocidade = min(max(velocidade, 0), 100)
            else:
                velocidade = 0
            
            velocidades_calculadas.append(velocidade)
        else:
            velocidades_calculadas.append(0)
    
    df_resultado['velocidade'] = velocidades_calculadas
    return df_resultado

def autenticar_sptrans(token):
    """Tenta autenticar na API da SPTrans"""
    url = f"http://api.olhovivo.sptrans.com.br/v2.1/Login/Autenticar?token={token}"

    session = requests.Session()
    response = session.post(url)

    if response.status_code == 200:
        print("✅ Autenticado com sucesso na SPTrans!")
        return session
    else:
        print(f"❌ Falha na autenticação: {response.status_code}")

def buscar_dados_reais(token):
    """Busca dados reais da SPTrans"""
    session = autenticar_sptrans(token)
    
    if session:
        try:
            url = "http://api.olhovivo.sptrans.com.br/v2.1/Posicao"
            response = session.get(url)
            
            if response.status_code == 200:
                dados = response.json()
                
                if not dados or not isinstance(dados, dict):
                    print("   ⚠️ API retornou resposta vazia")
                    return None
                
                linhas_api = dados.get('l', [])
                print(f"   📊 Linhas encontradas na API: {len(linhas_api)}")
                
                linhas = []
                for linha in linhas_api:
                    if not linha:
                        continue
                    veiculos = linha.get('vs', [])
                    codigo_linha = linha.get('c', '')
                    
                    for veiculo in veiculos:
                        if not veiculo:
                            continue
                        
                        # Velocidade inicial = 0 (será calculada depois baseada em histórico)
                        velocidade = 0
                        
                        linhas.append({
                            'linha': str(codigo_linha),
                            'velocidade': velocidade,
                            'lat': veiculo.get('py', 0),
                            'lon': veiculo.get('px', 0),
                            'timestamp': datetime.now()
                        })
                
                if len(linhas) == 0:
                    print("   ⚠️ API não retornou nenhum veículo ativo")
                    print("   💡 Usando dados de exemplo em seu lugar")
                    return None
                
                df = pd.DataFrame(linhas)
                print(f"   ✅ {len(df)} veículos coletados da API")
                return df
            else:
                print(f"   ⚠️ Status code: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erro na coleta real: {e}")
    
    return None

def criar_dados_exemplo():
    """Cria dados de exemplo quando a API falha"""
    print("🔄 Criando dados de exemplo...")
    
    np.random.seed(42)
    linhas = ['175T-10', '701U-10', '702U-10', '877T-10', '501U-10']
    
    dados = []
    for i in range(45):
        linha = np.random.choice(linhas)
        velocidade = np.random.randint(5, 45)
        lat = -23.5505 + np.random.uniform(-0.03, 0.03)
        lon = -46.6333 + np.random.uniform(-0.03, 0.03)
        
        dados.append({
            'linha': linha,
            'velocidade': velocidade,
            'lat': lat,
            'lon': lon,
            'timestamp': datetime.now() - timedelta(minutes=np.random.randint(0, 120))
        })
    
    df = pd.DataFrame(dados)
    return df


def adicionar_contexto_planejamento(df: pd.DataFrame) -> pd.DataFrame:
    """Enriquece o DataFrame com informações de contexto urbano."""
    if 'timestamp' not in df.columns:
        return df

    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    contexto = ContextoPlanejamento.obter()

    resumos = df['timestamp'].apply(lambda ts: contexto.resumo_diario(ts.to_pydatetime()))

    df['periodo_pico'] = resumos.apply(lambda r: r.get('periodo_pico'))
    df['descricao_pico'] = resumos.apply(lambda r: r.get('descricao_pico'))
    df['em_periodo_pico'] = df['periodo_pico'].notna().astype(int)
    df['rodizio_ativo'] = resumos.apply(lambda r: r.get('rodizio_ativo', False)).astype(int)

    df['feriado_nome'] = resumos.apply(
        lambda r: r.get('feriado', {}).get('nome') if r.get('feriado') else None
    )
    df['feriado_tipo'] = resumos.apply(
        lambda r: r.get('feriado', {}).get('tipo') if r.get('feriado') else None
    )
    df['feriado_categoria'] = resumos.apply(
        lambda r: r.get('feriado', {}).get('categoria') if r.get('feriado') else None
    )

    df['eventos_list'] = resumos.apply(lambda r: r.get('eventos', []))
    df['tem_evento_relevante'] = df['eventos_list'].apply(lambda eventos: int(bool(eventos)))
    df['eventos'] = df['eventos_list'].apply(lambda eventos: "; ".join(eventos) if eventos else None)
    df = df.drop(columns=['eventos_list'])

    return df


def adicionar_dados_climaticos(df: pd.DataFrame) -> pd.DataFrame:
    """Enriquece o DataFrame com dados climáticos de São Paulo"""
    if 'timestamp' not in df.columns:
        return df
    
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    print("   📡 Buscando dados climáticos...")
    clima = ClimaOpenMeteo.obter()
    
    # Obter clima atual uma vez
    clima_atual = clima.obter_clima_atual()
    
    # Valores padrão se API falhar
    if not clima_atual:
        clima_atual = {
            'temperatura': 22.0,
            'umidade': 65.0,
            'precipitacao': 0.0,
            'velocidade_vento': 10.0,
            'codigo_clima': 0
        }
        print("   ⚠️ Usando valores padrão de clima")
    else:
        print(f"   ✅ Clima: {clima_atual.get('temperatura')}°C")
    
    # Aplicar dados climáticos
    df['temperatura'] = clima_atual.get('temperatura', 22.0)
    df['umidade'] = clima_atual.get('umidade', 65.0)
    df['precipitacao'] = clima_atual.get('precipitacao', 0.0)
    df['velocidade_vento'] = clima_atual.get('velocidade_vento', 10.0)
    df['codigo_clima'] = clima_atual.get('codigo_clima', 0)
    
    # Features derivadas
    df['tem_chuva'] = (df['precipitacao'] > 0).astype(int)
    
    # Categoria de temperatura
    temp = clima_atual.get('temperatura', 22.0)
    if temp < 15:
        codigo = 0
    elif temp < 20:
        codigo = 1
    elif temp < 25:
        codigo = 2
    elif temp < 30:
        codigo = 3
    else:
        codigo = 4
    df['temperatura_categoria_codigo'] = codigo
    
    df['umidade_alta'] = (df['umidade'] > 70).astype(int)
    
    return df

def main():
    """Função principal"""
    token = "2a80206e20b1d3be63305d9e703cf2bcc761384f8826975b4c6b55deb70425e9"
    
    print("🚌 Iniciando coleta de dados de transporte público...")

    historico_path = 'dados/historico_posicoes.pkl'
    historico_anterior = None
    if os.path.exists(historico_path):
        try:
            with open(historico_path, 'rb') as f:
                historico_anterior = pickle.load(f)
            print("   📂 Histórico anterior carregado")
        except:
            pass
    
    # Tentar dados reais primeiro
    df = buscar_dados_reais(token)
    
    # Se falhar ou retornar poucos dados, usar dados de exemplo
    if df is None or len(df) == 0:
        df = criar_dados_exemplo()
        print("📊 Dados de exemplo criados")
    else:
        print(f"📊 Dados reais coletados da SPTrans: {len(df)} veículos")
        
        if historico_anterior is not None:
            print("   🧮 Calculando velocidades baseadas em mudanças de posição...")
            df = calcular_velocidade_historico(df, historico_anterior)
            velocidades_nao_zero = (df['velocidade'] > 0).sum()
            print(f"   ✅ {velocidades_nao_zero} veículos com velocidade calculada")
  
        try:
            with open(historico_path, 'wb') as f:
                pickle.dump(df[['linha', 'lat', 'lon', 'timestamp']], f)
        except:
            pass
    
    df = adicionar_contexto_planejamento(df)
    
    # Adicionar dados climáticos
    print("🌤️ Coletando dados climáticos...")
    df = adicionar_dados_climaticos(df)
    print("✅ Dados climáticos adicionados")
    
    # Garantir que a pasta dados existe
    os.makedirs('dados', exist_ok=True)
    
    # Diagnóstico
    print(f"\n📊 Diagnóstico dos dados:")
    print(f"   Total de registros: {len(df)}")
    print(f"   Colunas: {list(df.columns)}")
    print(f"   Primeiras linhas de lat/lon:")
    if 'lat' in df.columns and 'lon' in df.columns:
        print(df[['linha', 'lat', 'lon', 'velocidade']].head())
    
    # Salvar dados
    df.to_csv('dados/dados_onibus.csv', index=False)
    print(f"\n💾 Dados salvos: {len(df)} registros")
    print(f"📋 Linhas: {', '.join(df['linha'].unique())}")

if __name__ == "__main__":
    main()
