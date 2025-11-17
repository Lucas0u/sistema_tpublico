from dash import Dash, html, dcc, Input, Output, callback, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os
import joblib
from datetime import datetime, timedelta
from contexto_planejamento import obter_resumo_contexto
from clima_openmeteo import obter_resumo_clima

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
except:
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
    modelo = joblib.load('dados/modelo_lotacao.pkl')
    features = joblib.load('dados/features.pkl')
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

# LOCAIS CONHECIDOS PARA SELEÇÃO
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

# Funções auxiliares melhoradas
def calcular_lotacao_realista(hora, dia_semana=None, linha=None):
    """Calcula previsão de lotação de forma mais realista"""
    if modelo and features:
        try:
            if dia_semana is None:
                dia_semana = datetime.now().weekday()
            
            # Usar velocidade média específica da linha
            if linha and linha in df['linha'].values:
                vel_media = df[df['linha'] == linha]['velocidade'].mean()
            else:
                vel_media = 30
            
            previsao_df = pd.DataFrame([[hora, dia_semana, vel_media]], columns=features)
            previsao = modelo.predict(previsao_df)[0]
            
            # Adicionar variação natural
            variacao = np.random.normal(0, 3)
            return max(10, min(100, previsao + variacao))
        except:
            pass
    
    # Fallback com curva realista
    base = 40  # Lotação base
    
    # Fim de semana tem menos movimento
    if dia_semana is not None and dia_semana >= 5:
        base = 30
    
    # Curva de lotação ao longo do dia
    if 6 <= hora < 7:
        return base + 15 + np.random.randint(-5, 5)
    elif 7 <= hora < 9:  # Pico manhã
        return base + 45 + np.random.randint(-8, 8)
    elif 9 <= hora < 11:
        return base + 20 + np.random.randint(-5, 5)
    elif 11 <= hora < 14:  # Almoço
        return base + 25 + np.random.randint(-5, 5)
    elif 14 <= hora < 17:
        return base + 15 + np.random.randint(-5, 5)
    elif 17 <= hora < 20:  # Pico tarde
        return base + 40 + np.random.randint(-8, 8)
    elif 20 <= hora < 22:
        return base + 10 + np.random.randint(-5, 5)
    else:
        return base - 10 + np.random.randint(-5, 5)

def gerar_previsao_diaria():
    """Gera previsão de lotação para o dia inteiro"""
    horas = list(range(6, 24))
    dia_semana = datetime.now().weekday()
    
    previsoes = []
    for h in horas:
        lotacao = calcular_lotacao_realista(h, dia_semana)
        lotacao = max(10, min(100, lotacao))  # Garantir entre 10-100%
        
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
    
    # Características de cada linha
    perfis_linha = {
        '175T-10': {'multiplicador': 1.2, 'base': 5},  # Mais lotada
        '701U-10': {'multiplicador': 1.0, 'base': 0},
        '702U-10': {'multiplicador': 0.9, 'base': -5},
        '877T-10': {'multiplicador': 0.8, 'base': -10},  # Menos lotada
        '501U-10': {'multiplicador': 1.1, 'base': 3}
    }
    
    ocupacao_data = []
    for linha in linhas:
        perfil = perfis_linha.get(linha, {'multiplicador': 1.0, 'base': 0})
        
        # Lotação base
        lotacao_base = calcular_lotacao_realista(hora_atual, dia_semana, linha)
        
        # Aplicar perfil da linha
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
        
        # Calcular distância (Haversine simplificado)
        distancia = np.sqrt((destino_lat - origem_lat)**2 + (destino_lon - origem_lon)**2) * 111
        
        # Tempo estimado
        tempo_base = (distancia / vel_media) * 60 if vel_media > 0 else 999
        
        # Ajustar por lotação prevista
        lotacao = calcular_lotacao_realista(hora_atual, linha=linha)
        fator_lotacao = 1.0 + (lotacao - 50) / 200  # Maior lotação = mais tempo
        
        tempo_estimado = tempo_base * fator_lotacao
        
        resultados.append({
            'linha': linha,
            'tempo_min': tempo_estimado,
            'velocidade': vel_media,
            'distancia_km': distancia,
            'lotacao_prevista': lotacao
        })
    
    return pd.DataFrame(resultados).sort_values('tempo_min')

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
app = Dash(__name__, external_stylesheets=[])

app.layout = html.Div([
    # Título
    html.Div([
        html.H1("🚇 Sistema Inteligente de Transporte Público"),
        html.P("Dashboard em Tempo Real | Machine Learning | Otimização de Rotas", className='project_info'),
        
        # Botão de atualização
        html.Button('🔄 Atualizar Dados', id='btn-atualizar', className='update_button'),
    ]),
    
    # Estatísticas principais
    html.Div([
        html.Div([
            html.H3(id='stat-onibus', children=f"{len(df)}", 
                    style={'color': '#2c3e50', 'margin': '0', 'fontSize': '36px', 'fontWeight': '700'}),
            html.P("Ônibus Monitorados", style={'margin': '0', 'fontSize': '14px', 'color': '#666'})
        ], className='stat-card'),
        
        html.Div([
            html.H3(id='stat-velocidade', children=f"{df['velocidade'].mean():.1f} km/h", 
                    style={'color': '#27ae60', 'margin': '0', 'fontSize': '36px', 'fontWeight': '700'}),
            html.P("Velocidade Média", style={'margin': '0', 'fontSize': '14px', 'color': '#666'})
        ], className='stat-card'),
        
        html.Div([
            html.H3(id='stat-linhas', children=f"{len(df['linha'].unique())}", 
                    style={'color': '#e74c3c', 'margin': '0', 'fontSize': '36px', 'fontWeight': '700'}),
            html.P("Linhas Ativas", style={'margin': '0', 'fontSize': '14px', 'color': '#666'})
        ], className='stat-card'),
        
        html.Div([
            html.H3(id='lotacao-atual', children="75%", 
                    style={'color': '#f39c12', 'margin': '0', 'fontSize': '36px', 'fontWeight': '700'}),
            html.P("Lotação Prevista", style={'margin': '0', 'fontSize': '14px', 'color': '#666'})
        ], className='stat-card'),
    ], className='stats'),

    html.Div([
        html.Div([
            html.H3("Contexto urbano oficial", style={'marginBottom': '10px', 'color': '#2E86AB'}),
            html.Div(
                id='contexto-planejamento',
                style={
                    'border': '1px solid #ddd',
                    'borderRadius': '10px',
                    'padding': '15px',
                    'backgroundColor': '#f8f9fa',
                    'lineHeight': '1.6'
                }
            )
        ], style={'flex': '1', 'marginRight': '15px'}),
        
        html.Div([
            html.H3("🌤️ Clima atual - São Paulo", style={'marginBottom': '10px', 'color': '#2E86AB'}),
            html.Div(
                id='clima-atual',
                style={
                    'border': '1px solid #ddd',
                    'borderRadius': '10px',
                    'padding': '15px',
                    'backgroundColor': '#f0f8ff',
                    'lineHeight': '1.6'
                }
            )
        ], style={'flex': '1'}),
    ], className='info_container'),
    
    # Mapa de demanda
    html.Div([
        html.H2("🗺️ Mapa de Demanda em Tempo Real"),
        dcc.Graph(id='mapa-demanda', style={'height': '600px'}),
        html.P("Cores indicam lotação: Verde (OK) → Amarelo (Moderado) → Laranja (Cheio) → Vermelho (Lotado)", 
               style={'textAlign': 'center', 'fontSize': '12px', 'color': '#666', 'marginTop': '10px'})
    ], className='map'),
    
    # Previsão de lotação
    html.Div([
        html.H2("📈 Previsão de Lotação ao Longo do Dia"),
        dcc.Graph(id='grafico-previsao-diaria', style={'height': '400px'}),
    ], className='lines'),
    
    # Análise de Eficiência
    html.Div([
        html.Div([
            html.H3("🚀 Velocidade: Real vs Esperada", 
                    style={'color': '#2c3e50', 'marginBottom': '15px', 'fontWeight': '600'}),
            dcc.Graph(id='grafico-velocidade-eficiencia', style={'height': '350px'}),
        ], className='efficiency__graphs'),
        html.Div([
            html.H3("📊 Taxa de Ocupação Atual", 
                    style={'color': '#2c3e50', 'marginBottom': '15px', 'fontWeight': '600'}),
            dcc.Graph(id='grafico-ocupacao', style={'height': '350px'}),
        ], className='efficiency__graphs'),
    ], className='efficiency'),
    
    # Otimização de Rotas MELHORADA
    html.Div([
        html.H3("🎯 Otimização de Rotas - Menor Tempo de Viagem", 
                style={'color': '#2c3e50', 'marginBottom': '20px', 'fontWeight': '600'}),
        
        html.Div([
            html.Div([
                html.Label("📍 Origem:", style={'fontWeight': 'bold', 'marginBottom': '8px', 
                                                'display': 'block', 'color': '#333'}),
                dcc.Dropdown(
                    id='origem-dropdown',
                    options=[{'label': local, 'value': local} for local in LOCAIS_SP.keys()],
                    value='Centro (Sé)',
                    style={'width': '300px', 'marginBottom': '20px'}
                ),
            ], style={'display': 'inline-block', 'marginRight': '40px', 'verticalAlign': 'top'}),
            
            html.Div([
                html.Label("🎯 Destino:", style={'fontWeight': 'bold', 'marginBottom': '8px', 
                                                 'display': 'block', 'color': '#333'}),
                dcc.Dropdown(
                    id='destino-dropdown',
                    options=[{'label': local, 'value': local} for local in LOCAIS_SP.keys()],
                    value='Avenida Paulista',
                    style={'width': '300px', 'marginBottom': '20px'}
                ),
            ], style={'display': 'inline-block', 'marginRight': '40px', 'verticalAlign': 'top'}),
            
            html.Button(
                '🔍 Calcular Melhor Rota', 
                id='btn-calcular-rota',
                style={'padding': '12px 32px', 'backgroundColor': '#2c3e50', 'color': 'white', 
                       'border': 'none', 'borderRadius': '8px', 'cursor': 'pointer', 
                       'fontWeight': '600', 'fontSize': '16px', 'marginTop': '28px'}
            ),
        ]),
        
        html.Div(id='resultado-rotas', style={'marginTop': '25px'}),
    ], className='routes'),
    
    # Chat Inteligente
    html.Div([
        html.H3("💬 Assistente Virtual com NLP", 
                style={'color': '#2c3e50', 'marginBottom': '15px', 'fontWeight': '600'}),
        
        html.P("🧠 " + ("NLP Ativo - Processamento avançado de linguagem natural" if NLP_DISPONIVEL else "Chat básico ativo"), 
               style={'fontSize': '14px', 'color': '#666', 'marginBottom': '15px'}),
        
        html.Div([
            dcc.Input(
                id='input-pergunta',
                type='text', 
                placeholder='Ex: Qual lotação da linha 175T-10? | Melhor rota para Paulista?',
                style={'width': '70%', 'padding': '12px', 'fontSize': '16px', 
                       'borderRadius': '8px', 'border': '2px solid #ddd', 'marginRight': '15px'}
            ),
            
            html.Button(
                '🚀 Enviar', 
                id='botao-enviar',
                style={'padding': '12px 32px', 'fontSize': '16px', 
                       'backgroundColor': '#2c3e50', 'color': 'white', 'border': 'none', 
                       'borderRadius': '8px', 'cursor': 'pointer', 'fontWeight': '600'}
            ),
        ], style={'marginBottom': '20px'}),
        
        html.Div(
            id='resposta-chat', 
            children="💡 Faça uma pergunta sobre transporte público!",
            style={'padding': '20px', 'border': '2px solid #ddd', 
                   'borderRadius': '10px', 'backgroundColor': '#f8f9fa', 'minHeight': '120px',
                   'fontSize': '15px', 'whiteSpace': 'pre-line', 'lineHeight': '1.6', 'color': '#333'}
        )
    ], className='routes'),
    
    # Store para controlar atualizações
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
    """Incrementa contador para forçar atualização"""
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
    """Atualiza mapa e estatísticas"""
    df_map = df.copy()
    hora_atual = datetime.now().hour
    
    # Calcular lotação realista por linha
    df_map['lotacao'] = df_map['linha'].apply(
        lambda linha: calcular_lotacao_realista(hora_atual, linha=linha)
    )
    df_map['lotacao'] = df_map['lotacao'].clip(10, 100)
    
    # Criar mapa
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
    
    # Estatísticas
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
    """Gráfico de previsão de lotação ao longo do dia"""
    df_prev = gerar_previsao_diaria()
    
    # Criar cores por status
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
    
    # Linhas de referência
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
def atualizar_velocidade_eficiencia(contador):
    """Análise de velocidade média vs esperada"""
    velocidade_esperada = 30
    
    df_vel = df.groupby('linha')['velocidade'].mean().reset_index()
    df_vel['esperada'] = velocidade_esperada
    df_vel['diferenca'] = df_vel['velocidade'] - df_vel['esperada']
    
    # Cores baseadas em performance
    cores = ['#27ae60' if x >= 0 else '#e74c3c' for x in df_vel['diferenca']]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df_vel['linha'],
        y=df_vel['velocidade'],
        name='Velocidade Real',
        marker_color=cores,
        text=df_vel['velocidade'].apply(lambda x: f'{x:.1f} km/h'),
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Real: %{y:.1f} km/h<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=df_vel['linha'],
        y=df_vel['esperada'],
        name='Meta (30 km/h)',
        mode='lines+markers',
        line=dict(color='#34495e', width=2, dash='dash'),
        marker=dict(size=10, symbol='diamond'),
        hovertemplate='Meta: %{y} km/h<extra></extra>'
    ))
    
    fig.update_layout(
        title='Performance por Linha',
        xaxis_title='Linha',
        yaxis_title='Velocidade (km/h)',
        barmode='group',
        hovermode='x unified',
        showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        font=dict(color='#333')
    )
    
    return fig

@callback(
    Output('grafico-ocupacao', 'figure'),
    Input('contador-atualizacoes', 'data')
)
def atualizar_ocupacao(contador):
    """Taxa de ocupação por linha"""
    hora_atual = datetime.now().hour
    df_ocup = calcular_lotacao_por_linha(hora_atual)
    
    df_ocup['cor'] = df_ocup['ocupacao'].apply(
        lambda x: '#e74c3c' if x > 85 else '#e67e22' if x > 70 else '#f1c40f' if x > 50 else '#27ae60'
    )
    
    fig = go.Figure(data=[
        go.Bar(
            x=df_ocup['linha'],
            y=df_ocup['ocupacao'],
            marker_color=df_ocup['cor'],
            text=df_ocup['ocupacao'].apply(lambda x: f'{x:.0f}%'),
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Ocupação: %{y:.0f}%<extra></extra>'
        )
    ])
    
    fig.add_hline(y=85, line_dash="dash", line_color="#e74c3c", 
                  annotation_text="Limite Crítico", annotation_position="right",
                  annotation=dict(font=dict(size=11, color="#e74c3c")))
    
    fig.update_layout(
        title=f'Ocupação atual ({datetime.now().strftime("%H:%M")})',
        xaxis_title='Linha',
        yaxis_title='Ocupação (%)',
        yaxis_range=[0, 110],
        showlegend=False,
        font=dict(color='#333')
    )
    
    return fig

@callback(
    Output('lotacao-atual', 'children'),
    Input('interval-update', 'n_intervals')
)
def atualizar_lotacao_atual(n):
    """Atualiza lotação atual no card"""
    hora_atual = datetime.now().hour
    lotacao = calcular_lotacao_prevista(hora_atual)
    return f"{lotacao:.0f}%"


@callback(
    Output('contexto-planejamento', 'children'),
    Input('interval-update', 'n_intervals')
)
def atualizar_contexto_planejamento(n):
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
    return dcc.Markdown(markdown, dangerously_allow_html=True, style={'margin': 0})

@callback(
    Output('clima-atual', 'children'),
    Input('interval-update', 'n_intervals')
)
def atualizar_clima_atual(n):
    """Atualiza informações climáticas no dashboard"""
    resumo = obter_resumo_clima()
    
    if not resumo.get('disponivel'):
        return html.P(
            resumo.get('mensagem', 'Dados climáticos indisponíveis'),
            style={'color': '#666', 'margin': 0}
        )
    
    linhas = []
    
    # Emoji e descrição
    linhas.append(f"{resumo['emoji']} **{resumo['descricao']}**")
    
    # Temperatura
    if resumo.get('temperatura') is not None:
        linhas.append(f"🌡️ Temperatura: **{resumo['temperatura']:.1f}°C**")
    
    # Umidade
    if resumo.get('umidade') is not None:
        linhas.append(f"💧 Umidade: **{resumo['umidade']:.0f}%**")
    
    # Precipitação
    if resumo.get('precipitacao', 0) > 0:
        linhas.append(f"🌧️ Precipitação: **{resumo['precipitacao']:.1f}mm**")
    
    # Vento
    if resumo.get('velocidade_vento') is not None:
        linhas.append(f"💨 Vento: **{resumo['velocidade_vento']:.1f} km/h**")
    
    markdown = "\n".join([f"- {linha}" for linha in linhas])
    return dcc.Markdown(markdown, dangerously_allow_html=True, style={'margin': 0})

@callback(
    Output('resultado-rotas', 'children'),
    Input('btn-calcular-rota', 'n_clicks'),
    State('origem-dropdown', 'value'),
    State('destino-dropdown', 'value'),
    prevent_initial_call=True
)
def calcular_rota_otimizada(n_clicks, origem, destino):
    """Calcula e exibe melhor rota"""
    if not n_clicks or origem == destino:
        return html.P("⚠️ Selecione origem e destino diferentes", 
                      style={'textAlign': 'center', 'color': '#e74c3c', 'padding': '20px'})
    
    rotas = otimizar_rota_por_local(origem, destino)
    
    if rotas is None or len(rotas) == 0:
        return html.P("❌ Erro ao calcular rotas", 
                      style={'textAlign': 'center', 'color': '#e74c3c', 'padding': '20px'})
    
    melhor = rotas.iloc[0]
    
    return html.Div([
        html.Div([
            html.H4(f"🏆 Melhor Rota: {origem} → {destino}", 
                    style={'color': '#27ae60', 'marginBottom': '20px', 'fontWeight': '600'}),
        ]),
        
        html.Div([
            html.Div([
                html.H3(f"🚌 {melhor['linha']}", style={'color': '#2c3e50', 'margin': '0', 'fontWeight': '700'}),
                html.P("Linha", style={'margin': '0', 'fontSize': '14px', 'color': '#666'})
            ], style={'flex': '1', 'padding': '20px', 'backgroundColor': '#ecf0f1', 'borderRadius': '10px', 'textAlign': 'center'}),
            
            html.Div([
                html.H3(f"⏱️ {melhor['tempo_min']:.0f} min", style={'color': '#3498db', 'margin': '0', 'fontWeight': '700'}),
                html.P("Tempo", style={'margin': '0', 'fontSize': '14px', 'color': '#666'})
            ], style={'flex': '1', 'padding': '20px', 'backgroundColor': '#ecf0f1', 'borderRadius': '10px', 'marginLeft': '15px', 'textAlign': 'center'}),
            
            html.Div([
                html.H3(f"🚀 {melhor['velocidade']:.1f} km/h", style={'color': '#9b59b6', 'margin': '0', 'fontWeight': '700'}),
                html.P("Velocidade", style={'margin': '0', 'fontSize': '14px', 'color': '#666'})
            ], style={'flex': '1', 'padding': '20px', 'backgroundColor': '#ecf0f1', 'borderRadius': '10px', 'marginLeft': '15px', 'textAlign': 'center'}),
            
            html.Div([
                html.H3(f"📏 {melhor['distancia_km']:.1f} km", style={'color': '#e67e22', 'margin': '0', 'fontWeight': '700'}),
                html.P("Distância", style={'margin': '0', 'fontSize': '14px', 'color': '#666'})
            ], style={'flex': '1', 'padding': '20px', 'backgroundColor': '#ecf0f1', 'borderRadius': '10px', 'marginLeft': '15px', 'textAlign': 'center'}),
            
            html.Div([
                html.H3(f"{melhor['lotacao_prevista']:.0f}%", 
                        style={'color': '#e74c3c' if melhor['lotacao_prevista'] > 85 else '#f39c12' if melhor['lotacao_prevista'] > 70 else '#27ae60', 
                               'margin': '0', 'fontWeight': '700'}),
                html.P("Lotação", style={'margin': '0', 'fontSize': '14px', 'color': '#666'})
            ], style={'flex': '1', 'padding': '20px', 'backgroundColor': '#ecf0f1', 'borderRadius': '10px', 'marginLeft': '15px', 'textAlign': 'center'}),
        ], className='info_container'),
        
        html.H4("📋 Todas as Opções", style={'color': '#2c3e50', 'marginBottom': '15px', 'fontWeight': '600'}),
        
        html.Table([
            html.Thead([
                html.Tr([
                    html.Th("#", style={'padding': '12px', 'backgroundColor': '#34495e', 'color': 'white', 'fontWeight': '600'}),
                    html.Th("Linha", style={'padding': '12px', 'backgroundColor': '#34495e', 'color': 'white', 'fontWeight': '600'}),
                    html.Th("Tempo", style={'padding': '12px', 'backgroundColor': '#34495e', 'color': 'white', 'fontWeight': '600'}),
                    html.Th("Velocidade", style={'padding': '12px', 'backgroundColor': '#34495e', 'color': 'white', 'fontWeight': '600'}),
                    html.Th("Distância", style={'padding': '12px', 'backgroundColor': '#34495e', 'color': 'white', 'fontWeight': '600'}),
                    html.Th("Lotação", style={'padding': '12px', 'backgroundColor': '#34495e', 'color': 'white', 'fontWeight': '600'}),
                ])
            ]),
            html.Tbody([
                html.Tr([
                    html.Td(f"#{i+1}", style={'padding': '12px', 'textAlign': 'center', 'fontWeight': '700' if i == 0 else 'normal', 'color': '#333'}),
                    html.Td(row['linha'], style={'padding': '12px', 'color': '#333'}),
                    html.Td(f"{row['tempo_min']:.0f} min", style={'padding': '12px', 'textAlign': 'center', 'color': '#333'}),
                    html.Td(f"{row['velocidade']:.1f} km/h", style={'padding': '12px', 'textAlign': 'center', 'color': '#333'}),
                    html.Td(f"{row['distancia_km']:.1f} km", style={'padding': '12px', 'textAlign': 'center', 'color': '#333'}),
                    html.Td(f"{row['lotacao_prevista']:.0f}%", 
                           style={'padding': '12px', 'textAlign': 'center', 
                                  'color': '#e74c3c' if row['lotacao_prevista'] > 85 else '#f39c12' if row['lotacao_prevista'] > 70 else '#27ae60',
                                  'fontWeight': '600'}),
                ], style={'backgroundColor': '#d5f4e6' if i == 0 else 'white', 
                         'borderBottom': '1px solid #ddd'})
                for i, row in rotas.iterrows()
            ])
        ], style={'width': '100%', 'borderCollapse': 'collapse', 'border': '1px solid #ddd', 'borderRadius': '8px', 'overflow': 'hidden'})
    ])

@callback(
    Output('resposta-chat', 'children'),
    Input('botao-enviar', 'n_clicks'),
    State('input-pergunta', 'value'),
    prevent_initial_call=True
)
def responder_chat(n_clicks, pergunta):
    """Responde perguntas usando NLP"""
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
    print("="*60)
    
    app.run(debug=True, port=8050)