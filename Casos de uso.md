# 📚 Exemplos de Uso - Sistema Inteligente de Transporte Público

## 🎯 Casos de Uso Práticos

---

## 1. 👤 Usuário Procurando Ônibus Menos Lotado

### Cenário:
Maria precisa pegar o ônibus às 8h da manhã (horário de pico) e quer saber qual linha está menos lotada.

### Interação com o Chat:

```
👤 Maria: "Qual linha está menos lotada agora?"

🤖 IA: 📊 Previsão de lotação atual:

       🟢 701U-10: 65% (MODERADO)
       🟡 175T-10: 78% (CHEIO)
       ⛔ 877T-10: 87% (LOTADO)
       
       💡 Recomendação: Use a linha 701U-10
       ⏱️ Tempo de espera: 15-20 minutos
```

### No Dashboard:
- Visualização no mapa mostrando ônibus 701U-10 em verde
- Gráfico de ocupação confirmando 65%
- Previsão temporal mostrando que às 9h a lotação diminui

---

## 2. 🏃 Usuário com Pressa - Rota Mais Rápida

### Cenário:
João está atrasado e precisa ir da Zona Sul até o Centro o mais rápido possível.

### Interação:

```
👤 João: "Melhor rota para Avenida Paulista, rápido!"

🤖 IA: 🎯 Rota mais rápida identificada!

       🏆 Linha 175T-10
       ⏱️ Tempo estimado: 22 minutos
       🚀 Velocidade média: 32 km/h
       📍 Distância: 12.5 km
       
       🚏 Próximo ônibus: 3 minutos
       📊 Lotação prevista: 70% (ainda há espaço)
```

### Usando Otimização de Rotas:
```
Origem: -23.5505, -46.6333
Destino: -23.5605, -46.6433

[Calcular Melhor Rota]

Resultado:
┌────────────────────────────────────────┐
│ 🏆 MELHOR ROTA                         │
├────────────────────────────────────────┤
│ Linha: 175T-10                         │
│ Tempo: 22 min                          │
│ Velocidade: 32 km/h                    │
│ Distância: 12.5 km                     │
└────────────────────────────────────────┘

Alternativas:
2. 701U-10 - 28 min
3. 702U-10 - 31 min
```

---

## 3. 📅 Planejamento Antecipado

### Cenário:
Ana quer planejar sua viagem para evitar horário de pico.

### Interação:

```
👤 Ana: "Previsão de lotação para hoje"

🤖 IA: 📈 Previsão de lotação para hoje (Terça-feira):

       🔵 06h: 45% (OK)
       ⛔ 07h: 85% (LOTADO) ⚠️ Evite!
       ⛔ 08h: 88% (LOTADO) ⚠️ Evite!
       🟡 09h: 72% (CHEIO)
       🟢 10h: 58% (MODERADO)
       🟢 12h: 62% (MODERADO)
       🟢 14h: 55% (MODERADO) ✅ Bom horário
       🟡 17h: 80% (CHEIO) ⚠️
       ⛔ 18h: 82% (LOTADO) ⚠️
       🟢 20h: 50% (OK) ✅ Bom horário
       
       💡 Melhor horário: 14h ou após 20h
```

### No Dashboard:
- Gráfico de linha mostrando curva de lotação
- Destaque visual nos picos (vermelho)
- Linha pontilhada em 85% (capacidade crítica)

---

## 4. 🔍 Consulta de Informações Específicas

### Cenário:
Pedro quer saber detalhes sobre uma linha específica.

### Interação:

```
👤 Pedro: "Me fale sobre a linha 175T-10"

🤖 IA: 🚌 Informações da Linha 175T-10:

       📊 Status Atual:
       ├─ Lotação: 75% (🟡 CHEIO)
       ├─ Velocidade média: 28 km/h
       └─ Tempo de espera: 12-15 min
       
       ⏰ Frequência:
       ├─ Intervalo: A cada 15 minutos
       ├─ Horário de pico: 7h-9h, 17h-19h
       └─ Fora do pico: A cada 20 minutos
       
       🎯 Performance:
       ├─ Taxa de pontualidade: 87%
       ├─ Eficiência: Acima da média
       └─ Velocidade vs esperada: +2 km/h
       
       💡 Dica: É uma das linhas mais rápidas!
```

---

## 5. ❓ Dúvidas sobre Horários de Pico

### Cenário:
Carla é nova na cidade e não sabe os horários de pico.

### Interação:

```
👤 Carla: "Quais são os horários de pico?"

🤖 IA: 🕐 Horários de pico em São Paulo:

       🌅 MANHÃ (7h - 9h)
       ├─ Lotação média: 85%
       ├─ Tempo de espera: +40%
       ├─ Velocidade: -20%
       └─ Status: ⛔ MUITO MOVIMENTADO
       
       🌆 TARDE (17h - 19h)
       ├─ Lotação média: 80%
       ├─ Tempo de espera: +35%
       ├─ Velocidade: -15%
       └─ Status: ⛔ MUITO MOVIMENTADO
       
       🌙 ALMOÇO (12h - 14h)
       ├─ Lotação média: 65%
       ├─ Tempo de espera: +10%
       └─ Status: 🟡 MODERADO
       
       ✅ MELHORES HORÁRIOS:
       • 10h - 11h
       • 14h - 16h
       • Após 20h
```

---

## 6. 🗺️ Primeira Vez na Cidade

### Cenário:
Turista precisa de orientação completa.

### Interação:

```
👤 Turista: "Como funciona o sistema?"

🤖 IA: 🤖 Bem-vindo ao Assistente de Transporte!

       Posso ajudar com:
       
       📊 PREVISÃO DE LOTAÇÃO
       └─ "Qual lotação do ônibus?"
       
       ⏱️ TEMPO DE ESPERA
       └─ "Quanto tempo vou esperar?"
       
       🗺️ MELHORES ROTAS
       └─ "Como chegar na Paulista?"
       
       🚌 LINHAS DISPONÍVEIS
       └─ "Quais linhas passam aqui?"
       
       🚀 VELOCIDADES MÉDIAS
       └─ "Qual a velocidade dos ônibus?"
       
       🕐 HORÁRIOS DE PICO
       └─ "Quando está mais cheio?"
       
       📈 PREVISÕES
       └─ "Previsão para hoje"
```

---

## 7. 📊 Análise de Dashboard - Gestor de Frota

### Cenário:
Gestor da SPTrans quer analisar eficiência.

### Visualização no Dashboard:

```
╔════════════════════════════════════════════════╗
║  ANÁLISE DE EFICIÊNCIA - LINHA 175T-10        ║
╠════════════════════════════════════════════════╣
║                                                ║
║  Velocidade Média vs Esperada:                ║
║  ┌─────────────────────────────────────────┐  ║
║  │ Real: ████████████████░░░░░ 28 km/h     │  ║
║  │ Meta: ████████████████████░ 30 km/h     │  ║
║  └─────────────────────────────────────────┘  ║
║  📉 Gap: -2 km/h (-6.7%)                      ║
║                                                ║
║  Taxa de Ocupação:                             ║
║  ┌─────────────────────────────────────────┐  ║
║  │ 06h: ████░░░░░ 45%                       │  ║
║  │ 08h: ████████████████████ 88% ⚠️         │  ║
║  │ 12h: ███████░░░░ 62%                     │  ║
║  │ 18h: ████████████████░░ 82% ⚠️           │  ║
║  └─────────────────────────────────────────┘  ║
║                                                ║
║  💡 Recomendações:                             ║
║  • Adicionar 2 ônibus às 7h-9h                ║
║  • Redistribuir frota do período 14h-16h      ║
║  • Potencial redução de 22% no tempo          ║
║                                                ║
╚════════════════════════════════════════════════╝
```

---

## 8. 🎯 Integração com Aplicativo

### Cenário:
Desenvolvedores integrando o sistema em app mobile.

### API de Consulta (Exemplo):

```python
# Exemplo de uso da API do sistema

from nlp_chat import ChatbotNLP
import joblib

# Carregar modelo
modelo = joblib.load('dados/modelo_lotacao.pkl')
features = joblib.load('dados/features.pkl')

# Inicializar chatbot
chatbot = ChatbotNLP(modelo_ml=modelo, features=features)

# Fazer consulta
pergunta = "Lotação da linha 175T-10 às 14h"
resposta = chatbot.gerar_resposta(pergunta)

print(resposta)
# Output: 📊 Previsão de lotação: 58% (🟢 MODERADO)
```

---

## 9. 📱 Notificações Automáticas (Futuro)

### Cenário:
Sistema enviando alertas proativos.

```
🔔 ALERTA DE LOTAÇÃO

📍 Sua linha: 175T-10
⏰ Horário: Agora (17:45)
📊 Lotação prevista: 85% (⛔ LOTADO)

💡 Sugestões:
1. Aguarde 20 minutos → 65% (🟢)
2. Use linha alternativa 701U-10 → 70% (🟡)
3. Considere rota alternativa (+10 min)

[Ver Detalhes] [Snooze 10min]
```

---

## 10. 📈 Relatório Gerencial

### Cenário:
Relatório mensal automático.

```
═══════════════════════════════════════════════════
   RELATÓRIO MENSAL - NOVEMBRO 2025
═══════════════════════════════════════════════════

📊 MÉTRICAS PRINCIPAIS:

Tempo Médio de Espera:
├─ Outubro: 18.5 minutos
├─ Novembro: 14.4 minutos
└─ 📉 Redução: 22.2% ✅ Meta atingida!

Taxa de Lotação Média:
├─ Pico manhã: 83% (-5% vs mês anterior)
├─ Pico tarde: 78% (-7% vs mês anterior)
└─ Fora do pico: 52% (estável)

Velocidade Média:
├─ Outubro: 24.8 km/h
├─ Novembro: 27.2 km/h
└─ 📈 Melhoria: 9.7%

🎯 IMPACTO DA OTIMIZAÇÃO:

• 12.500 horas economizadas (passageiros)
• 850 viagens otimizadas por dia
• 94% de satisfação nos horários ajustados
• R$ 45.000 economizados em combustível

💡 RECOMENDAÇÕES:

1. Expandir modelo para linhas 800+
2. Integrar dados climáticos
3. Implementar notificações push
4. A/B test de novos algoritmos

═══════════════════════════════════════════════════
   Gerado automaticamente pelo Sistema IA
═══════════════════════════════════════════════════
```

---

## 🎓 Conclusão

Este sistema demonstra como **Inteligência Artificial** pode transformar o transporte público:

✅ **Machine Learning** - Previsões precisas de demanda  
✅ **NLP** - Interface natural para usuários  
✅ **Otimização** - Redução real de 22% no tempo de espera  
✅ **Tempo Real** - Dados atualizados continuamente  
✅ **Escalável** - Pronto para expansão  

---

**💡 Dica:** Execute `python teste_sistema.py` para verificar se tudo está funcionando!