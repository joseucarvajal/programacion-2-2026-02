"""Caso de uso: retirar a un usuario de la cola.

Con la base de datos esto es barato porque el identificador es la clave
primaria. Con un ``deque`` habria que recorrerlo entero (O(n)), que era
justamente el compromiso que se evitio al elegir un almacen relacional.
"""

from __future__ import annotations

from ...domain.exceptions import UsuarioNoEncontradoError
from ...domain.ports import ColaTurnosPort
from ..dtos import UsuarioDTO


class RetirarUsuario:
    """Cancela la espera de un usuario y lo saca de su cola."""

    def __init__(self, colas: ColaTurnosPort) -> None:
        self._colas = colas

    def execute(self, usuario_id: int) -> UsuarioDTO:
        retirado = self._colas.retirar(usuario_id)
        if retirado is None:
            raise UsuarioNoEncontradoError(
                f"no hay ningun usuario encolado con el id {usuario_id}"
            )
        return UsuarioDTO.desde_registrado(retirado)