"""Caso de uso: atender el siguiente usuario aplicando el turno del ciclo.

Este es el corazon del Round Robin. Compara con ``v82`` (prioridad estricta):
alli el usuario de credito podia esperar indefinidamente; aqui el ciclo
garantiza que se atienda en menos de una vuelta completa.
"""

from __future__ import annotations

from ...domain.exceptions import ColaVaciaError
from ...domain.plan import Planificador
from ...domain.ports import ColaTurnosPort
from ..dtos import TurnoAtendidoDTO, UsuarioDTO


class AtenderSiguienteUsuario:
    """Ejecuta el proximo turno de la rotacion."""

    def __init__(self, colas: ColaTurnosPort, planificador: Planificador) -> None:
        self._colas = colas
        self._planificador = planificador

    @property
    def longitud_ciclo(self) -> int:
        """Largo del ciclo con el que rota este caso de uso."""
        return self._planificador.longitud_ciclo

    def execute(self) -> TurnoAtendidoDTO:
        turno = self._colas.avanzar_turno(self._planificador)
        if turno is None:
            raise ColaVaciaError("no hay usuarios en ninguna cola para atender")

        return TurnoAtendidoDTO(
            usuario=UsuarioDTO.desde_registrado(turno.usuario),
            tipo_tramite=turno.tipo_tramite,
            posicion_ciclo_anterior=turno.posicion_anterior,
            posicion_ciclo_siguiente=turno.posicion_siguiente,
        )