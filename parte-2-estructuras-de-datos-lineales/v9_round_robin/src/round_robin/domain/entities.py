"""Entidades del dominio.

Una entidad es un objeto con identidad propia. Aqui hay dos:

* :class:`Usuario`      -> lo que la persona quiere resolver (datos de negocio).
* :class:`UsuarioRegistrado` -> ese mismo usuario ya metido en una cola, con el
  identificador que le asigno el almacen.

La separacion importa: ``Usuario`` no sabe nada de persistencia ni de ids, y
``UsuarioRegistrado`` es lo que realmente se guarda y se saca de la cola.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .enums import TipoTramite


@dataclass(frozen=True, slots=True)
class Usuario:
    """Persona que llega a la tienda a resolver un tramite."""

    nombre: str
    tipo_tramite: TipoTramite
    monto_transaccion: float
    creado_en: datetime

    @property
    def es_prioritario(self) -> bool:
        """True si el tramite es de la maxima prioridad (pago de deudas)."""
        return self.tipo_tramite is TipoTramite.PAGO_DEUDAS


@dataclass(frozen=True, slots=True)
class UsuarioRegistrado:
    """Usuario ya encolado, con el identificador que le dio el almacen."""

    id: int
    usuario: Usuario

    # Delegaciones para no tener que escribir ``.usuario.usuario.nombre``
    # cada vez que se usa un usuario ya registrado.
    @property
    def nombre(self) -> str:
        return self.usuario.nombre

    @property
    def tipo_tramite(self) -> TipoTramite:
        return self.usuario.tipo_tramite

    @property
    def monto_transaccion(self) -> float:
        return self.usuario.monto_transaccion

    @property
    def creado_en(self) -> datetime:
        return self.usuario.creado_en