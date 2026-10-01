"""Caso de uso: consultar el estado completo de las colas."""

from __future__ import annotations

from ...domain.plan import Planificador
from ...domain.ports import ColaTurnosPort
from ..dtos import EstadoDeColasDTO


class ConsultarEstadoDeColas:
    """Devuelve las tres colas con sus usuarios, los totales y el ciclo."""

    def __init__(self, colas: ColaTurnosPort, planificador: Planificador) -> None:
        self._colas = colas
        self._planificador = planificador

    def execute(self) -> EstadoDeColasDTO:
        estado = self._colas.instantanea()
        return EstadoDeColasDTO.desde_dominio(
            estado,
            pesos=self._planificador.pesos,
            longitud_ciclo=self._planificador.longitud_ciclo,
        )