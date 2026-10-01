"""Puerto de las colas: la frontera entre el dominio y el almacenamiento.

Este es el punto mas importante del diseno. El dominio dice *que* hay que
guardar ("encola esto", "avanza un turno", "dame el estado"); el adaptador dice
*como* se guarda (SQLite, memoria, Redis, Postgres...).

Detalle importante sobre ``avanzar_turno`` y ``inspeccionar_turno``
--------------------------------------------------------------------
Estas operaciones reciben el planificador en vez de que el caso de uso componga
los pasos por su cuenta. La razon es la **atomicidad**:

    leer posicion -> calcular turno -> borrar usuario -> guardar posicion nueva

Si el caso de uso hiciera ``planificador.planear(...)`` y despues
``cola.sacar(...)``, dos peticiones simultaneas podrian calcular el mismo turno
y atender dos veces al mismo usuario. Solo quien tiene el estado puede
garantizar que eso no pase, asi que la transaccion vive en el adaptador.

La politica sigue siendo pura: no sabe que existe una base de datos.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass

from ..entities import Usuario, UsuarioRegistrado
from ..enums import TipoTramite
from ..plan.planificador import Planificador, Turno


@dataclass(frozen=True, slots=True)
class TurnoAtendido:
    """Turno que ya se ejecuto: se removio al usuario de su cola."""

    tipo_tramite: TipoTramite
    posicion_anterior: int
    posicion_siguiente: int
    usuario: UsuarioRegistrado


@dataclass(frozen=True, slots=True)
class SiguienteEnCola:
    """Consulta del proximo turno **sin** ejecutarlo (peek)."""

    turno: Turno
    usuario: UsuarioRegistrado


@dataclass(frozen=True, slots=True)
class EstadoDeColas:
    """Fotografia de las tres colas en un momento dado."""

    colas: Mapping[TipoTramite, tuple[UsuarioRegistrado, ...]]
    posicion_ciclo: int

    @property
    def total_usuarios(self) -> int:
        return sum(len(usuarios) for usuarios in self.colas.values())

    @property
    def total_montos(self) -> float:
        return sum(
            registrado.usuario.monto_transaccion
            for usuarios in self.colas.values()
            for registrado in usuarios
        )


class ColaTurnosPort(ABC):
    """Almacen de colas de usuarios con rotacion de turnos."""

    @abstractmethod
    def encolar(self, usuario: Usuario) -> UsuarioRegistrado:
        """Agrega un usuario al final de la cola de su tipo de tramite.

        El orden de llegada es lo que garantiza el orden dentro de la cola.
        """

    @abstractmethod
    def avanzar_turno(self, planificador: Planificador) -> TurnoAtendido | None:
        """Ejecuta el proximo turno de forma atomica.

        Retorna ``None`` si no hay nada en ninguna cola.
        """

    @abstractmethod
    def inspeccionar_turno(self, planificador: Planificador) -> SiguienteEnCola | None:
        """Consulta el proximo turno **sin** consumirlo ni avanzar el ciclo.

        Separado de ``avanzar_turno`` a proposito: si compartieran el avance,
        cada consulta le robaria un turno al usuario.
        """

    @abstractmethod
    def posicion_ciclo(self, longitud_ciclo: int) -> int:
        """Posicion actual del ciclo, ya normalizada al largo del ciclo."""

    @abstractmethod
    def instantanea(self) -> EstadoDeColas:
        """Estado completo de las colas y del ciclo."""

    @abstractmethod
    def retirar(self, usuario_id: int) -> UsuarioRegistrado | None:
        """Saca a un usuario de su cola. Retorna ``None`` si no existe."""

    @abstractmethod
    def reiniciar(self) -> None:
        """Vacia todas las colas y deja el ciclo en la posicion 0."""