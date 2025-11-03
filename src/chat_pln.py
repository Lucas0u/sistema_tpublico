import joblib
import pandas as pd
from datetime import datetime
import os

def carregar_modelo():
    """Carrega o modelo de ML treinado"""
    try:
        modelo = joblib.load('dados/modelo_lotacao.pkl')
        features = joblib.load('dados/features.pkl')
        print("✅ Modelo de IA carregado com sucesso!")
        return modelo, features
    except FileNotFoundError:
        print("❌ Modelo não encontrado. Execute ml_simples.py primeiro.")
        return None, None

def responder_pergunta(pergunta, modelo=None, features=None):
    """Responde perguntas sobre transporte usando IA"""
    pergunta = pergunta.lower()
    
    if 'lotação' in pergunta or 'cheio' in pergunta or 'vazio' in pergunta:
        if modelo is not None:
            # Previsão para agora
            agora = datetime.now()
            hora = agora.hour
            dia_semana = agora.weekday()
            
            # Usar DataFrame para previsão
            previsao_df = pd.DataFrame([[hora, dia_semana, 30]], columns=features)
            previsao = modelo.predict(previsao_df)[0]
            
            # Classificar status
            if previsao > 85:
                status = "⛔ LOTADO"
                cor = "red"
            elif previsao > 70:
                status = "🟡 CHEIO"
                cor = "orange"
            elif previsao > 50:
                status = "🟢 MODERADO"
                cor = "yellow"
            else:
                status = "🔵 OK"
                cor = "green"
                
            return f"📊 Previsão de lotação atual: {previsao:.0f}% ({status})"
        else:
            return "🔧 Sistema de previsão em manutenção. Tente novamente em alguns minutos."
    
    elif 'tempo' in pergunta or 'espera' in pergunta or 'demora' in pergunta:
        return "⏱️ Tempo médio de espera: **12-15 minutos** (baseado em dados históricos)"
    
    elif 'rota' in pergunta or 'melhor' in pergunta or 'como chegar' in pergunta:
        return "🗺️ **Melhor rota sugerida:** Linha 175T-10\n📍 Tempo estimado: 25 minutos\n🚏 8 paradas até o destino"
    
    elif 'linha' in pergunta or 'ônibus' in pergunta or 'qual ônibus' in pergunta:
        return "🚌 **Linhas disponíveis no seu trajeto:**\n• 175T-10 (a cada 15min)\n• 701U-10 (a cada 20min)\n• 702U-10 (a cada 25min)\n• 877T-10 (a cada 30min)"
    
    elif 'velocidade' in pergunta or 'rápido' in pergunta or 'devagar' in pergunta:
        return "🚀 **Velocidade média dos ônibus:** 25 km/h\n📈 Máxima registrada: 45 km/h\n📉 Mínima registrada: 5 km/h"
    
    elif 'funciona' in pergunta or 'faz' in pergunta or 'ajuda' in pergunta:
        return "🤖 **Posso ajudar com:**\n• 📊 Previsão de lotação\n• ⏱️ Tempo de espera\n• 🗺️ Melhores rotas\n• 🚌 Linhas disponíveis\n• 🚀 Velocidades médias"
    
    elif 'horário' in pergunta or 'pico' in pergunta or 'movimentado' in pergunta:
        return "🕐 **Horários de pico:**\n• Manhã: 7h-9h (85% lotação)\n• Tarde: 17h-19h (80% lotação)\n• Fora do pico: 50-65% lotação"
    
    else:
        return "❓ Não entendi sua pergunta. Tente perguntar sobre:\n• 'Qual a lotação do ônibus?'\n• 'Qual o tempo de espera?'\n• 'Qual a melhor rota?'\n• 'Quais linhas disponíveis?'"

def main():
    """Função principal para testar o chat"""
    print("💬 CHAT DO SISTEMA DE TRANSPORTE")
    print("=" * 40)
    
    # Carregar modelo
    modelo, features = carregar_modelo()
    
    # Testar algumas perguntas
    perguntas_teste = [
        "Qual a lotação do ônibus?",
        "Quanto tempo de espera?",
        "Qual a melhor rota?",
        "Quais linhas disponíveis?",
        "Como está a velocidade?"
    ]
    
    for pergunta in perguntas_teste:
        print(f"\n👤 Você: {pergunta}")
        resposta = responder_pergunta(pergunta, modelo, features)
        print(f"🤖 IA: {resposta}")
        print("-" * 40)

if __name__ == "__main__":
    main()