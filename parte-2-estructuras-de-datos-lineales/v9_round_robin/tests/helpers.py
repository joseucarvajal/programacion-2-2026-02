"""Utilidades compartidas por los tests."""

from __future__ import annotations

from datetime import datetime, timezone

from round_robin.domain.entities import Usuario
from round_robin.domain.enums import TipoTramite

FECHA_FIJA = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)


def usuario(
    nombre: str = "Ana",
    tipo_tramite: TipoTramite = TipoTramite.PAGO_DEUDAS,
    monto: float = 1000.0,
) -> Usuario:
    """Constructor de usuarios para los tests, con fecha fija.

    La fecha fija evita que dos usuarios del mismo lote se ordenen de forma
    distinta por microsegundos.
    """
    return Usuario(
        nombre=nombre,
        tipo_tramite=tipo_tramite,
        monto_transaccion=monto,
        creado_en=FECHA_FIJA,
    )