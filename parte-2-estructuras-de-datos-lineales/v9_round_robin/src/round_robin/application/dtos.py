"""Objetos de transferencia de datos de la capa de aplicacion.

Son la frontera entre el mundo del negocio y el mundo de la API. Se usan
dataclasses propios en vez de modelos de Pydantic para que las reglas de
validacion del transporte (que son de otra capa) no se filtren hacia adentro.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from ..domain.entities import UsuarioRegistrado
from ..domain.enums import TipoTramite
from ..domain.ports import EstadoDeColas


@dataclass(frozen=True, slots=True)
class UsuarioDTO:
    """Usuario como lo ve el cliente de la API."""

    id: int
    nombre: str
    tipo_tramite: TipoTramite
    monto_transaccion: float
    creado_en: datetime

    @classmethod
    def desde_registrado(cls, registrado: UsuarioRegistrado) -> UsuarioDTO:
        return cls(
            id=registrado.id,
            nombre=registrado.usuario.nombre,
            tipo_tramite=registrado.usuario.tipo_tramite,
            monto_transaccion=registrado.usuario.monto_transaccion,
            creado_en=registrado.usuario.creado_en,
        )


@dataclass(frozen=True, slots=True)
class TurnoAtendidoDTO:
    """Resultado de atender: el usuario ya salio de la cola."""

    usuario: UsuarioDTO
    tipo_tramite: TipoTramite
    posicion_ciclo_anterior: int
    posicion_ciclo_siguiente: int


@dataclass(frozen=True, slots=True)
class SiguienteDTO:
    """Consulta del proximo turno. El usuario sigue en la cola."""

    usuario: UsuarioDTO
    tipo_tramite: TipoTramite
    posicion_ciclo: int


@dataclass(frozen=True, slots=True)
class ColaDTO:
    """Una de las tres colas, con su peso en la rotacion."""

    tipo_tramite: TipoTramite
    peso: int
    usuarios: tuple[UsuarioDTO, ...]

    @property
    def total(self) -> int:
        return len(self.usuarios)

    @property
    def monto_total(self) -> float:
        return sum(usuario.monto_transaccion for usuario in self.usuarios)


@dataclass(frozen=True, slots=True)
class EstadoDeColasDTO:
    """Fotografia completa: las tres colas, los totales y el ciclo."""

    colas: tuple[ColaDTO, ...]
    posicion_ciclo: int
    longitud_ciclo: int
    total_usuarios: int
    total_montos: float

    @classmethod
    def desde_dominio(
        cls,
        estado: EstadoDeColas,
        pesos: dict[TipoTramite, int],
        longitud_ciclo: int,
    ) -> EstadoDeColasDTO:
        colas = tuple(
            ColaDTO(
                tipo_tramite=tipo,
                peso=pesos.get(tipo, 0),
                usuarios=tuple(UsuarioDTO.desde_registrado(u) for u in estado.colas.get(tipo, ())),
            )
            for tipo in sorted(pesos, key=int)
        )
        return cls(
            colas=colas,
            posicion_ciclo=estado.posicion_ciclo,
            longitud_ciclo=longitud_ciclo,
            total_usuarios=estado.total_usuarios,
            total_montos=estado.total_montos,
        )


@dataclass(frozen=True, slots=True)
class ConfiguracionRotacionDTO:
    """Como esta configurada la rotacion en este momento."""

    politica: str
    pesos: tuple[tuple[TipoTramite, int], ...]
    ciclo: tuple[TipoTramite, ...]
    longitud_ciclo: int
    posicion_ciclo: int