"""Enumeraciones del dominio.

Es la capa más interna del proyecto: no importa nada de ninguna otra capa.
Se usa ``IntEnum`` para conservar los valores 0, 1 y 2 de la version de
consola (``v82_colas_con_prioridad``), de modo que la API habla el mismo
lenguaje que el código que ya existe en el curso.
"""

from __future__ import annotations

from enum import IntEnum


class TipoTramite(IntEnum):
    """Clase de tramite que determina a que cola pertenece un usuario."""

    PAGO_DEUDAS = 0
    COMPRA_DE_CONTADO = 1
    SOLICITUD_CREDITO = 2


DESCRIPCION_TRAMITE: dict[TipoTramite, str] = {
    TipoTramite.PAGO_DEUDAS: "pago de deudas",
    TipoTramite.COMPRA_DE_CONTADO: "compra de contado",
    TipoTramite.SOLICITUD_CREDITO: "solicitud de credito",
}


def descripcion_de(tipo_tramite: TipoTramite) -> str:
    """Texto legible de un tipo de tramite."""
    return DESCRIPCION_TRAMITE[tipo_tramite]