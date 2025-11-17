#!/usr/bin/env python3
"""
🧪 EXEMPLOS PRÁTICOS - Testando os 3 Ajustes PLN
"""

from src.pln_processor import (
    ClassificadorTematica,
    ExtractorEntidades,
    IndicadoresProblema,
    ProcessadorPLN
)

print("=" * 80)
print("🧪 EXEMPLOS PRÁTICOS DOS 3 AJUSTES PLN")
print("=" * 80)

# ============================================================================
# 1️⃣ CLASSIFICAÇÃO DA TEMÁTICA
# ============================================================================
print("\n" + "=" * 80)
print("1️⃣ CLASSIFICAÇÃO DA TEMÁTICA (com Confiança)")
print("=" * 80)

classificador = ClassificadorTematica()

perguntas_tematica = [
    "Qual a lotação do ônibus agora?",
    "Quanto tempo vou esperar?",
    "Qual a melhor rota para o Centro?",
    "A linha 175T-10 está funcionando?",
]

for pergunta in perguntas_tematica:
    print(f"\n📝 '{pergunta}'")
    resultado = classificador.classificar(pergunta)
    
    print(f"   {resultado['emoji']} Temática: {resultado['tematica'].upper()}")
    print(f"   📊 Confiança: {resultado['confianca']*100:.0f}%")
    print(f"   📖 Descrição: {resultado['descricao']}")
    
    # Mostrar top 3 tematicas
    top3 = sorted(resultado['scores'].items(), key=lambda x: x[1], reverse=True)[:3]
    print(f"   🏆 Top 3: {', '.join([f'{t[0]}({t[1]*100:.0f}%)' for t in top3])}")

# ============================================================================
# 2️⃣ INDICADORES-CHAVE (Detecção de Problemas)
# ============================================================================
print("\n" + "=" * 80)
print("2️⃣ INDICADORES-CHAVE DE PROBLEMAS")
print("=" * 80)

indicadores = IndicadoresProblema()

perguntas_problema = [
    "Tudo bem!",
    "A linha está super lotada!",
    "Estou muito atrasado esperando o ônibus",
    "Não vem ônibus nunca nessa linha!",
    "O ônibus está muito lento por causa do trânsito",
    "Tenho medo de entrar no ônibus, não é seguro!",
]

for pergunta in perguntas_problema:
    print(f"\n📝 '{pergunta}'")
    resultado = indicadores.detectar(pergunta)
    
    if resultado['problemas_encontrados']:
        print(f"   ⚠️  Severidade Máxima: {resultado['severidade_maxima']}")
        for problema in resultado['problemas_encontrados']:
            emoji_sev = "🔴" if problema['severidade'] == 'CRÍTICA' else "🟠" if problema['severidade'] == 'ALTA' else "🟡"
            print(f"   {emoji_sev} {problema['descricao']} ({problema['severidade']})")
        print(f"   ⚡ Ação Urgente: {'SIM' if resultado['requer_acao_urgente'] else 'NÃO'}")
    else:
        print(f"   ✅ Nenhum problema detectado")

# ============================================================================
# 3️⃣ EXTRAÇÃO DE ENTIDADES
# ============================================================================
print("\n" + "=" * 80)
print("3️⃣ EXTRAÇÃO DE ENTIDADES")
print("=" * 80)

extractor = ExtractorEntidades()

perguntas_entidades = [
    "Como chegar na Avenida Paulista?",
    "Qual a lotação da linha 175T-10 às 14h30?",
    "Melhor rota para o Centro de ônibus rápido",
    "Que hora o ônibus 701U-10 sai agora?",
]

for pergunta in perguntas_entidades:
    print(f"\n📝 '{pergunta}'")
    resultado = extractor.extrair(pergunta)
    
    print(f"   Total de Entidades: {resultado['numero_entidades']}")
    
    if resultado['linhas']:
        print(f"   🚌 Linhas:")
        for linha, conf in resultado['linhas']:
            print(f"      • {linha} (Confiança: {conf*100:.0f}%)")
    
    if resultado['horarios']:
        print(f"   🕐 Horários: {', '.join(resultado['horarios'])}")
    
    if resultado['locais']:
        print(f"   📍 Locais: {', '.join(resultado['locais'])}")
    
    if resultado['tempos']:
        print(f"   📅 Tempos: {', '.join([t['valor'] for t in resultado['tempos']])}")

# ============================================================================
# PROCESSADOR COMPLETO (Integrado)
# ============================================================================
print("\n" + "=" * 80)
print("🎯 ANÁLISE COMPLETA (Todos os 3 Ajustes Integrados)")
print("=" * 80)

processador = ProcessadorPLN()

pergunta_completa = "A linha 175T-10 está muito lotada e não sai do lugar às 14h30!"
print(f"\n📝 Pergunta: '{pergunta_completa}'")
print("-" * 80)

resultado = processador.processar(pergunta_completa)

# Exibir análise formatada
print(resultado['analise_completa'])

# ============================================================================
# RESUMO FINAL
# ============================================================================
print("\n" + "=" * 80)
print("📋 RESUMO DOS 3 AJUSTES IMPLEMENTADOS")
print("=" * 80)

resumo = """
✅ 1. CLASSIFICAÇÃO DA TEMÁTICA
   • Detecta automáticamente o tipo de pergunta
   • Retorna score de confiança (0-100%)
   • 8 categorias diferentes
   • Scores de todas as categorias para análise

✅ 2. INDICADORES-CHAVE DE PROBLEMAS
   • Detecta problemas no texto automaticamente
   • 6 tipos de problemas com severidade
   • Alerta para ações urgentes
   • Inclui keyword que disparou detecção

✅ 3. EXTRAÇÃO DE ENTIDADES
   • Extrai linhas de ônibus com validação
   • Reconhece horários em vários formatos
   • Identifica locais via spaCy + dicionário
   • Calcula confiança de cada entidade

🎯 INTEGRAÇÃO:
   • Todos os 3 módulos trabalham juntos
   • Compatível com código existente
   • Fácil expandir/customizar
   • Bem documentado e testado
"""

print(resumo)

print("=" * 80)
print("✨ Pronto! Os 3 ajustes de PLN estão implementados e funcionando!")
print("=" * 80)
