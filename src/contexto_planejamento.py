"""
Módulo responsável por carregar o contexto oficial de planejamento urbano
e oferecer utilitários para enriquecer os dados coletados pelo sistema.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import date, datetime, time
from functools import lru_cache
from typing import Dict, List, Optional


BASE_PATH = os.path.dirname(os.path.dirname(__file__))
JSON_PATH = os.path.join(BASE_PATH, "dados", "contexto_planejamento.json")

DIAS_SEMANA = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
MESES = [
    "Janeiro",
    "Fevereiro",
    "Março",
    "Abril",
    "Maio",
    "Junho",
    "Julho",
    "Agosto",
    "Setembro",
    "Outubro",
    "Novembro",
    "Dezembro",
]


def _hora_para_time(valor: str) -> time:
    horas, minutos = [int(part) for part in valor.split(":")]
    return time(hour=horas, minute=minutos)


def _extrair_datas_intervalo(intervalo: str) -> Optional[tuple[date, date]]:
    partes = [parte.strip() for parte in intervalo.split("a")]
    if len(partes) != 2:
        return None

    try:
        inicio = datetime.fromisoformat(partes[0]).date()
        fim = datetime.fromisoformat(partes[1]).date()
    except ValueError:
        return None

    return inicio, fim


@dataclass
class ResultadoFeriado:
    nome: str
    tipo: str
    categoria: str


class ContextoPlanejamento:
    """
    Carrega o JSON de contexto e oferece métodos de consulta
    para diferentes componentes do sistema.
    """

    def __init__(self):
        self._dados = self._carregar_json()
        self._periodos_pico = [
            {
                **periodo,
                "start_time": _hora_para_time(periodo["start"]),
                "end_time": _hora_para_time(periodo["end"]),
            }
            for periodo in self._dados.get("peak_hours", {}).get("periods", [])
        ]
        self._rodizio = self._dados.get("traffic_restriction", {})
        self._rodizio_horarios = [
            (
                _hora_para_time(intervalo["start"]),
                _hora_para_time(intervalo["end"]),
            )
            for intervalo in self._rodizio.get("restricted_times", [])
        ]

    @staticmethod
    def _carregar_json() -> Dict:
        if not os.path.exists(JSON_PATH):
            raise FileNotFoundError(
                f"Arquivo de contexto não encontrado em '{JSON_PATH}'."
            )

        with open(JSON_PATH, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)

    @classmethod
    @lru_cache(maxsize=1)
    def obter(cls) -> "ContextoPlanejamento":
        """Retorna instância singleton."""
        return cls()

    def periodo_pico(self, momento: datetime) -> Optional[Dict]:
        """Retorna o período de pico correspondente ao horário informado."""
        hora_atual = momento.time()
        for periodo in self._periodos_pico:
            if periodo["start_time"] <= hora_atual <= periodo["end_time"]:
                return periodo
        return None

    def rodizio_ativo(self, momento: datetime) -> bool:
        """Indica se o rodízio está ativo para o horário e dia."""
        dia_semana_nome = DIAS_SEMANA[momento.weekday()]
        dias_validos = self._rodizio.get("days", [])
        if dia_semana_nome not in dias_validos:
            return False

        hora_atual = momento.time()
        for inicio, fim in self._rodizio_horarios:
            if inicio <= hora_atual <= fim:
                return True
        return False

    def feriado_no_dia(self, momento: datetime) -> Optional[ResultadoFeriado]:
        """Retorna informações de feriado/ponto facultativo."""
        data_iso = momento.date().isoformat()
        feriados = self._dados.get("holidays", {})

        for categoria, itens in feriados.items():
            for feriado in itens:
                if feriado["date"] == data_iso:
                    return ResultadoFeriado(
                        nome=feriado["name"],
                        tipo=feriado["type"],
                        categoria=categoria,
                    )
        return None

    def eventos_do_dia(self, momento: datetime) -> List[str]:
        """Lista eventos relevantes previstos para o dia."""
        eventos: List[str] = []
        recorrentes = self._dados.get("recurring_events", {}).get("events", [])
        dia_semana_nome = DIAS_SEMANA[momento.weekday()]
        data_iso = momento.date().isoformat()
        mes_nome = MESES[momento.month - 1]

        for evento in recorrentes:
            dias = evento.get("days", [])
            meses = evento.get("typical_months", [])

            if dias and dia_semana_nome not in dias:
                continue

            if meses and mes_nome not in meses:
                continue

            intervalo = evento.get("dates") or evento.get("next_dates")
            if intervalo:
                faixa = _extrair_datas_intervalo(intervalo)
                if faixa and not (faixa[0] <= momento.date() <= faixa[1]):
                    continue

            eventos.append(evento["name"])

        return eventos

    def resumo_diario(self, momento: datetime) -> Dict:
        """Retorna um resumo consolidado para uso no dashboard/chat."""
        periodo = self.periodo_pico(momento)
        feriado = self.feriado_no_dia(momento)
        eventos = self.eventos_do_dia(momento)

        return {
            "periodo_pico": periodo["period"] if periodo else None,
            "descricao_pico": periodo["description"] if periodo else None,
            "rodizio_ativo": self.rodizio_ativo(momento),
            "feriado": {
                "nome": feriado.nome,
                "tipo": feriado.tipo,
                "categoria": feriado.categoria,
            }
            if feriado
            else None,
            "eventos": eventos,
        }


def obter_resumo_contexto(momento: Optional[datetime] = None) -> Dict:
    instante = momento or datetime.now()
    return ContextoPlanejamento.obter().resumo_diario(instante)
