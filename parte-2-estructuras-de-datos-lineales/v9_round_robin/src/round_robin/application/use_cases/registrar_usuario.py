"""Caso de uso: registrar un usuario en la cola de su tipo de tramite."""

from __future__ import annotations

from datetime import datetime, timezone

from ...domain.entities import Usuario
from ...domain.enums import TipoTramite
from ...domain.exceptions import DatosInvalidosError
from ...domain.ports import ColaTurnosPort
from ..dtos import UsuarioDTO


class RegistrarUsuarioEnCola:
    """Da de alta a un usuario en la cola que le corresponde a su tramite."""

    def __init__(self, colas: ColaTurnosPort) -> None:
        self._colas = colas

    def execute(
        self,
        nombre: str,
        tipo_tramite: TipoTramite,
        monto_transaccion: float,
    ) -> UsuarioDTO:
        nombre = nombre.strip()
        if not nombre:
            raise DatosInvalidosError("el nombre del usuario no puede estar vacio")

        monto = float(monto_transaccion)
        if monto < 0:
            raise DatosInvalidosError("el monto de la transaccion no puede ser negativo")

        usuario = Usuario(
            nombre=nombre,
            tipo_tramite=tipo_tramite,
            monto_transaccion=monto,
            creado_en=datetime.now(timezone.utc),
        )
        return UsuarioDTO.desde_registrado(self._colas.encolar(usuario))