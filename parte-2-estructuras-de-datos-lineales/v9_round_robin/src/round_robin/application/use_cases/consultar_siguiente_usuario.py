"""Caso de uso: consultar quien sigue, sin atenderlo (peek).

Equivale a la operacion "Consultar" del ``definiciones.md`` de las colas: se
mira el frente de la cola pero **no** se saca a nadie. Por eso el almacen
expone ``inspeccionar_turno`` separado de ``avanzar_turno``.
"""

from __future__ import annotations

from ...domain.exceptions import ColaVaciaError
from ...domain.plan import Planificador
from ...domain.ports import ColaTurnosPort
from ..dtos import SiguienteDTO, UsuarioDTO


class ConsultarSiguienteUsuario:
    """Muestra el proximo turno sin consumirlo ni avanzar el ciclo."""

    def __init__(self, colas: ColaTurnosPort, planificador: Planificador) -> None:
        self._colas = colas
        self._planificador = planificador

    @property
    def longitud_ciclo(self) -> int:
        """Largo del ciclo con el que rota este caso de uso."""
        return self._planificador.longitud_ciclo

    def execute(self) -> SiguienteDTO:
        siguiente = self._colas.inspeccionar_turno(self._planificador)
        if siguiente is None:
            raise ColaVaciaError("no hay usuarios en ninguna cola para consultar")

        return SiguienteDTO(
            usuario=UsuarioDTO.desde_registrado(siguiente.usuario),
            tipo_tramite=siguiente.turno.tipo_tramite,
            posicion_ciclo=siguiente.turno.posicion_siguiente,
        )