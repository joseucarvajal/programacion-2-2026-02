"""Caso de uso: consultar como esta configurada la rotacion.

Sirve para que el frontend muestre la secuencia de turnos sin tener que
calcularla, y para verificar en clase que el ponderado (3, 2, 1) genera el
ciclo (deudas, deudas, deudas, contado, contado, credito).
"""

from __future__ import annotations

from ...domain.plan import Planificador
from ...domain.ports import ColaTurnosPort
from ..dtos import ConfiguracionRotacionDTO


class ConsultarConfiguracionRotacion:
    """Expone la politica, los pesos, el ciclo y la posicion actual."""

    def __init__(self, colas: ColaTurnosPort, planificador: Planificador) -> None:
        self._colas = colas
        self._planificador = planificador

    def execute(self) -> ConfiguracionRotacionDTO:
        pesos = self._planificador.pesos
        return ConfiguracionRotacionDTO(
            politica=self._planificador.nombre,
            pesos=tuple(sorted(pesos.items(), key=lambda par: int(par[0]))),
            ciclo=self._planificador.ciclo,
            longitud_ciclo=self._planificador.longitud_ciclo,
            # Se normaliza con el largo del ciclo: si alguien reconfigura los
            # pesos en caliente, la posicion guardada puede quedar fuera de rango.
            posicion_ciclo=self._colas.posicion_ciclo(self._planificador.longitud_ciclo),
        )