from dash import Dash, html, dcc, Input, Output, callback, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os
import joblib
from datetime import datetime, timedelta
from contexto_planejamento import obter_resumo_contexto

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

# Funções auxiliares
def calcular_lotacao_prevista(hora, dia_semana=None):
    """Calcula previsão de lotação"""
    if modelo and features:
        try:
            if dia_semana is None:
                dia_semana = datetime.now().weekday()
            previsao_df = pd.DataFrame([[hora, dia_semana, 30]], columns=features)
            return modelo.predict(previsao_df)[0]
        except:
            pass
    
    # Fallback: simulação baseada em horários
    if 7 <= hora <= 9:
        return 85
    elif 17 <= hora <= 19:
        return 80
    elif 12 <= hora <= 14:
        return 65
    else:
        return 50

def gerar_previsao_diaria():
    """Gera previsão de lotação para o dia inteiro"""
    horas = list(range(6, 23))
    dia_semana = datetime.now().weekday()
    
    previsoes = []
    for h in horas:
        lotacao = calcular_lotacao_prevista(h, dia_semana)
        previsoes.append({
            'hora': f"{h:02d}:00",
            'lotacao': lotacao,
            'status': 'Lotado' if lotacao > 85 else 'Cheio' if lotacao > 70 else 'Moderado' if lotacao > 50 else 'OK'
        })
    
    return pd.DataFrame(previsoes)

def otimizar_rota(origem_lat, origem_lon, destino_lat, destino_lon):
    """Sugere melhor rota baseada em menor tempo"""
    linhas = df['linha'].unique()
    
    resultados = []
    for linha in linhas:
        df_linha = df[df['linha'] == linha]
        vel_media = df_linha['velocidade'].mean()
        
        # Calcular distância aproximada (Haversine simplificado)
        distancia = np.sqrt((destino_lat - origem_lat)**2 + (destino_lon - origem_lon)**2) * 111  # km aprox
        
        tempo_estimado = (distancia / vel_media) * 60 if vel_media > 0 else 999  # minutos
        
        resultados.append({
            'linha': linha,
            'tempo_min': tempo_estimado,
            'velocidade': vel_media,
            'distancia_km': distancia
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
app = Dash(__name__)

app.layout = html.Div([
    # Título
    html.Div([
        html.H1("Sistema Inteligente de Transporte Público", 
                style={'textAlign': 'center', 'color': '#000000', 'marginBottom': '10px'}),
        html.P("Dashboard em Tempo Real | Machine Learning | Otimização de Rotas", 
               style={'textAlign': 'center', 'fontSize': '18px', 'color': '#555', 'marginBottom': '30px'}),
    ]),
    
    # Estatísticas principais
    html.Div([
        html.Div([
            html.H3(f"{len(df)}", style={'color': '#2E86AB', 'margin': '0', 'fontSize': '36px'}),
            html.P("Ônibus Monitorados", style={'margin': '0', 'fontSize': '14px'})
        ], className='stat-card'),
        
        html.Div([
            html.H3(f"{df['velocidade'].mean():.1f} km/h", style={'color': '#A23B72', 'margin': '0', 'fontSize': '36px'}),
            html.P("Velocidade Média", style={'margin': '0', 'fontSize': '14px'})
        ], className='stat-card'),
        
        html.Div([
            html.H3(f"{len(df['linha'].unique())}", style={'color': '#F18F01', 'margin': '0', 'fontSize': '36px'}),
            html.P("Linhas Ativas", style={'margin': '0', 'fontSize': '14px'})
        ], className='stat-card'),
        
        html.Div([
            html.H3(id='lotacao-atual', children="75%", style={'color': '#06A77D', 'margin': '0', 'fontSize': '36px'}),
            html.P("Lotação Prevista", style={'margin': '0', 'fontSize': '14px'})
        ], className='stat-card'),
    ], className='stats'),

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
    ], style={'marginBottom': '30px'}),
    
    # Linha 1: Mapa + Previsão de Lotação
    html.Div([
        # Mapa de demanda em tempo real
        html.Div([
            html.H3("🗺️ Mapa de Demanda em Tempo Real", style={'color': '#2E86AB', 'marginBottom': '15px'}),
            dcc.Graph(id='mapa-demanda', style={'height': '500px', 'width': '100%'}),
            html.P("🔄 Atualização automática a cada 10 segundos", 
                   style={'textAlign': 'center', 'fontSize': '12px', 'color': '#666', 'marginTop': '10px', 'width': '100%'})
        ], style={'border': '1px solid #ddd', 'display': 'flex', 'flex-direction': 'column',  'verticalAlign': 'top', 'padding': '20px', 'margin': '0 auto', 'align-items': 'center',
                  'backgroundColor': 'white', 'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'marginBottom': '30px'}),
        
        # Previsão de lotação diária
        html.Div([
            html.H3("📈 Previsão de Lotação - Hoje", style={'marginBottom': '15px'}),
            dcc.Graph(id='grafico-previsao-diaria', style={'height': '450px'}),
        ], className='lines'),
    ], className='map'),
    
    # Linha 2: Análise de Eficiência
    html.Div([
        # Velocidade Média vs Esperada
        html.Div([
            html.H3("🚀 Análise de Velocidade", style={'color': '#2E86AB', 'marginBottom': '15px'}),
            dcc.Graph(id='grafico-velocidade-eficiencia', style={'height': '350px'}),
        ], className='efficiency__graphs'),
        
        # Taxa de Ocupação
        html.Div([
            html.H3("📊 Taxa de Ocupação por Linha", style={'color': '#2E86AB', 'marginBottom': '15px'}),
            dcc.Graph(id='grafico-ocupacao', style={'height': '350px'}),
        ], className='efficiency__graphs'),
    ], className='efficiency'),
    
    # Linha 3: Otimização de Rotas
    html.Div([
        html.H3("🎯 Otimização de Rotas - Menor Tempo de Viagem", style={'color': '#2E86AB', 'marginBottom': '15px'}),
        html.Div([
            html.Div([
                html.Label("📍 Origem (Lat):", style={'fontWeight': 'bold', 'marginRight': '10px'}),
                dcc.Input(id='origem-lat', type='number', value=-23.5505, step=0.001, 
                         style={'width': '150px', 'padding': '8px', 'marginRight': '20px'}),
                
                html.Label("📍 Origem (Lon):", style={'fontWeight': 'bold', 'marginRight': '10px'}),
                dcc.Input(id='origem-lon', type='number', value=-46.6333, step=0.001, 
                         style={'width': '150px', 'padding': '8px', 'marginRight': '20px'}),
            ], style={'marginBottom': '15px'}),
            
            html.Div([
                html.Label("🎯 Destino (Lat):", style={'fontWeight': 'bold', 'marginRight': '10px'}),
                dcc.Input(id='destino-lat', type='number', value=-23.5605, step=0.001, 
                         style={'width': '150px', 'padding': '8px', 'marginRight': '20px'}),
                
                html.Label("🎯 Destino (Lon):", style={'fontWeight': 'bold', 'marginRight': '10px'}),
                dcc.Input(id='destino-lon', type='number', value=-46.6433, step=0.001, 
                         style={'width': '150px', 'padding': '8px', 'marginRight': '20px'}),
                
                html.Button('🔍 Calcular Melhor Rota', id='btn-calcular-rota',
                           style={'padding': '10px 24px', 'backgroundColor': '#2E86AB', 'color': 'white', 
                                  'border': 'none', 'borderRadius': '8px', 'cursor': 'pointer', 'fontWeight': 'bold'}),
            ], style={'marginBottom': '20px'}),
        ]),
        
        html.Div(id='resultado-rotas', style={'marginTop': '20px'}),
    ], className='routes'),
    
    # Chat Inteligente com NLP
    html.Div([
        html.H3("💬 Assistente Virtual - IA com Processamento de Linguagem Natural", 
                style={'color': '#2E86AB', 'marginBottom': '15px'}),
        
        html.P("🧠 " + ("NLP Ativo - Classificação de intenções e extração de entidades" if NLP_DISPONIVEL else "Chat básico ativo"), 
               style={'fontSize': '14px', 'color': '#666', 'marginBottom': '15px'}),
        
        dcc.Input(
            id='input-pergunta',
            type='text', 
            placeholder='Ex: Qual lotação da linha 175T-10 às 14h? | Melhor rota para Paulista?',
            style={'width': '70%', 'padding': '12px', 'fontSize': '16px', 
                   'borderRadius': '8px', 'border': '2px solid #2E86AB'}
        ),
        
        html.Button(
            '🚀 Enviar', 
            id='botao-enviar',
            style={'marginLeft': '15px', 'padding': '12px 32px', 'fontSize': '16px', 
                   'backgroundColor': '#2E86AB', 'color': 'white', 'border': 'none', 
                   'borderRadius': '8px', 'cursor': 'pointer', 'fontWeight': 'bold'}
        ),
        
        html.Div(
            id='resposta-chat', 
            children="💡 Faça uma pergunta sobre transporte público!",
            style={'marginTop': '20px', 'padding': '20px', 'border': '2px solid #2E86AB', 
                   'borderRadius': '10px', 'backgroundColor': '#f8f9fa', 'minHeight': '120px',
                   'fontSize': '15px', 'whiteSpace': 'pre-line', 'lineHeight': '1.6'}
        )
    ], className='chat'),
    
    # Intervalo para atualização automática
    dcc.Interval(
        id='interval-update',
        interval=10*1000,  # 10 segundos
        n_intervals=0
    )
    
], className='root')

# Callbacks

@callback(
    Output('mapa-demanda', 'figure'),
    Input('interval-update', 'n_intervals')
)
def atualizar_mapa(n):
    """Atualiza mapa de demanda em tempo real"""
    # Simular lotação por ônibus
    df_map = df.copy()
    hora_atual = datetime.now().hour
    df_map['lotacao'] = df_map.apply(
        lambda row: calcular_lotacao_prevista(hora_atual) + np.random.randint(-10, 10), 
        axis=1
    )
    df_map['lotacao'] = df_map['lotacao'].clip(0, 100)
    
    # Criar mapa
    fig = px.scatter_mapbox(
        df_map,
        lat='lat',
        lon='lon',
        color='lotacao',
        size='lotacao',
        hover_data=['linha', 'velocidade', 'lotacao'],
        color_continuous_scale=['green', 'yellow', 'orange', 'red'],
        size_max=15,
        zoom=11,
        mapbox_style='carto-positron',
        title='Posição dos ônibus com intensidade de lotação'
    )
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=40, b=0),
        coloraxis_colorbar=dict(title="Lotação (%)")
    )
    
    return fig

@callback(
    Output('grafico-previsao-diaria', 'figure'),
    Input('interval-update', 'n_intervals')
)
def atualizar_previsao_diaria(n):
    """Gráfico de previsão de lotação ao longo do dia"""
    df_prev = gerar_previsao_diaria()
    
    fig = go.Figure()
    
    # Adicionar linha de previsão
    fig.add_trace(go.Scatter(
        x=df_prev['hora'],
        y=df_prev['lotacao'],
        mode='lines+markers',
        name='Lotação Prevista',
        line=dict(color='#2E86AB', width=3),
        marker=dict(size=8),
        fill='tozeroy',
        fillcolor='rgba(46, 134, 171, 0.2)'
    ))
    
    # Adicionar linha de referência (capacidade máxima)
    fig.add_hline(y=85, line_dash="dash", line_color="red", 
                  annotation_text="Lotação Crítica", annotation_position="right")
    
    fig.update_layout(
        title='Previsão hora a hora usando Machine Learning',
        xaxis_title='Horário',
        yaxis_title='Lotação (%)',
        hovermode='x unified',
        showlegend=True
    )
    
    return fig

@callback(
    Output('grafico-velocidade-eficiencia', 'figure'),
    Input('interval-update', 'n_intervals')
)
def atualizar_velocidade_eficiencia(n):
    """Análise de velocidade média vs esperada"""
    velocidade_esperada = 30  # km/h
    
    df_vel = df.groupby('linha')['velocidade'].mean().reset_index()
    df_vel['esperada'] = velocidade_esperada
    df_vel['diferenca'] = df_vel['velocidade'] - df_vel['esperada']
    df_vel['status'] = df_vel['diferenca'].apply(lambda x: 'Acima' if x > 0 else 'Abaixo')
    
    fig = go.Figure()
    
    # Velocidade real
    fig.add_trace(go.Bar(
        x=df_vel['linha'],
        y=df_vel['velocidade'],
        name='Velocidade Real',
        marker_color='#2E86AB'
    ))
    
    # Velocidade esperada
    fig.add_trace(go.Scatter(
        x=df_vel['linha'],
        y=df_vel['esperada'],
        name='Velocidade Esperada',
        mode='lines+markers',
        line=dict(color='red', width=2, dash='dash'),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title='Comparação: Velocidade Real vs Esperada (30 km/h)',
        xaxis_title='Linha',
        yaxis_title='Velocidade (km/h)',
        barmode='group',
        hovermode='x unified'
    )
    
    return fig

@callback(
    Output('grafico-ocupacao', 'figure'),
    Input('interval-update', 'n_intervals')
)
def atualizar_ocupacao(n):
    """Taxa de ocupação por linha"""
    hora_atual = datetime.now().hour
    
    linhas = df['linha'].unique()
    ocupacao_data = []
    
    for linha in linhas:
        lotacao = calcular_lotacao_prevista(hora_atual) + np.random.randint(-5, 5)
        ocupacao_data.append({
            'linha': linha,
            'ocupacao': max(0, min(100, lotacao))
        })
    
    df_ocup = pd.DataFrame(ocupacao_data)
    df_ocup['cor'] = df_ocup['ocupacao'].apply(
        lambda x: '#EF4444' if x > 85 else '#F59E0B' if x > 70 else '#10B981'
    )
    
    fig = go.Figure(data=[
        go.Bar(
            x=df_ocup['linha'],
            y=df_ocup['ocupacao'],
            marker_color=df_ocup['cor'],
            text=df_ocup['ocupacao'].apply(lambda x: f'{x:.0f}%'),
            textposition='outside'
        )
    ])
    
    fig.add_hline(y=85, line_dash="dash", line_color="red", 
                  annotation_text="Limite", annotation_position="right")
    
    fig.update_layout(
        title='Taxa de ocupação atual por linha',
        xaxis_title='Linha',
        yaxis_title='Ocupação (%)',
        yaxis_range=[0, 105]
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
    Output('resultado-rotas', 'children'),
    Input('btn-calcular-rota', 'n_clicks'),
    State('origem-lat', 'value'),
    State('origem-lon', 'value'),
    State('destino-lat', 'value'),
    State('destino-lon', 'value'),
    prevent_initial_call=True
)
def calcular_rota_otimizada(n_clicks, orig_lat, orig_lon, dest_lat, dest_lon):
    """Calcula e exibe melhor rota"""
    if n_clicks:
        rotas = otimizar_rota(orig_lat, orig_lon, dest_lat, dest_lon)
        
        # Melhor rota
        melhor = rotas.iloc[0]
        
        resultado = html.Div([
            html.H4("🏆 Rota Recomendada (Menor Tempo)", 
                    style={'color': '#06A77D', 'marginBottom': '15px'}),
            
            html.Div([
                html.Div([
                    html.H3(f"🚌 {melhor['linha']}", style={'color': '#2E86AB', 'margin': '0'}),
                    html.P("Linha Recomendada", style={'margin': '0', 'fontSize': '14px', 'color': '#666'})
                ], style={'flex': '1', 'padding': '15px', 'backgroundColor': '#f0f8ff', 'borderRadius': '8px'}),
                
                html.Div([
                    html.H3(f"⏱️ {melhor['tempo_min']:.0f} min", style={'color': '#F18F01', 'margin': '0'}),
                    html.P("Tempo Estimado", style={'margin': '0', 'fontSize': '14px', 'color': '#666'})
                ], style={'flex': '1', 'padding': '15px', 'backgroundColor': '#f0f8ff', 'borderRadius': '8px', 'marginLeft': '15px'}),
                
                html.Div([
                    html.H3(f"🚀 {melhor['velocidade']:.1f} km/h", style={'color': '#A23B72', 'margin': '0'}),
                    html.P("Velocidade Média", style={'margin': '0', 'fontSize': '14px', 'color': '#666'})
                ], style={'flex': '1', 'padding': '15px', 'backgroundColor': '#f0f8ff', 'borderRadius': '8px', 'marginLeft': '15px'}),
                
                html.Div([
                    html.H3(f"📏 {melhor['distancia_km']:.1f} km", style={'color': '#06A77D', 'margin': '0'}),
                    html.P("Distância", style={'margin': '0', 'fontSize': '14px', 'color': '#666'})
                ], style={'flex': '1', 'padding': '15px', 'backgroundColor': '#f0f8ff', 'borderRadius': '8px', 'marginLeft': '15px'}),
            ], style={'display': 'flex', 'marginBottom': '25px'}),
            
            html.H4("📋 Todas as Rotas Disponíveis", style={'color': '#2E86AB', 'marginBottom': '10px'}),
            
            html.Table([
                html.Thead([
                    html.Tr([
                        html.Th("Posição", style={'padding': '10px', 'backgroundColor': '#2E86AB', 'color': 'white'}),
                        html.Th("Linha", style={'padding': '10px', 'backgroundColor': '#2E86AB', 'color': 'white'}),
                        html.Th("Tempo (min)", style={'padding': '10px', 'backgroundColor': '#2E86AB', 'color': 'white'}),
                        html.Th("Velocidade (km/h)", style={'padding': '10px', 'backgroundColor': '#2E86AB', 'color': 'white'}),
                        html.Th("Distância (km)", style={'padding': '10px', 'backgroundColor': '#2E86AB', 'color': 'white'}),
                    ])
                ]),
                html.Tbody([
                    html.Tr([
                        html.Td(f"#{i+1}", style={'padding': '10px', 'textAlign': 'center', 'fontWeight': 'bold' if i == 0 else 'normal'}),
                        html.Td(row['linha'], style={'padding': '10px'}),
                        html.Td(f"{row['tempo_min']:.0f}", style={'padding': '10px', 'textAlign': 'center'}),
                        html.Td(f"{row['velocidade']:.1f}", style={'padding': '10px', 'textAlign': 'center'}),
                        html.Td(f"{row['distancia_km']:.1f}", style={'padding': '10px', 'textAlign': 'center'}),
                    ], style={'backgroundColor': '#e8f4f8' if i == 0 else 'white'})
                    for i, row in rotas.iterrows()
                ])
            ], style={'width': '100%', 'borderCollapse': 'collapse', 'border': '1px solid #ddd'})
        ])
        
        return resultado
    
    return html.P("👆 Insira as coordenadas e clique em 'Calcular Melhor Rota'", 
                  style={'textAlign': 'center', 'color': '#666', 'padding': '20px'})

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
    print("🔄 Atualização automática: 10 segundos")
    print("🤖 NLP:", "Ativo ✅" if NLP_DISPONIVEL else "Desativado ⚠️")
    print("🧠 ML:", "Ativo ✅" if ML_DISPONIVEL else "Desativado ⚠️")
    print("="*60)
    
    app.run(debug=True, port=8050)