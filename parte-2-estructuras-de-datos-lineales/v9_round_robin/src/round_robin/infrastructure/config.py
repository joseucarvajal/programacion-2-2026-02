"""Configuracion de la aplicacion, leida del entorno.

Se mantiene como dataclass plano (sin pydantic-settings) para no sumar
dependencias y para que se vea de forma explicita de donde sale cada valor.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

from ..domain.enums import TipoTramite
from ..domain.plan import PESOS_POR_DEFECTO

PREFIJO_SQLITE = "sqlite:///"


PREFIJO_SQLITE = "sqlite:///"

# Los valores por defecto viven aqui y no como atributos de clase: con
# ``slots=True`` los defaults dejan de ser accesibles desde ``Cls.campo``
# (devuelven el descriptor del slot), asi que se referencian desde el modulo.
RUTA_POR_DEFECTO = "var/round_robin.db"
CORS_POR_DEFECTO = ("http://localhost:3000", "http://localhost:5173")
TITULO_POR_DEFECTO = "API de colas de la tienda - Round Robin"
VERSION_POR_DEFECTO = "1.0.0"


@dataclass(frozen=True, slots=True)
class Configuracion:
    """Parametros con los que arranca el servidor."""

    ruta_base_datos: str = RUTA_POR_DEFECTO
    pesos_por_defecto: Mapping[TipoTramite, int] = field(default=PESOS_POR_DEFECTO)
    cors_origins: tuple[str, ...] = CORS_POR_DEFECTO
    titulo: str = TITULO_POR_DEFECTO
    descripcion: str = (
        "Gestion de las colas de atencion de una tienda con rotacion de turnos "
        "Round Robin ponderada (3 pago de deudas, 2 compra de contado, "
        "1 solicitud de credito)."
    )
    version: str = VERSION_POR_DEFECTO

    @classmethod
    def desde_entorno(cls) -> Configuracion:
        """Construye la configuracion leyendo las variables de entorno."""
        pesos = PESOS_POR_DEFECTO
        if crudo := os.getenv("ROUND_ROBIN_PESOS"):
            pesos = _parsear_pesos(crudo)

        cors = os.getenv("CORS_ORIGINS")
        return cls(
            ruta_base_datos=os.getenv("DATABASE_URL") or RUTA_POR_DEFECTO,
            pesos_por_defecto=pesos,
            cors_origins=tuple(o.strip() for o in cors.split(",") if o.strip())
            if cors
            else CORS_POR_DEFECTO,
            titulo=os.getenv("TITULO") or TITULO_POR_DEFECTO,
            version=os.getenv("VERSION_API") or VERSION_POR_DEFECTO,
        )


def parsear_ruta_sqlite(valor: str) -> str:
    """Normaliza la ruta de la base de datos.

    Acepta las tres formas habituales:

    ==============================  ==========================
    ``DATABASE_URL``                resultado
    ==============================  ==========================
    ``sqlite:///var/datos.db``      ``var/datos.db`` (relativa)
    ``sqlite:////tmp/datos.db``     ``/tmp/datos.db`` (absoluta)
    ``var/datos.db``                ``var/datos.db``
    ==============================  ==========================

    Ojo con la convencion de URLs: tras ``sqlite://`` queda siempre una barra
    inicial, y es la que distingue una ruta relativa de una absoluta (una barra
    mas es la ruta absoluta). Por eso se quita exactamente una.

    Raises:
        ValueError: si se pide un esquema que SQLite no maneja, o una base en
            memoria, que no serviria porque se abre una conexion por operacion.
    """
    if "://" in valor:
        esquema, _, resto = valor.partition("://")
        if esquema != "sqlite":
            raise ValueError(
                f"esquema no soportado: {esquema!r}. Solo se admite 'sqlite:///' "
                "por ahora (ver README para migrar a PostgreSQL)."
            )
        # Tras "sqlite://" siempre queda una barra inicial: es la que separa la
        # ruta relativa de la absoluta. Se quita exactamente una.
        valor = resto[1:] if resto.startswith("/") else resto

    if valor in ("", ":memory:"):
        raise ValueError(
            "no se admite una base en memoria: el repositorio abre una conexion "
            "por operacion y cada conexion(':memory:') seria una base distinta. "
            "Usa una ruta de archivo."
        )
    return valor


def _parsear_pesos(crudo: str) -> dict[TipoTramite, int]:
    """Interpreta ``ROUND_ROBIN_PESOS=3,2,1`` segun el orden 0, 1, 2."""
    partes = [p.strip() for p in crudo.split(",")]
    if len(partes) != len(TipoTramite):
        raise ValueError(
            f"ROUND_ROBIN_PESOS debe tener {len(TipoTramite)} valores "
            f"(orden: {', '.join(str(int(t)) for t in sorted(TipoTramite, key=int))})"
        )
    return {
        tipo: int(valor)
        for tipo, valor in zip(sorted(TipoTramite, key=int), partes, strict=True)
    }


def ruta_por_defecto() -> Path:
    return Path(Configuracion.ruta_base_datos)