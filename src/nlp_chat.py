import re
import spacy
from datetime import datetime
import pandas as pd
from pln_processor import ProcessadorPLN

# Carregar modelo de português do spaCy
try:
    nlp = spacy.load("pt_core_news_sm")
except:
    print("⚠️ Modelo spaCy não encontrado. Instale: python -m spacy download pt_core_news_sm")
    nlp = None

class ChatbotNLP:
    """Chatbot com NLP avançado para sistema de transporte"""
    
    def __init__(self, modelo_ml=None, features=None, df_onibus=None):
        self.modelo_ml = modelo_ml
        self.features = features
        self.df_onibus = df_onibus
        
        # Integrar processador PLN
        self.processador_pln = ProcessadorPLN()
        
        # Padrões de intenções
        self.intencoes = {
            'lotacao': ['lotação', 'cheio', 'vazio', 'ocupação', 'lotado', 'passageiros'],
            'tempo_espera': ['tempo', 'espera', 'demora', 'aguardar', 'quanto tempo', 'esperando'],
            'rota': ['rota', 'caminho', 'trajeto', 'melhor rota', 'como chegar', 'ir para'],
            'linha': ['linha', 'ônibus', 'qual ônibus', 'número', 'linhas disponíveis'],
            'velocidade': ['velocidade', 'rápido', 'devagar', 'lento', 'km/h'],
            'horario_pico': ['horário', 'pico', 'movimentado', 'rush', 'hora do rush'],
            'previsao': ['previsão', 'prever', 'futuro', 'próximas horas', 'vai estar'],
        }
        
        # Linhas conhecidas
        self.linhas_conhecidas = ['175T-10', '701U-10', '702U-10', '877T-10', '501U-10']
    
    def extrair_entidades(self, texto):
        """Extrai entidades do texto (linhas, horários, locais)"""
        entidades = {
            'linhas': [],
            'horarios': [],
            'locais': []
        }
        
        # Extrair linhas de ônibus
        for linha in self.linhas_conhecidas:
            if linha.lower() in texto.lower():
                entidades['linhas'].append(linha)
        
        # Extrair horários (formato: 14h, 14:00, 2pm)
        horarios = re.findall(r'\b(\d{1,2})[h:]?(\d{2})?\b', texto)
        for h, m in horarios:
            if int(h) < 24:
                entidades['horarios'].append(f"{h}:{m if m else '00'}")
        
        # Usar spaCy para extrair locais (GPE - Geo-Political Entity)
        if nlp:
            doc = nlp(texto)
            for ent in doc.ents:
                if ent.label_ == 'LOC' or ent.label_ == 'GPE':
                    entidades['locais'].append(ent.text)
        
        return entidades
    
    def obter_analise_pln_detalhada(self, pergunta):
        """
        Retorna análise PLN completa com classificação e entidades
        """
        return self.processador_pln.processar(pergunta)
    
    def classificar_intencao(self, texto):
        """Classifica a intenção do usuário"""
        texto = texto.lower()
        
        # Contar palavras-chave por intenção
        scores = {}
        for intencao, keywords in self.intencoes.items():
            score = sum(1 for kw in keywords if kw in texto)
            if score > 0:
                scores[intencao] = score
        
        # Retornar intenção com maior score
        if scores:
            return max(scores, key=scores.get)
        return 'ajuda'
    
    def prever_lotacao(self, hora=None, dia_semana=None):
        """Previsão de lotação usando ML"""
        if self.modelo_ml is None:
            return None
        
        try:
            import joblib
            if hora is None:
                agora = datetime.now()
                hora = agora.hour
                dia_semana = agora.weekday()
            
            # Criar DataFrame para previsão
            previsao_df = pd.DataFrame([[hora, dia_semana, 30]], columns=self.features)
            previsao = self.modelo_ml.predict(previsao_df)[0]
            
            return previsao
        except Exception as e:
            print(f"Erro na previsão: {e}")
            return None
    
    def gerar_resposta(self, pergunta):
        """Gera resposta inteligente usando NLP"""
        # Extrair entidades
        entidades = self.extrair_entidades(pergunta)
        
        # Classificar intenção
        intencao = self.classificar_intencao(pergunta)
        
        # Gerar resposta baseada na intenção
        if intencao == 'lotacao':
            previsao = self.prever_lotacao()
            if previsao:
                if previsao > 85:
                    status = "⛔ LOTADO"
                elif previsao > 70:
                    status = "🟡 CHEIO"
                elif previsao > 50:
                    status = "🟢 MODERADO"
                else:
                    status = "🔵 OK"
                
                resposta = f"📊 **Previsão de lotação atual:** {previsao:.0f}% ({status})\n"
                
                if entidades['linhas']:
                    resposta += f"🚌 Para a linha {entidades['linhas'][0]}\n"
                
                resposta += "\n💡 **Dica:** Evite horários de pico (7h-9h e 17h-19h)"
                return resposta
            else:
                return "🔧 Sistema de previsão temporariamente indisponível."
        
        elif intencao == 'tempo_espera':
            if entidades['linhas']:
                linha = entidades['linhas'][0]
                tempos = {
                    '175T-10': '12-15',
                    '701U-10': '15-20',
                    '702U-10': '20-25',
                    '877T-10': '25-30',
                    '501U-10': '15-18'
                }
                tempo = tempos.get(linha, '12-20')
                return f"⏱️ **Tempo de espera para linha {linha}:** {tempo} minutos\n📍 Baseado em dados históricos"
            else:
                return "⏱️ **Tempo médio de espera:** 12-20 minutos\n📊 Varia por linha e horário"
        
        elif intencao == 'rota':
            if entidades['locais']:
                destino = entidades['locais'][0]
                return f"🗺️ **Melhor rota para {destino}:**\n🚌 Linha recomendada: 175T-10\n⏱️ Tempo estimado: 25-30 minutos\n🚏 8 paradas\n\n💡 Alternativa: Linha 701U-10 (30-35 min)"
            else:
                return "🗺️ **Para sugerir melhor rota, informe:**\n📍 Seu destino\n🕐 Horário desejado\n\nExemplo: 'Melhor rota para Avenida Paulista às 14h'"
        
        elif intencao == 'linha':
            resposta = "🚌 **Linhas disponíveis:**\n\n"
            linhas_info = [
                "• 175T-10 - A cada 12-15min ⚡ Mais rápida",
                "• 701U-10 - A cada 15-20min",
                "• 702U-10 - A cada 20-25min",
                "• 877T-10 - A cada 25-30min",
                "• 501U-10 - A cada 15-18min"
            ]
            
            if entidades['horarios']:
                horario = entidades['horarios'][0]
                resposta += f"🕐 Para o horário {horario}:\n"
            
            resposta += "\n".join(linhas_info)
            return resposta
        
        elif intencao == 'velocidade':
            if self.df_onibus is not None and len(self.df_onibus) > 0:
                vel_media = self.df_onibus['velocidade'].mean()
                vel_max = self.df_onibus['velocidade'].max()
                vel_min = self.df_onibus['velocidade'].min()
                
                return f"🚀 **Análise de velocidade:**\n📊 Média atual: {vel_media:.1f} km/h\n📈 Máxima: {vel_max:.0f} km/h\n📉 Mínima: {vel_min:.0f} km/h\n\n💡 Velocidade esperada: 30 km/h"
            else:
                return "🚀 **Velocidade média:** 25-30 km/h\n📊 Dados em tempo real indisponíveis"
        
        elif intencao == 'horario_pico':
            return "🕐 **Horários de pico:**\n\n⏰ **Manhã:** 7h-9h\n├─ Lotação média: 85%\n└─ Tempo de espera: +40%\n\n⏰ **Tarde:** 17h-19h\n├─ Lotação média: 80%\n└─ Tempo de espera: +35%\n\n✅ **Melhor horário:** 10h-16h ou após 20h"
        
        elif intencao == 'previsao':
            horas = list(range(6, 23))
            resposta = "📈 **Previsão de lotação para hoje:**\n\n"
            
            for h in [7, 9, 12, 14, 17, 19, 21]:
                prev = self.prever_lotacao(hora=h, dia_semana=datetime.now().weekday())
                if prev:
                    emoji = "⛔" if prev > 85 else "🟡" if prev > 70 else "🟢" if prev > 50 else "🔵"
                    resposta += f"{emoji} {h:02d}h: {prev:.0f}%\n"
            
            return resposta
        
        else:  # ajuda
            return "🤖 **Assistente Virtual de Transporte**\n\n**Posso ajudar com:**\n\n📊 Previsão de lotação\n⏱️ Tempo de espera\n🗺️ Melhores rotas\n🚌 Linhas disponíveis\n🚀 Velocidades médias\n🕐 Horários de pico\n\n**Exemplos:**\n• 'Qual lotação da linha 175T-10?'\n• 'Melhor rota para Paulista às 14h'\n• 'Tempo de espera agora'"

def testar_nlp():
    """Testa o módulo NLP"""
    chat = ChatbotNLP()
    
    perguntas_teste = [
        "Qual a lotação do ônibus agora?",
        "Quanto tempo vou esperar pela linha 175T-10?",
        "Como chegar na Avenida Paulista?",
        "Quais linhas passam aqui?",
        "Qual a velocidade média dos ônibus?",
        "Quais os horários de pico?",
        "Previsão de lotação para hoje"
    ]
    
    print("🧪 TESTANDO MÓDULO NLP")
    print("=" * 60)
    
    for pergunta in perguntas_teste:
        print(f"\n💬 Pergunta: {pergunta}")
        
        # Extrair entidades
        entidades = chat.extrair_entidades(pergunta)
        if any(entidades.values()):
            print(f"🔍 Entidades: {entidades}")
        
        # Classificar intenção
        intencao = chat.classificar_intencao(pergunta)
        print(f"🎯 Intenção: {intencao}")
        
        # Gerar resposta
        resposta = chat.gerar_resposta(pergunta)
        print(f"🤖 Resposta:\n{resposta}")
        print("-" * 60)

if __name__ == "__main__":
    testar_nlp()