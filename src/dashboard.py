from dash import Dash, html, dcc, Input, Output, callback, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os
import joblib
from datetime import datetime, timedelta

# Importações de contexto e clima
try:
    from contexto_planejamento import obter_resumo_contexto
    CONTEXTO_DISPONIVEL = True
except ImportError:
    CONTEXTO_DISPONIVEL = False
    print("⚠️ Módulo contexto_planejamento não encontrado")

try:
    from clima_openmeteo import obter_resumo_clima
    CLIMA_DISPONIVEL = True
except ImportError:
    CLIMA_DISPONIVEL = False
    print("⚠️ Módulo clima_openmeteo não encontrado")

# Importações de contexto e clima
try:
    from contexto_planejamento import obter_resumo_contexto
    CONTEXTO_DISPONIVEL = True
except ImportError:
    CONTEXTO_DISPONIVEL = False
    print("⚠️ Módulo contexto_planejamento não encontrado")

try:
    from clima_openmeteo import obter_resumo_clima
    CLIMA_DISPONIVEL = True
except ImportError:
    CLIMA_DISPONIVEL = False
    print("⚠️ Módulo clima_openmeteo não encontrado")

# Importar módulo NLP
try:
    from nlp_chat import ChatbotNLP
    NLP_DISPONIVEL = True
except ImportError:
    print("⚠️ Módulo NLP não encontrado. Usando chat básico.")
    NLP_DISPONIVEL = False

# Carregar dados
try:
    df = pd.read_csv('dados/dados_onibus.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    print("✅ Dados carregados do CSV")
except Exception as e:
    print(f"⚠️ Erro ao carregar CSV: {e}")
    # Dados de exemplo se falhar
    np.random.seed(42)
    df = pd.DataFrame({
        'velocidade': np.random.randint(10, 45, 50),
        'linha': np.random.choice(['175T-10', '701U-10', '702U-10', '877T-10', '501U-10'], 50),
        'lat': -23.5505 + np.random.uniform(-0.05, 0.05, 50),
        'lon': -46.6333 + np.random.uniform(-0.05, 0.05, 50),
        'timestamp': [datetime.now() - timedelta(minutes=i*5) for i in range(50)]
    })
    print("⚠️ Usando dados de exemplo")

# Carregar modelo ML
try:
    modelo = joblib.load('dados/modelo_final.pkl')
    features = joblib.load('dados/features_finais.pkl')
    print("✅ Modelo ML carregado")
    ML_DISPONIVEL = True
except:
    modelo = None
    features = None
    ML_DISPONIVEL = False
    print("⚠️ Modelo ML não disponível")

# Inicializar chatbot NLP
if NLP_DISPONIVEL and ML_DISPONIVEL:
    chatbot = ChatbotNLP(modelo_ml=modelo, features=features, df_onibus=df)
else:
    chatbot = None
    
# LOCAIS CONHECIDOS
LOCAIS_SP = {
    'Avenida Paulista': (-23.5614, -46.6558),
    'Centro (Sé)': (-23.5505, -46.6333),
    'Vila Mariana': (-23.5880, -46.6354),
    'Pinheiros': (-23.5619, -46.6914),
    'Itaim Bibi': (-23.5866, -46.6847),
    'Zona Sul': (-23.6200, -46.6500),
    'Zona Norte': (-23.5000, -46.6200),
    'Zona Leste': (-23.5505, -46.4700),
    'Zona Oeste': (-23.5505, -46.7400),
    'Consolação': (-23.5552, -46.6611),
    'Bela Vista': (-23.5611, -46.6514),
    'Liberdade': (-23.5591, -46.6344)
}

# LOCAIS CONHECIDOS
LOCAIS_SP = {
    'Avenida Paulista': (-23.5614, -46.6558),
    'Centro (Sé)': (-23.5505, -46.6333),
    'Vila Mariana': (-23.5880, -46.6354),
    'Pinheiros': (-23.5619, -46.6914),
    'Itaim Bibi': (-23.5866, -46.6847),
    'Zona Sul': (-23.6200, -46.6500),
    'Zona Norte': (-23.5000, -46.6200),
    'Zona Leste': (-23.5505, -46.4700),
    'Zona Oeste': (-23.5505, -46.7400),
    'Consolação': (-23.5552, -46.6611),
    'Bela Vista': (-23.5611, -46.6514),
    'Liberdade': (-23.5591, -46.6344)
}

# Funções auxiliares
def calcular_lotacao_prevista(hora, dia_semana=None):
    """
    Calcula previsão de lotação baseada em padrões históricos
    NOTA: API SPTrans não fornece dados de ocupação em tempo real
    """
    if modelo and features:
        try:
            if dia_semana is None:
                dia_semana = datetime.now().weekday()
            
            if linha and linha in df['linha'].values:
                vel_media = df[df['linha'] == linha]['velocidade'].mean()
            else:
                vel_media = 30
            
            previsao_df = pd.DataFrame([[hora, dia_semana, vel_media]], columns=features)
            previsao = modelo.predict(previsao_df)[0]
            variacao = np.random.normal(0, 3)
            return max(10, min(100, previsao + variacao))
        except:
            pass
    
    # Predição baseada em padrões conhecidos de SP
    if dia_semana is None:
        dia_semana = datetime.now().weekday()
    
    # Fim de semana tem menos lotação
    fator_fds = 0.7 if dia_semana >= 5 else 1.0
    
    # Horários de pico
    if 7 <= hora <= 9:
        return int(85 * fator_fds)
    elif 17 <= hora <= 19:
        return int(80 * fator_fds)
    elif 12 <= hora <= 14:
        return int(65 * fator_fds)
    elif 5 <= hora <= 7:
        return int(60 * fator_fds)
    elif 20 <= hora <= 22:
        return int(55 * fator_fds)
    else:
        return int(40 * fator_fds)

def gerar_previsao_diaria():
    """Gera previsão de lotação para o dia inteiro"""
    horas = list(range(6, 24))
    dia_semana = datetime.now().weekday()
    
    previsoes = []
    for h in horas:
        lotacao = calcular_lotacao_prevista(h, dia_semana)
        lotacao = max(10, min(100, lotacao))
        
        if lotacao > 85:
            status = 'Lotado'
        elif lotacao > 70:
            status = 'Cheio'
        elif lotacao > 50:
            status = 'Moderado'
        else:
            status = 'OK'
        
        previsoes.append({
            'hora': f"{h:02d}:00",
            'lotacao': lotacao,
            'status': status
        })
    
    return pd.DataFrame(previsoes)

def calcular_lotacao_por_linha(hora_atual):
    """Calcula lotação específica por linha"""
    linhas = df['linha'].unique()
    dia_semana = datetime.now().weekday()
    
    perfis_linha = {
        '175T-10': {'multiplicador': 1.2, 'base': 5},
        '701U-10': {'multiplicador': 1.0, 'base': 0},
        '702U-10': {'multiplicador': 0.9, 'base': -5},
        '877T-10': {'multiplicador': 0.8, 'base': -10},
        '501U-10': {'multiplicador': 1.1, 'base': 3}
    }
    
    ocupacao_data = []
    for linha in linhas:
        perfil = perfis_linha.get(linha, {'multiplicador': 1.0, 'base': 0})
        lotacao_base = calcular_lotacao_prevista(hora_atual, dia_semana, linha)
        lotacao = lotacao_base * perfil['multiplicador'] + perfil['base']
        lotacao = max(15, min(100, lotacao))
        
        ocupacao_data.append({
            'linha': linha,
            'ocupacao': lotacao
        })
    
    return pd.DataFrame(ocupacao_data)

def otimizar_rota_por_local(origem_nome, destino_nome):
    """Sugere melhor rota usando nomes de locais"""
    if origem_nome not in LOCAIS_SP or destino_nome not in LOCAIS_SP:
        return None
    
    origem_lat, origem_lon = LOCAIS_SP[origem_nome]
    destino_lat, destino_lon = LOCAIS_SP[destino_nome]
    
    linhas = df['linha'].unique()
    hora_atual = datetime.now().hour
    
    resultados = []
    for linha in linhas:
        df_linha = df[df['linha'] == linha]
        vel_media = df_linha['velocidade'].mean()
        distancia = np.sqrt((destino_lat - origem_lat)**2 + (destino_lon - origem_lon)**2) * 111
        tempo_base = (distancia / vel_media) * 60 if vel_media > 0 else 999
        lotacao = calcular_lotacao_prevista(hora_atual)
        fator_lotacao = 1.0 + (lotacao - 50) / 200
        tempo_estimado = tempo_base * fator_lotacao
        
        resultados.append({
            'linha': linha,
            'tempo_min': tempo_estimado,
            'velocidade': vel_media,
            'distancia_km': distancia,
            'lotacao_prevista': lotacao
        })
    
    # Ordenar por tempo e retornar apenas os 10 primeiros
    rotas_df = pd.DataFrame(resultados).sort_values('tempo_min')
    return rotas_df.head(10)

def responder_pergunta_basico(pergunta):
    """Chat básico sem NLP"""
    pergunta = pergunta.lower()
    
    if 'lotação' in pergunta or 'cheio' in pergunta:
        return "📊 Previsão de lotação atual: 75% (🟡 CHEIO)\nBaseado em dados históricos"
    elif 'tempo' in pergunta or 'espera' in pergunta:
        return "⏱️ Tempo médio de espera: 12-15 minutos\n📈 Horário de pico: 7h-9h e 17h-19h"
    elif 'rota' in pergunta:
        return "🗺️ Melhor rota: Linha 175T-10\n⏱️ Tempo estimado: 25 minutos"
    elif 'linha' in pergunta:
        return "🚌 Linhas disponíveis:\n• 175T-10 (15min)\n• 701U-10 (20min)\n• 702U-10 (25min)"
    else:
        return "🤖 Posso ajudar com:\n• Previsão de lotação\n• Tempo de espera\n• Melhores rotas\n• Linhas disponíveis"

# Inicializar app
app = Dash(__name__)

app.layout = html.Div([
    # Título
    html.Div([
        html.H1("🚇 Sistema Inteligente de Transporte Público", className='page-title'),
        html.P("Dashboard em Tempo Real | Machine Learning | Otimização de Rotas", className='page-subtitle'),
        html.Button('🔄 Atualizar Dados', id='btn-atualizar', className='btn-primary btn-update'),
    ], className='header-container'),
    
    # Estatísticas principais
    html.Div([
        html.Div([
            html.H3(id='stat-onibus', children=f"{len(df)}", className='stat-value'),
            html.P("Ônibus Monitorados", className='stat-label')
        ], className='stat-card'),
        
        html.Div([
            html.H3(id='stat-velocidade', children=f"{df['velocidade'].mean():.1f} km/h", className='stat-value stat-value-success'),
            html.P("Velocidade Média", className='stat-label')
        ], className='stat-card'),
        
        html.Div([
            html.H3(id='stat-linhas', children=f"{len(df['linha'].unique())}", className='stat-value stat-value-danger'),
            html.P("Linhas Ativas", className='stat-label')
        ], className='stat-card'),
        
        html.Div([
            html.H3(id='lotacao-atual', children="75%", className='stat-value stat-value-warning'),
            html.P("Lotação Prevista", className='stat-label')
        ], className='stat-card'),
    ], className='stats-container'),
    
    # Contexto e Clima
    html.Div([
        html.Div([
            html.H3("🏙️ Contexto Urbano Oficial", className='section-title'),
            html.Div(id='contexto-planejamento', className='info-box')
        ], className='info-card'),
        
        html.Div([
            html.H3("🌤️ Clima Atual - São Paulo", className='section-title'),
            html.Div(id='clima-atual', className='info-box info-box-climate')
        ], className='info-card'),
    ], className='context-container'),
    
    # Mapa de demanda
    html.Div([
        html.H3("🗺️ Mapa de Demanda em Tempo Real", className='section-title'),
        dcc.Graph(id='mapa-demanda', className='graph-full'),
        html.P("Cores indicam lotação: Verde (OK) → Amarelo (Moderado) → Laranja (Cheio) → Vermelho (Lotado)", 
               className='graph-caption')
    ], className='card map-card'),
    
    # Previsão de lotação
    html.Div([
        html.H3("📈 Previsão de Lotação ao Longo do Dia", className='section-title'),
        dcc.Graph(id='grafico-previsao-diaria', className='graph-full'),
    ], className='card'),
    
    # Análise de Eficiência
    html.Div([
        html.Div([
            html.H3("🚀 Velocidade: Real vs Esperada", className='section-title'),
            dcc.Graph(id='grafico-velocidade-eficiencia', className='graph-medium'),
        ], className='card card-half'),
        
        html.Div([
            html.H3("📊 Taxa de Ocupação Atual", className='section-title'),
            dcc.Graph(id='grafico-ocupacao', className='graph-medium'),
        ], className='card card-half'),
    ], className='efficiency-container'),
    
    # Otimização de Rotas
    html.Div([
        html.H3("🎯 Otimização de Rotas - Menor Tempo de Viagem", className='section-title'),
        html.Div([
            html.Div([
                html.Label("📍 Origem:", className='input-label'),
                dcc.Dropdown(
                    id='origem-dropdown',
                    options=[{'label': local, 'value': local} for local in LOCAIS_SP.keys()],
                    value='Centro (Sé)',
                    className='dropdown-input'
                ),
            ], className='input-group'),
            
            html.Div([
                html.Label("🎯 Destino:", className='input-label'),
                dcc.Dropdown(
                    id='destino-dropdown',
                    options=[{'label': local, 'value': local} for local in LOCAIS_SP.keys()],
                    value='Avenida Paulista',
                    className='dropdown-input'
                ),
            ], className='input-group'),
            
            html.Button('🔍 Calcular Melhor Rota', id='btn-calcular-rota', className='btn-primary'),
        ], className='route-inputs'),
        
        html.Div(id='resultado-rotas', className='route-results'),
    ], className='card routes-card'),
    
    # Chat Inteligente
    html.Div([
        html.H3("💬 Assistente Virtual com NLP", className='section-title'),
        html.P("🧠 " + ("NLP Ativo - Processamento avançado de linguagem natural" if NLP_DISPONIVEL else "Chat básico ativo"), 
               className='chat-status'),
        
        html.Div([
            dcc.Input(
                id='input-pergunta',
                type='text', 
                placeholder='Ex: Qual lotação da linha 175T-10? | Melhor rota para Paulista?',
                className='chat-input'
            ),
            html.Button('🚀 Enviar', id='botao-enviar', className='btn-primary btn-chat'),
        ], className='chat-input-container'),
        
        html.Div(
            id='resposta-chat', 
            children="💡 Faça uma pergunta sobre transporte público!",
            className='chat-response'
        )
    ], className='card chat-card'),
    
    # Store para atualização
    dcc.Store(id='contador-atualizacoes', data=0)
    
], className='root')

# Callbacks

@callback(
    Output('contador-atualizacoes', 'data'),
    Input('btn-atualizar', 'n_clicks'),
    State('contador-atualizacoes', 'data'),
    prevent_initial_call=True
)
def incrementar_contador(n_clicks, contador):
    return (contador or 0) + 1

@callback(
    [Output('mapa-demanda', 'figure'),
     Output('stat-onibus', 'children'),
     Output('stat-velocidade', 'children'),
     Output('stat-linhas', 'children'),
     Output('lotacao-atual', 'children')],
    Input('contador-atualizacoes', 'data')
)
def atualizar_mapa_e_stats(contador):
    df_map = df.copy()
    hora_atual = datetime.now().hour
    
    df_map['lotacao'] = df_map['linha'].apply(
        lambda linha: calcular_lotacao_realista(hora_atual, linha=linha)
    )
    df_map['lotacao'] = df_map['lotacao'].clip(10, 100)
    
    fig = px.scatter_mapbox(
        df_map,
        lat='lat',
        lon='lon',
        color='lotacao',
        size='lotacao',
        hover_data={'linha': True, 'velocidade': True, 'lotacao': ':.0f', 'lat': False, 'lon': False},
        color_continuous_scale=['#27ae60', '#f1c40f', '#e67e22', '#e74c3c'],
        range_color=[0, 100],
        size_max=20,
        zoom=11,
        mapbox_style='carto-positron',
        labels={'lotacao': 'Lotação (%)'}
    )
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        coloraxis_colorbar=dict(
            title="Lotação (%)",
            tickvals=[25, 50, 75, 100],
            ticktext=['25%', '50%', '75%', '100%']
        )
    )
    
    lotacao_media = df_map['lotacao'].mean()
    
    return (
        fig,
        f"{len(df)}",
        f"{df['velocidade'].mean():.1f} km/h",
        f"{len(df['linha'].unique())}",
        f"{lotacao_media:.0f}%"
    )

@callback(
    Output('grafico-previsao-diaria', 'figure'),
    Input('contador-atualizacoes', 'data')
)
def atualizar_previsao_diaria(contador):
    df_prev = gerar_previsao_diaria()
    
    cores = df_prev['status'].map({
        'OK': '#27ae60',
        'Moderado': '#f1c40f',
        'Cheio': '#e67e22',
        'Lotado': '#e74c3c'
    })
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_prev['hora'],
        y=df_prev['lotacao'],
        mode='lines+markers',
        name='Lotação Prevista',
        line=dict(color='#2c3e50', width=3),
        marker=dict(size=10, color=cores, line=dict(color='#2c3e50', width=1)),
        fill='tozeroy',
        fillcolor='rgba(44, 62, 80, 0.1)',
        hovertemplate='<b>%{x}</b><br>Lotação: %{y:.0f}%<extra></extra>'
    ))
    
    fig.add_hline(y=85, line_dash="dash", line_color="#e74c3c", 
                  annotation_text="Lotação Crítica (85%)", annotation_position="right",
                  annotation=dict(font=dict(size=11, color="#e74c3c")))
    fig.add_hline(y=50, line_dash="dot", line_color="#95a5a6", 
                  annotation_text="Lotação Confortável (50%)", annotation_position="right",
                  annotation=dict(font=dict(size=11, color="#95a5a6")))
    
    fig.update_layout(
        title='Previsão usando Machine Learning - Variação hora a hora',
        xaxis_title='Horário',
        yaxis_title='Lotação (%)',
        hovermode='x unified',
        showlegend=False,
        yaxis_range=[0, 105],
        font=dict(color='#333')
    )
    
    return fig

@callback(
    Output('grafico-velocidade-eficiencia', 'figure'),
    Input('contador-atualizacoes', 'data')
)
def atualizar_velocidade_eficiencia(n):
    """Análise de velocidade média vs esperada - Top 15 linhas"""
    
    # Calcular velocidade esperada dinâmica baseada no horário
    hora_atual = datetime.now().hour
    dia_semana = datetime.now().weekday()
    
    # Velocidade esperada varia com horário e dia
    if dia_semana >= 5:  # Fim de semana
        if 0 <= hora_atual < 6:
            velocidade_esperada = 40  # Madrugada livre
        elif 6 <= hora_atual < 10:
            velocidade_esperada = 30  # Manhã tranquila
        elif 10 <= hora_atual < 18:
            velocidade_esperada = 28  # Dia normal
        elif 18 <= hora_atual < 22:
            velocidade_esperada = 32  # Tarde/noite ok
        else:
            velocidade_esperada = 35  # Noite
    else:  # Dia útil
        if 0 <= hora_atual < 5:
            velocidade_esperada = 45  # Madrugada - trânsito livre
        elif 5 <= hora_atual < 7:
            velocidade_esperada = 35  # Manhã cedo
        elif 7 <= hora_atual < 10:
            velocidade_esperada = 18  # PICO MANHÃ - trânsito pesado
        elif 10 <= hora_atual < 12:
            velocidade_esperada = 28  # Meio da manhã
        elif 12 <= hora_atual < 14:
            velocidade_esperada = 22  # Horário de almoço
        elif 14 <= hora_atual < 17:
            velocidade_esperada = 30  # Tarde normal
        elif 17 <= hora_atual < 20:
            velocidade_esperada = 16  # PICO TARDE - trânsito pesado
        elif 20 <= hora_atual < 23:
            velocidade_esperada = 32  # Noite
        else:
            velocidade_esperada = 38  # Noite tardia
    
    try:
        df_vel = df.groupby('linha').agg({
            'velocidade': 'mean',
            'linha': 'count'
        }).rename(columns={'linha': 'count'}).reset_index()
        
        df_vel = df_vel.nlargest(15, 'count')
    except Exception as e:
        print(f"❌ Erro no gráfico de velocidade: {e}")
        return go.Figure()
    
    df_vel['esperada'] = velocidade_esperada
    
    fig = go.Figure()
    
    # Velocidade real - barras azuis
    fig.add_trace(go.Bar(
        x=df_vel['linha'],
        y=df_vel['velocidade'],
        name='Velocidade Real',
        marker=dict(
            color='#4A90B5',  # Azul mais suave
            line=dict(color='#2E86AB', width=1.5)
        ),
        text=df_vel['velocidade'].round(1),
        textposition='none',
        hovertemplate='<b>%{x}</b><br>Velocidade: %{y:.1f} km/h<extra></extra>'
    ))
    
    # Velocidade esperada - linha vermelha tracejada
    fig.add_trace(go.Scatter(
        x=df_vel['linha'],
        y=[velocidade_esperada] * len(df_vel),
        name='Velocidade Esperada',
        mode='lines',
        line=dict(color='#EF4444', width=2.5, dash='dash'),
        hovertemplate='Esperada: %{y} km/h<extra></extra>'
    ))
    
    fig.update_layout(
        title=f'🚀 Análise de Velocidade<br><sub>Comparação: Velocidade Real vs Esperada ({velocidade_esperada} km/h para este horário)</sub>',
        xaxis_title='Linha',
        yaxis_title='Velocidade (km/h)',
        barmode='group',
        hovermode='x unified',
        plot_bgcolor='rgba(240,240,240,0.3)',
        xaxis=dict(
            showgrid=False,
            categoryorder='total descending'
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(200,200,200,0.3)',
            range=[0, max(df_vel['velocidade'].max(), velocidade_esperada) * 1.2]
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(t=80, b=60, l=60, r=20)
    )
    
    return fig

@callback(
    Output('grafico-ocupacao', 'figure'),
    Input('contador-atualizacoes', 'data')
)
def atualizar_ocupacao(n):
    """Taxa de ocupação por linha - Top 15"""
    hora_atual = datetime.now().hour
    df_ocup = calcular_lotacao_por_linha(hora_atual)
    
    try:
        linhas_top = df['linha'].value_counts().head(15).index.tolist()
    except Exception as e:
        print(f"❌ Erro no gráfico de ocupação: {e}")
        return go.Figure()
    
    ocupacao_data = []
    
    for linha in linhas_top:
        lotacao = calcular_lotacao_prevista(hora_atual) + np.random.randint(-5, 5)
        ocupacao_data.append({
            'linha': linha,
            'ocupacao': max(0, min(100, lotacao))
        })
    
    df_ocup = pd.DataFrame(ocupacao_data)
    
    fig = go.Figure()
    
    # Barras de ocupação - laranja uniforme
    fig.add_trace(go.Bar(
        x=df_ocup['linha'],
        y=df_ocup['ocupacao'],
        name='Ocupação',
        marker=dict(
            color='#F59E0B',  # Laranja uniforme
            line=dict(color='#D97706', width=1.5)
        ),
        text=df_ocup['ocupacao'].apply(lambda x: f'{x:.0f}%'),
        textposition='outside',
        textfont=dict(size=11, color='#333'),
        hovertemplate='<b>%{x}</b><br>Ocupação: %{y:.0f}%<extra></extra>'
    ))
    
    # Linha de limite - vermelha tracejada
    fig.add_hline(
        y=85, 
        line_dash="dash", 
        line_color="#EF4444",
        line_width=2.5,
        annotation_text="Limite",
        annotation_position="right",
        annotation=dict(font_size=11, font_color="#EF4444")
    )
    
    fig.update_layout(
        title='📊 Taxa de Ocupação por Linha<br><sub>Taxa de ocupação atual por linha</sub>',
        xaxis_title='Linha',
        yaxis_title='Ocupação (%)',
        yaxis_range=[0, 110],
        plot_bgcolor='rgba(240,240,240,0.3)',
        xaxis=dict(
            showgrid=False
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(200,200,200,0.3)'
        ),
        showlegend=False,
        margin=dict(t=80, b=60, l=60, r=20)
    )
    
    return fig

@callback(
    Output('contexto-planejamento', 'children'),
    Input('contador-atualizacoes', 'data')
)
def atualizar_contexto_planejamento(contador):
    if not CONTEXTO_DISPONIVEL:
        return html.P("Dados de contexto indisponíveis", className='info-unavailable')
    
    resumo = obter_resumo_contexto()
    linhas = []

    if resumo.get('feriado'):
        feriado = resumo['feriado']
        linhas.append(f"Hoje é **{feriado['nome']}** ({feriado['tipo']}).")

    if resumo.get('rodizio_ativo'):
        linhas.append("Rodízio veicular **ativo** no horário atual.")
    else:
        linhas.append("Rodízio inativo neste momento.")

    if resumo.get('periodo_pico'):
        descricao = resumo.get('descricao_pico') or ""
        linhas.append(f"Período de pico: **{resumo['periodo_pico']}**. {descricao}")
    else:
        linhas.append("Fora dos períodos oficiais de pico.")

    if resumo.get('eventos'):
        eventos = ', '.join(resumo['eventos'])
        linhas.append(f"Eventos em destaque: {eventos}.")
    else:
        linhas.append("Sem grandes eventos cadastrados para hoje.")

    markdown = "\n".join([f"- {linha}" for linha in linhas])
    return dcc.Markdown(markdown, dangerously_allow_html=True)

@callback(
    Output('clima-atual', 'children'),
    Input('contador-atualizacoes', 'data')
)
def atualizar_clima_atual(contador):
    if not CLIMA_DISPONIVEL:
        return html.P("Dados climáticos indisponíveis", className='info-unavailable')
    
    resumo = obter_resumo_clima()
    
    if not resumo.get('disponivel'):
        return html.P(resumo.get('mensagem', 'Dados climáticos indisponíveis'), className='info-unavailable')
    
    linhas = []
    linhas.append(f"{resumo['emoji']} **{resumo['descricao']}**")
    
    if resumo.get('temperatura') is not None:
        linhas.append(f"🌡️ Temperatura: **{resumo['temperatura']:.1f}°C**")
    
    if resumo.get('umidade') is not None:
        linhas.append(f"💧 Umidade: **{resumo['umidade']:.0f}%**")
    
    if resumo.get('precipitacao', 0) > 0:
        linhas.append(f"🌧️ Precipitação: **{resumo['precipitacao']:.1f}mm**")
    
    if resumo.get('velocidade_vento') is not None:
        linhas.append(f"💨 Vento: **{resumo['velocidade_vento']:.1f} km/h**")
    
    markdown = "\n".join([f"- {linha}" for linha in linhas])
    return dcc.Markdown(markdown, dangerously_allow_html=True)

@callback(
    Output('resultado-rotas', 'children'),
    Input('btn-calcular-rota', 'n_clicks'),
    State('origem-dropdown', 'value'),
    State('destino-dropdown', 'value'),
    prevent_initial_call=True
)
def calcular_rota_otimizada(n_clicks, origem, destino):
    if not n_clicks or origem == destino:
        return html.P("⚠️ Selecione origem e destino diferentes", className='route-error')
    
    rotas = otimizar_rota_por_local(origem, destino)
    
    if rotas is None or len(rotas) == 0:
        return html.P("❌ Erro ao calcular rotas", className='route-error')
    
    # Garantir que temos no máximo 10 rotas
    rotas = rotas.head(10)
    melhor = rotas.iloc[0]
    
    return html.Div([
        html.H4(f"🏆 Melhor Rota: {origem} → {destino}", className='route-title'),
        
        html.Div([
            html.Div([
                html.H3(f"🚌 {melhor['linha']}", className='route-metric-value'),
                html.P("Linha", className='route-metric-label')
            ], className='route-metric-card'),
            
            html.Div([
                html.H3(f"⏱️ {melhor['tempo_min']:.0f} min", className='route-metric-value route-metric-info'),
                html.P("Tempo", className='route-metric-label')
            ], className='route-metric-card'),
            
            html.Div([
                html.H3(f"🚀 {melhor['velocidade']:.1f} km/h", className='route-metric-value route-metric-purple'),
                html.P("Velocidade", className='route-metric-label')
            ], className='route-metric-card'),
            
            html.Div([
                html.H3(f"📏 {melhor['distancia_km']:.1f} km", className='route-metric-value route-metric-orange'),
                html.P("Distância", className='route-metric-label')
            ], className='route-metric-card'),
            
            html.Div([
                html.H3(f"{melhor['lotacao_prevista']:.0f}%", 
                        className=f"route-metric-value {'route-metric-danger' if melhor['lotacao_prevista'] > 85 else 'route-metric-warning' if melhor['lotacao_prevista'] > 70 else 'route-metric-success'}"),
                html.P("Lotação", className='route-metric-label')
            ], className='route-metric-card'),
        ], className='route-metrics'),
        
        html.H4("📋 Todas as Opções", className='route-subtitle'),
        
        html.Table([
            html.Thead([
                html.Tr([
                    html.Th("#", className='table-header'),
                    html.Th("Linha", className='table-header'),
                    html.Th("Tempo", className='table-header'),
                    html.Th("Velocidade", className='table-header'),
                    html.Th("Distância", className='table-header'),
                    html.Th("Lotação", className='table-header'),
                ])
            ]),
            html.Tbody([
                html.Tr([
                    html.Td(f"#{i+1}", className='table-cell table-cell-center table-cell-bold' if i == 0 else 'table-cell table-cell-center'),
                    html.Td(row['linha'], className='table-cell'),
                    html.Td(f"{row['tempo_min']:.0f} min", className='table-cell table-cell-center'),
                    html.Td(f"{row['velocidade']:.1f} km/h", className='table-cell table-cell-center'),
                    html.Td(f"{row['distancia_km']:.1f} km", className='table-cell table-cell-center'),
                    html.Td(f"{row['lotacao_prevista']:.0f}%", 
                           className=f"table-cell table-cell-center table-cell-bold {'table-cell-danger' if row['lotacao_prevista'] > 85 else 'table-cell-warning' if row['lotacao_prevista'] > 70 else 'table-cell-success'}"),
                ], className='table-row table-row-best' if i == 0 else 'table-row')
                for i, row in rotas.iterrows()
            ])
        ], className='route-table')
    ])

@callback(
    Output('resposta-chat', 'children'),
    Input('botao-enviar', 'n_clicks'),
    State('input-pergunta', 'value'),
    prevent_initial_call=True
)
def responder_chat(n_clicks, pergunta):
    if n_clicks and pergunta:
        if chatbot:
            resposta = chatbot.gerar_resposta(pergunta)
        else:
            resposta = responder_pergunta_basico(pergunta)
        
        return resposta
    
    return "💡 Faça uma pergunta sobre transporte público!"

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚇 DASHBOARD INTELIGENTE DE TRANSPORTE PÚBLICO")
    print("="*60)
    print("🌐 Acesse: http://127.0.0.1:8050")
    print("🔄 Atualização: Manual (botão 'Atualizar Dados')")
    print("🤖 NLP:", "Ativo ✅" if NLP_DISPONIVEL else "Desativado ⚠️")
    print("🧠 ML:", "Ativo ✅" if ML_DISPONIVEL else "Desativado ⚠️")
    print("🏙️ Contexto:", "Ativo ✅" if CONTEXTO_DISPONIVEL else "Desativado ⚠️")
    print("🌤️ Clima:", "Ativo ✅" if CLIMA_DISPONIVEL else "Desativado ⚠️")
    print("="*60)
    
    app.run(debug=True, port=8050)