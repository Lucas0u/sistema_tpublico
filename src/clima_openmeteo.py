"""
Módulo para integração com API Open-Meteo
Fornece dados climáticos de São Paulo para o sistema de transporte
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import json
import os


class ClimaOpenMeteo:
    """Classe singleton para buscar dados climáticos via Open-Meteo API"""
    
    _instancia = None
    
    # Coordenadas de São Paulo
    LATITUDE_SP = -23.5505
    LONGITUDE_SP = -46.6333
    
    # URL base da API
    BASE_URL = "https://api.open-meteo.com/v1/forecast"
    
    def __init__(self):
        """Inicializa o cliente Open-Meteo"""
        self.cache = {}
        self.cache_timestamp = None
        self.cache_ttl = 3600  # Cache por 1 hora
    
    @classmethod
    def obter(cls):
        """Retorna instância singleton"""
        if cls._instancia is None:
            cls._instancia = cls()
        return cls._instancia
    
    def _fazer_requisicao(self, params: Dict) -> Optional[Dict]:
        """Faz requisição à API Open-Meteo"""
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"⚠️ Erro na API Open-Meteo: {response.status_code}")
                return None
        except Exception as e:
            print(f"⚠️ Erro ao buscar dados climáticos: {e}")
            return None
    
    def obter_clima_atual(self) -> Optional[Dict]:
        """
        Obtém dados climáticos atuais de São Paulo
        
        Returns:
            Dict com temperatura, umidade, precipitação, etc.
        """
        # Verificar cache
        agora = datetime.now()
        if (self.cache_timestamp and 
            (agora - self.cache_timestamp).total_seconds() < self.cache_ttl and
            'atual' in self.cache):
            return self.cache['atual']
        
        params = {
            'latitude': self.LATITUDE_SP,
            'longitude': self.LONGITUDE_SP,
            'current': 'temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m',
            'timezone': 'America/Sao_Paulo',
            'forecast_days': 1
        }
        
        dados = self._fazer_requisicao(params)
        if dados and 'current' in dados:
            resultado = {
                'temperatura': dados['current'].get('temperature_2m', None),
                'umidade': dados['current'].get('relative_humidity_2m', None),
                'precipitacao': dados['current'].get('precipitation', None),
                'codigo_clima': dados['current'].get('weather_code', None),
                'velocidade_vento': dados['current'].get('wind_speed_10m', None),
                'timestamp': dados['current'].get('time', None)
            }
            
            # Atualizar cache
            self.cache['atual'] = resultado
            self.cache_timestamp = agora
            
            return resultado
        
        return None
    
    def obter_previsao_horaria(self, horas: int = 24) -> Optional[Dict]:
        """
        Obtém previsão horária para as próximas N horas
        
        Args:
            horas: Número de horas para prever (máximo 168)
        
        Returns:
            Dict com arrays de dados horários
        """
        params = {
            'latitude': self.LATITUDE_SP,
            'longitude': self.LONGITUDE_SP,
            'hourly': 'temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m',
            'timezone': 'America/Sao_Paulo',
            'forecast_days': min(7, (horas // 24) + 1)
        }
        
        dados = self._fazer_requisicao(params)
        if dados and 'hourly' in dados:
            # Limitar ao número de horas solicitado
            resultado = {
                'horarios': dados['hourly']['time'][:horas],
                'temperaturas': dados['hourly']['temperature_2m'][:horas],
                'umidades': dados['hourly']['relative_humidity_2m'][:horas],
                'precipitacoes': dados['hourly']['precipitation'][:horas],
                'codigos_clima': dados['hourly']['weather_code'][:horas],
                'velocidades_vento': dados['hourly']['wind_speed_10m'][:horas]
            }
            return resultado
        
        return None
    
    def obter_clima_para_timestamp(self, timestamp: datetime) -> Optional[Dict]:
        """
        Obtém dados climáticos para um timestamp específico
        Usa previsão horária e encontra o horário mais próximo
        
        Args:
            timestamp: Data/hora desejada
        
        Returns:
            Dict com dados climáticos do horário mais próximo
        """
        # Se for no passado ou muito distante, usar dados atuais
        agora = datetime.now()
        diferenca = (timestamp - agora).total_seconds()
        
        if diferenca < -3600:  # Mais de 1 hora no passado
            return self.obter_clima_atual()
        
        if diferenca > 168 * 3600:  # Mais de 7 dias no futuro
            return self.obter_clima_atual()
        
        # Buscar previsão horária
        horas_futuro = int(diferenca / 3600) + 1
        previsao = self.obter_previsao_horaria(horas=min(168, horas_futuro + 1))
        
        if previsao and previsao['horarios']:
            # Encontrar horário mais próximo
            timestamp_str = timestamp.strftime('%Y-%m-%dT%H:00')
            
            try:
                idx = previsao['horarios'].index(timestamp_str)
                return {
                    'temperatura': previsao['temperaturas'][idx],
                    'umidade': previsao['umidades'][idx],
                    'precipitacao': previsao['precipitacoes'][idx],
                    'codigo_clima': previsao['codigos_clima'][idx],
                    'velocidade_vento': previsao['velocidades_vento'][idx],
                    'timestamp': timestamp_str
                }
            except ValueError:
                # Se não encontrar exato, usar o primeiro disponível
                return {
                    'temperatura': previsao['temperaturas'][0],
                    'umidade': previsao['umidades'][0],
                    'precipitacao': previsao['precipitacoes'][0],
                    'codigo_clima': previsao['codigos_clima'][0],
                    'velocidade_vento': previsao['velocidades_vento'][0],
                    'timestamp': previsao['horarios'][0]
                }
        
        return self.obter_clima_atual()
    
    def interpretar_codigo_clima(self, codigo: int) -> Dict[str, str]:
        """
        Interpreta código WMO Weather Interpretation Codes
        
        Returns:
            Dict com descrição e emoji do clima
        """
        codigos = {
            0: {'descricao': 'Céu limpo', 'emoji': '☀️'},
            1: {'descricao': 'Principalmente limpo', 'emoji': '🌤️'},
            2: {'descricao': 'Parcialmente nublado', 'emoji': '⛅'},
            3: {'descricao': 'Nublado', 'emoji': '☁️'},
            45: {'descricao': 'Neblina', 'emoji': '🌫️'},
            48: {'descricao': 'Neblina depositada', 'emoji': '🌫️'},
            51: {'descricao': 'Chuva leve', 'emoji': '🌦️'},
            53: {'descricao': 'Chuva moderada', 'emoji': '🌧️'},
            55: {'descricao': 'Chuva forte', 'emoji': '🌧️'},
            56: {'descricao': 'Chuva congelante leve', 'emoji': '🌨️'},
            57: {'descricao': 'Chuva congelante forte', 'emoji': '🌨️'},
            61: {'descricao': 'Chuva leve', 'emoji': '🌦️'},
            63: {'descricao': 'Chuva moderada', 'emoji': '🌧️'},
            65: {'descricao': 'Chuva forte', 'emoji': '⛈️'},
            66: {'descricao': 'Chuva congelante leve', 'emoji': '🌨️'},
            67: {'descricao': 'Chuva congelante forte', 'emoji': '🌨️'},
            71: {'descricao': 'Queda de neve leve', 'emoji': '❄️'},
            73: {'descricao': 'Queda de neve moderada', 'emoji': '❄️'},
            75: {'descricao': 'Queda de neve forte', 'emoji': '❄️'},
            77: {'descricao': 'Grãos de neve', 'emoji': '❄️'},
            80: {'descricao': 'Chuva leve', 'emoji': '🌦️'},
            81: {'descricao': 'Chuva moderada', 'emoji': '🌧️'},
            82: {'descricao': 'Chuva forte', 'emoji': '⛈️'},
            85: {'descricao': 'Queda de neve leve', 'emoji': '❄️'},
            86: {'descricao': 'Queda de neve forte', 'emoji': '❄️'},
            95: {'descricao': 'Trovoada', 'emoji': '⛈️'},
            96: {'descricao': 'Trovoada com granizo', 'emoji': '⛈️'},
            99: {'descricao': 'Trovoada com granizo forte', 'emoji': '⛈️'}
        }
        
        return codigos.get(codigo, {'descricao': 'Desconhecido', 'emoji': '❓'})


def obter_resumo_clima() -> Dict:
    """
    Função helper para obter resumo climático atual
    
    Returns:
        Dict com informações climáticas formatadas
    """
    clima = ClimaOpenMeteo.obter()
    dados = clima.obter_clima_atual()
    
    if not dados:
        return {
            'disponivel': False,
            'mensagem': 'Dados climáticos temporariamente indisponíveis'
        }
    
    interpretacao = clima.interpretar_codigo_clima(dados.get('codigo_clima', 0))
    
    return {
        'disponivel': True,
        'temperatura': dados.get('temperatura'),
        'umidade': dados.get('umidade'),
        'precipitacao': dados.get('precipitacao', 0),
        'velocidade_vento': dados.get('velocidade_vento'),
        'descricao': interpretacao['descricao'],
        'emoji': interpretacao['emoji'],
        'codigo_clima': dados.get('codigo_clima'),
        'timestamp': dados.get('timestamp')
    }


if __name__ == "__main__":
    """Teste do módulo"""
    print("🌤️ TESTE DO MÓDULO CLIMA OPEN-METEO")
    print("=" * 60)
    
    clima = ClimaOpenMeteo.obter()
    
    # Teste 1: Clima atual
    print("\n1️⃣ Clima Atual:")
    atual = clima.obter_clima_atual()
    if atual:
        print(f"   🌡️ Temperatura: {atual.get('temperatura')}°C")
        print(f"   💧 Umidade: {atual.get('umidade')}%")
        print(f"   🌧️ Precipitação: {atual.get('precipitacao', 0)}mm")
        print(f"   💨 Vento: {atual.get('velocidade_vento')} km/h")
        
        interpretacao = clima.interpretar_codigo_clima(atual.get('codigo_clima', 0))
        print(f"   {interpretacao['emoji']} {interpretacao['descricao']}")
    else:
        print("   ❌ Erro ao obter dados")
    
    # Teste 2: Resumo
    print("\n2️⃣ Resumo Climático:")
    resumo = obter_resumo_clima()
    if resumo.get('disponivel'):
        print(f"   {resumo['emoji']} {resumo['descricao']}")
        print(f"   🌡️ {resumo['temperatura']}°C | 💧 {resumo['umidade']}%")
        if resumo['precipitacao'] > 0:
            print(f"   🌧️ Precipitação: {resumo['precipitacao']}mm")
    else:
        print(f"   {resumo['mensagem']}")
