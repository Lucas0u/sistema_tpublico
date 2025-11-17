"""
Módulo de Processamento de Linguagem Natural (PLN) Avançado
Implementa:
- Classificação de Temática
- Indicadores-chave de Problemas
- Extração de Entidades
"""

import re
import spacy
from typing import Dict, List, Tuple
from datetime import datetime

# Carregar modelo spaCy em português
try:
    nlp = spacy.load("pt_core_news_sm")
except OSError:
    print("⚠️ Modelo spaCy não encontrado. Execute: python -m spacy download pt_core_news_sm")
    nlp = None


class ClassificadorTematica:
    """Classifica a temática da pergunta com score de confiança"""
    
    def __init__(self):
        self.tematicas = {
            'lotacao': {
                'keywords': ['lotação', 'cheio', 'vazio', 'ocupação', 'lotado', 'passageiros', 'apertado', 'aglomerado'],
                'descricao': 'Previsão de ocupação/densidade de ônibus',
                'emoji': '📊'
            },
            'tempo_espera': {
                'keywords': ['tempo', 'espera', 'demora', 'aguardar', 'quanto tempo', 'esperando', 'demoreî', 'demore'],
                'descricao': 'Tempo de espera nas paradas',
                'emoji': '⏱️'
            },
            'rota': {
                'keywords': ['rota', 'caminho', 'trajeto', 'melhor', 'como chegar', 'ir para', 'itinerário', 'camino'],
                'descricao': 'Otimização de rotas/caminhos',
                'emoji': '🗺️'
            },
            'linha': {
                'keywords': ['linha', 'ônibus', 'qual ônibus', 'número', 'linhas', 'ônibús', 'onibus'],
                'descricao': 'Informações sobre linhas de transporte',
                'emoji': '🚌'
            },
            'velocidade': {
                'keywords': ['velocidade', 'rápido', 'devagar', 'lento', 'km/h', 'velocidade', 'rápida'],
                'descricao': 'Análise de velocidade/performance',
                'emoji': '🚀'
            },
            'horario_pico': {
                'keywords': ['horário', 'pico', 'movimentado', 'rush', 'hora do rush', 'horarios', 'horários'],
                'descricao': 'Informações sobre horários críticos',
                'emoji': '🕐'
            },
            'previsao': {
                'keywords': ['previsão', 'prever', 'futuro', 'próximas', 'vai estar', 'amanhã', 'semana'],
                'descricao': 'Previsões futuras de demanda',
                'emoji': '📈'
            },
            'problema_tecnico': {
                'keywords': ['erro', 'bug', 'não funciona', 'quebrado', 'falha', 'problema', 'defeito'],
                'descricao': 'Relato de problemas técnicos',
                'emoji': '⚠️'
            }
        }
    
    def classificar(self, texto: str) -> Dict:
        """
        Classifica a temática com score de confiança
        
        Returns:
            {
                'tematica': str,
                'confianca': float (0-1),
                'descricao': str,
                'emoji': str,
                'scores': Dict (todas as tematicas com scores)
            }
        """
        texto_lower = texto.lower()
        scores = {}
        
        # Calcular score para cada temática
        for tema, info in self.tematicas.items():
            # Contar matches de palavras-chave
            matches = sum(1 for kw in info['keywords'] if kw in texto_lower)
            # Calcular score normalizado (0-1)
            score = min(matches / len(info['keywords']), 1.0) if info['keywords'] else 0
            scores[tema] = score
        
        # Encontrar melhor temática
        if max(scores.values()) > 0:
            melhor_tema = max(scores, key=scores.get)
            confianca = scores[melhor_tema]
        else:
            melhor_tema = 'ajuda'
            confianca = 0.0
            scores['ajuda'] = 0.0
        
        return {
            'tematica': melhor_tema,
            'confianca': confianca,
            'descricao': self.tematicas.get(melhor_tema, {}).get('descricao', 'Consulta geral'),
            'emoji': self.tematicas.get(melhor_tema, {}).get('emoji', '❓'),
            'scores': scores
        }


class ExtractorEntidades:
    """Extrai entidades do texto com validação"""
    
    def __init__(self):
        # Linhas conhecidas de São Paulo (SPTrans)
        self.linhas_conhecidas = {
            '175T-10': 'Linha expressinha',
            '701U-10': 'Linha circular',
            '702U-10': 'Linha radial',
            '877T-10': 'Linha noturna',
            '501U-10': 'Linha tronco'
        }
        
        # Locais importantes
        self.locais_conhecidos = [
            'Avenida Paulista', 'Centro', 'Zona Sul', 'Zona Norte',
            'Zona Leste', 'Zona Oeste', 'Itaim', 'Pinheiros',
            'Vila Mariana', 'Consolação'
        ]
        
        # Padrões de tempo
        self.padroes_tempo = [
            (r'\b(\d{1,2})[:h](\d{2})?\b', 'horario'),  # 14:30, 14h30, 14h
            (r'\b(hoje|amanhã|amanha)\b', 'dia_relativo'),
            (r'\b(segunda|terça|terca|quarta|quinta|sexta|sábado|sabado|domingo)\b', 'dia_semana'),
            (r'\b(manhã|manha|tarde|noite)\b', 'periodo_dia')
        ]
    
    def extrair(self, texto: str) -> Dict:
        """
        Extrai todas as entidades do texto
        
        Returns:
            {
                'linhas': List[Tuple(linha, confianca)],
                'horarios': List[str],
                'locais': List[str],
                'tempos': List[Dict],
                'numero_entidades': int
            }
        """
        entidades = {
            'linhas': [],
            'horarios': [],
            'locais': [],
            'tempos': [],
            'numero_entidades': 0
        }
        
        texto_lower = texto.lower()
        
        # === EXTRAÇÃO DE LINHAS ===
        for linha in self.linhas_conhecidas.keys():
            if linha.lower() in texto_lower:
                confianca = 0.95  # Alto porque é match exato
                entidades['linhas'].append((linha, confianca))
        
        # Buscar padrões de linha (números com traço)
        padrao_linha = r'\b(\d{3}[A-Za-z])-(\d{2})\b'
        matches_linha = re.findall(padrao_linha, texto)
        for match in matches_linha:
            linha_possivel = f"{match[0]}-{match[1]}"
            if linha_possivel not in [l[0] for l in entidades['linhas']]:
                confianca = 0.70  # Moderada porque é inferência
                entidades['linhas'].append((linha_possivel, confianca))
        
        # === EXTRAÇÃO DE HORÁRIOS ===
        for padrao, tipo in self.padroes_tempo:
            if tipo == 'horario':
                matches = re.findall(padrao, texto)
                for h, m in matches:
                    if int(h) < 24:
                        horario = f"{h}:{m if m else '00'}"
                        if horario not in entidades['horarios']:
                            entidades['horarios'].append(horario)
        
        # === EXTRAÇÃO DE LOCAIS ===
        # Buscar locais conhecidos
        for local in self.locais_conhecidos:
            if local.lower() in texto_lower:
                if local not in entidades['locais']:
                    entidades['locais'].append(local)
        
        # Usar spaCy para extrair locais (Named Entity Recognition)
        if nlp:
            doc = nlp(texto)
            for ent in doc.ents:
                if ent.label_ in ['LOC', 'GPE']:
                    if ent.text not in entidades['locais']:
                        entidades['locais'].append(ent.text)
        
        # === EXTRAÇÃO DE PERÍODOS ===
        for padrao, tipo in self.padroes_tempo:
            if tipo in ['dia_relativo', 'periodo_dia']:
                matches = re.findall(padrao, texto)
                for match in matches:
                    entidades['tempos'].append({
                        'valor': match,
                        'tipo': tipo
                    })
        
        # Contar total de entidades
        entidades['numero_entidades'] = (
            len(entidades['linhas']) +
            len(entidades['horarios']) +
            len(entidades['locais']) +
            len(entidades['tempos'])
        )
        
        return entidades


class IndicadoresProblema:
    """Identifica indicadores-chave de problemas no texto"""
    
    def __init__(self):
        self.indicadores = {
            'lotacao_critica': {
                'keywords': ['lotado', 'super lotado', 'apertado', 'impossível entrar', 'cheio demais'],
                'problema': 'Lotação acima da capacidade segura',
                'severidade': 'CRÍTICA'
            },
            'atraso_excessivo': {
                'keywords': ['muito atraso', 'atrasado', 'demorando muito', 'nunca chega'],
                'problema': 'Atraso além do esperado',
                'severidade': 'ALTA'
            },
            'velocidade_baixa': {
                'keywords': ['muito lento', 'devagar demais', 'engarrafado', 'trânsito'],
                'problema': 'Velocidade abaixo do esperado',
                'severidade': 'MÉDIA'
            },
            'indisponibilidade': {
                'keywords': ['não passa', 'sem ônibus', 'sumiu', 'desapareceu', 'faltando'],
                'problema': 'Linha ou ônibus indisponível',
                'severidade': 'ALTA'
            },
            'inseguranca': {
                'keywords': ['inseguro', 'perigoso', 'assalto', 'roubo', 'medo'],
                'problema': 'Questão de segurança do passageiro',
                'severidade': 'CRÍTICA'
            },
            'conforto_precario': {
                'keywords': ['incômodo', 'desconfortável', 'quebrado', 'sujo', 'barulhento'],
                'problema': 'Problema de conforto/manutenção',
                'severidade': 'MÉDIA'
            }
        }
    
    def detectar(self, texto: str) -> Dict:
        """
        Detecta problemas no texto
        
        Returns:
            {
                'problemas_encontrados': List[Dict],
                'severidade_maxima': str,
                'requer_acao_urgente': bool
            }
        """
        texto_lower = texto.lower()
        problemas_encontrados = []
        
        # Verificar cada indicador
        for indicador, info in self.indicadores.items():
            for keyword in info['keywords']:
                if keyword in texto_lower:
                    problema = {
                        'tipo': indicador,
                        'descricao': info['problema'],
                        'severidade': info['severidade'],
                        'keyword_match': keyword
                    }
                    if problema not in problemas_encontrados:
                        problemas_encontrados.append(problema)
                    break  # Já encontrou este indicador
        
        # Determinar severidade máxima
        severidades = {'CRÍTICA': 3, 'ALTA': 2, 'MÉDIA': 1}
        if problemas_encontrados:
            severidade_maxima = max(
                [p['severidade'] for p in problemas_encontrados],
                key=lambda x: severidades.get(x, 0)
            )
        else:
            severidade_maxima = 'NENHUMA'
        
        return {
            'problemas_encontrados': problemas_encontrados,
            'severidade_maxima': severidade_maxima,
            'requer_acao_urgente': severidade_maxima in ['CRÍTICA', 'ALTA']
        }


class ProcessadorPLN:
    """Classe principal que integra todos os módulos PLN"""
    
    def __init__(self):
        self.classificador = ClassificadorTematica()
        self.extractor = ExtractorEntidades()
        self.indicadores = IndicadoresProblema()
    
    def processar(self, texto: str) -> Dict:
        """
        Processa texto com análise completa PLN
        
        Returns:
            {
                'texto_original': str,
                'classificacao': Dict,
                'entidades': Dict,
                'problemas': Dict,
                'analise_completa': str
            }
        """
        resultado = {
            'texto_original': texto,
            'classificacao': self.classificador.classificar(texto),
            'entidades': self.extractor.extrair(texto),
            'problemas': self.indicadores.detectar(texto)
        }
        
        # Gerar análise textual completa
        resultado['analise_completa'] = self._gerar_analise_textual(resultado)
        
        return resultado
    
    def _gerar_analise_textual(self, resultado: Dict) -> str:
        """Gera texto formatado com análise completa"""
        texto = []
        
        # Cabeçalho
        classif = resultado['classificacao']
        texto.append(f"{classif['emoji']} **ANÁLISE PLN**")
        texto.append(f"Temática: {classif['tematica'].upper()}")
        texto.append(f"Confiança: {classif['confianca']*100:.0f}%")
        
        # Entidades
        ent = resultado['entidades']
        if ent['numero_entidades'] > 0:
            texto.append(f"\n🔍 **ENTIDADES ENCONTRADAS ({ent['numero_entidades']})**")
            if ent['linhas']:
                texto.append(f"  • Linhas: {', '.join([f'{l[0]} ({l[1]*100:.0f}%)' for l in ent['linhas']])}")
            if ent['horarios']:
                texto.append(f"  • Horários: {', '.join(ent['horarios'])}")
            if ent['locais']:
                texto.append(f"  • Locais: {', '.join(ent['locais'])}")
        
        # Problemas
        prob = resultado['problemas']
        if prob['problemas_encontrados']:
            texto.append(f"\n⚠️ **PROBLEMAS DETECTADOS**")
            texto.append(f"Severidade: {prob['severidade_maxima']}")
            for p in prob['problemas_encontrados']:
                emoji = '🔴' if p['severidade'] == 'CRÍTICA' else '🟠' if p['severidade'] == 'ALTA' else '🟡'
                texto.append(f"  {emoji} {p['descricao']} ({p['severidade']})")
        else:
            texto.append(f"\n✅ Nenhum problema detectado")
        
        return "\n".join(texto)


# ============ TESTES ============

def testar_processador_pln():
    """Testa o processador PLN completo"""
    processador = ProcessadorPLN()
    
    # Perguntas de teste
    testes = [
        "Qual a lotação do ônibus 175T-10 agora?",
        "Quanto tempo vou esperar?",
        "Como chegar na Avenida Paulista às 14h30?",
        "A linha está muito lotada e atrasada!",
        "Qual a velocidade média hoje?",
        "Preciso de uma linha rápida para o Centro"
    ]
    
    print("=" * 70)
    print("🧪 TESTE DO PROCESSADOR PLN COMPLETO")
    print("=" * 70)
    
    for pergunta in testes:
        print(f"\n📝 Pergunta: '{pergunta}'")
        print("-" * 70)
        
        resultado = processador.processar(pergunta)
        print(resultado['analise_completa'])
        print()


if __name__ == "__main__":
    testar_processador_pln()
