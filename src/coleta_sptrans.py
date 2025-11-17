import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

from contexto_planejamento import ContextoPlanejamento

def autenticar_sptrans(token):
    """Tenta autenticar na API da SPTrans"""
    url = "http://api.olhovivo.sptrans.com.br/v2.1/Login/Autenticar"
    
    session = requests.Session()
    response = session.post(url, data={"token": token})
    
    if response.status_code == 200:
        print("✅ Autenticado com sucesso na SPTrans!")
        return session
    else:
        print(f"❌ Falha na autenticação: {response.status_code}")
        return None

def buscar_dados_reais(token):
    """Busca dados reais da SPTrans"""
    session = autenticar_sptrans(token)
    
    if session:
        try:
            url = "http://api.olhovivo.sptrans.com.br/v2.1/Posicao"
            response = session.get(url)
            
            if response.status_code == 200:
                dados = response.json()
                linhas = []
                
                for linha in dados.get('l', []):
                    for veiculo in linha.get('vs', []):
                        linhas.append({
                            'linha': linha.get('c', ''),
                            'velocidade': veiculo.get('v', 0),
                            'lat': veiculo.get('py', 0),
                            'lon': veiculo.get('px', 0),
                            'timestamp': datetime.now()
                        })
                
                df = pd.DataFrame(linhas)
                return df
                
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

def main():
    """Função principal"""
    token = "2a80206e20b1d3be63305d9e703cf2bcc761384f8826975b4c6b55deb70425e9"
    
    print("🚌 Iniciando coleta de dados de transporte público...")
    
    # Tentar dados reais primeiro
    df = buscar_dados_reais(token)
    
    # Se falhar, usar dados de exemplo
    if df is None or len(df) == 0:
        df = criar_dados_exemplo()
        print("📊 Dados de exemplo criados")
    else:
        print("📊 Dados reais coletados da SPTrans")
    
    df = adicionar_contexto_planejamento(df)
    
    # Garantir que a pasta dados existe
    os.makedirs('dados', exist_ok=True)
    
    # Salvar dados
    df.to_csv('dados/dados_onibus.csv', index=False)
    print(f"💾 Dados salvos: {len(df)} registros")
    print(f"📋 Linhas: {', '.join(df['linha'].unique())}")

if __name__ == "__main__":
    main()