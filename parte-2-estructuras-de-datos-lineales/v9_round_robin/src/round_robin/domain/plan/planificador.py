"""Contrato de las politicas de asignacion de turnos.

Una politica decide *a quien le toca*, pero **no guarda estado**. La posicion
actual del ciclo vive en el almacen (el puerto), no aqui. Gracias a eso la
politica es una funcion pura: facil de probar y de razonar.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Collection
from dataclasses import dataclass

from ..enums import TipoTramite


@dataclass(frozen=True, slots=True)
class Turno:
    """Decision de la politica: a que cola le toca y donde queda el ciclo.

    ``posicion_siguiente`` es la posicion del ciclo **despues** de aplicar este
    turno. Quienllame lo persiste.
    """

    tipo_tramite: TipoTramite
    posicion_siguiente: int


class Planificador(ABC):
    """Politica de rotacion de colas."""

    @property
    @abstractmethod
    def nombre(self) -> str:
        """Nombre legible de la politica."""

    @property
    @abstractmethod
    def pesos(self) -> dict[TipoTramite, int]:
        """Cuantos turnos le tocan a cada tipo de tramite por ciclo."""

    @property
    @abstractmethod
    def ciclo(self) -> tuple[TipoTramite, ...]:
        """La secuencia de tipos que se repite indefinidamente.

        Round Robin puro      -> (deudas, contado, credito)
        Round Robin ponderado -> (deudas, deudas, deudas, contado, contado, credito)
        """

    @property
    def longitud_ciclo(self) -> int:
        return len(self.ciclo)

    @abstractmethod
    def planear(
        self,
        tipos_ocupados: Collection[TipoTramite],
        posicion_actual: int,
    ) -> Turno | None:
        """Elige el proximo tipo de tramite a atender.

        Args:
            tipos_ocupados: tipos de tramite que tienen al menos un usuario.
            posicion_actual: indice dentro del ciclo, tal como quedo guardado.

        Returns:
            El turno, o ``None`` si no hay nada que atender.
        """