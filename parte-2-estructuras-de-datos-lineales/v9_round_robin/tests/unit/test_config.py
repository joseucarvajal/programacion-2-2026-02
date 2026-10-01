"""Pruebas del parseo de la ruta y de los pesos de configuracion."""

from __future__ import annotations

import pytest

from round_robin.infrastructure.config import parsear_ruta_sqlite


@pytest.mark.parametrize(
    "valor, esperado",
    [
        ("sqlite:///var/datos.db", "var/datos.db"),  # relativa
        ("sqlite:////tmp/datos.db", "/tmp/datos.db"),  # absoluta
        ("var/datos.db", "var/datos.db"),  # sin esquema
        ("./datos.db", "./datos.db"),
    ],
)
def test_parsear_ruta_sqlite(valor, esperado):
    assert parsear_ruta_sqlite(valor) == esperado


@pytest.mark.parametrize(
    "valor",
    [
        "sqlite:///:memory:",
        "sqlite://",  # queda una ruta vacia
        ":memory:",
        "",
    ],
)
def test_se_rechaza_la_base_en_memoria(valor):
    with pytest.raises(ValueError, match="memoria"):
        parsear_ruta_sqlite(valor)


def test_se_rechaza_un_esquema_no_soportado():
    with pytest.raises(ValueError, match="esquema no soportado"):
        parsear_ruta_sqlite("postgresql://localhost/tienda")


def test_la_ruta_relativa_se_crea_sola(tmp_path, monkeypatch):
    """El directorio de la base se crea si no existe."""
    monkeypatch.chdir(tmp_path)

    from round_robin.infrastructure.persistence.sqlite import FabricaDeConexionSQLite

    ruta = parsear_ruta_sqlite("sqlite:///var/anidada/colas.db")
    fabrica = FabricaDeConexionSQLite(ruta)
    fabrica.inicializar_esquema()

    assert (tmp_path / "var" / "anidada" / "colas.db").exists()