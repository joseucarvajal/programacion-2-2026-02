"""Fixtures compartidas.

Nótese que los tests de persistencia corren **las mismas pruebas** contra el
repositorio en memoria y contra el de SQLite. Esa es la prueba practica de que
el puerto funciona: mismo comportamiento, dos almacenes distintos.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest

from round_robin.domain.plan import PoliticaRoundRobin
from round_robin.domain.ports import ColaTurnosPort
from round_robin.infrastructure.persistence.en_memoria import ColaTurnosEnMemoria
from round_robin.infrastructure.persistence.sqlite import (
    ColaTurnosSQLite,
    FabricaDeConexionSQLite,
)


@pytest.fixture
def fabrica_sqlite(tmp_path) -> Iterator[FabricaDeConexionSQLite]:
    fabrica = FabricaDeConexionSQLite(str(tmp_path / "colas.db"))
    fabrica.inicializar_esquema()
    yield fabrica


@pytest.fixture
def colas_sqlite(fabrica_sqlite: FabricaDeConexionSQLite) -> ColaTurnosPort:
    return ColaTurnosSQLite(fabrica_sqlite)


@pytest.fixture
def colas_memoria() -> ColaTurnosPort:
    return ColaTurnosEnMemoria()


@pytest.fixture(params=["memoria", "sqlite"])
def colas(request, fabrica_sqlite) -> ColaTurnosPort:
    """Ejecuta cada test de persistencia contra los dos adaptadores."""
    if request.param == "sqlite":
        return ColaTurnosSQLite(fabrica_sqlite)
    return ColaTurnosEnMemoria()


@pytest.fixture
def planificador() -> PoliticaRoundRobin:
    """Round Robin ponderado 3-2-1, el del enunciado."""
    return PoliticaRoundRobin()