"""Caso de uso: vaciar las colas y reiniciar la rotacion.

Pensado para pruebas y para el boton "reiniciar" de la interfaz de
administracion de la tienda.
"""

from __future__ import annotations

from ...domain.ports import ColaTurnosPort


class ReiniciarColas:
    """Deja el sistema como si nadie se hubiera registrado nunca."""

    def __init__(self, colas: ColaTurnosPort) -> None:
        self._colas = colas

    def execute(self) -> None:
        self._colas.reiniciar()