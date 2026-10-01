"""Pruebas del adaptador de SQLite.

Se concentran en lo que el repositorio en memoria **no** puede dar:

* que el estado sobreviva a cerrar y reabrir la base,
* que el turno sea atomico,
* que retirar por id sea barato,
* que la base imponga sus propias reglas.
"""

from __future__ import annotations

import sqlite3

import pytest

from round_robin.domain.enums import TipoTramite
from round_robin.domain.plan import PESOS_ROUND_ROBIN_PURO, PoliticaRoundRobin
from round_robin.infrastructure.persistence.sqlite import (
    ColaTurnosSQLite,
    FabricaDeConexionSQLite,
)

from helpers import usuario

T = TipoTramite


@pytest.fixture
def planificador() -> PoliticaRoundRobin:
    return PoliticaRoundRobin()


# ------------------------------------------------------------- orden de cola


def test_la_cola_respeta_el_orden_de_llegada(colas, planificador):
    for numero in range(3):
        colas.encolar(usuario(f"pago-{numero}", T.PAGO_DEUDAS))

    atendidos = [colas.avanzar_turno(planificador).usuario.nombre for _ in range(3)]

    assert atendidos == ["pago-0", "pago-1", "pago-2"]


def test_el_id_autoincremental_da_el_orden_de_llegada(colas):
    primero = colas.encolar(usuario("Ana"))
    segundo = colas.encolar(usuario("Luis"))
    assert primero.id < segundo.id


# ------------------------------------------------------------------ atomicidad


def test_avanzar_turno_consume_una_sola_vez(colas, planificador):
    for numero in range(3):
        colas.encolar(usuario(f"pago-{numero}", T.PAGO_DEUDAS))

    atendidos = [colas.avanzar_turno(planificador).usuario.nombre for _ in range(3)]

    assert len(set(atendidos)) == 3, "ningun usuario puede ser atendido dos veces"
    assert colas.instantanea().total_usuarios == 0


def test_inspeccionar_no_mueve_el_ciclo(colas, planificador):
    for _ in range(2):
        colas.encolar(usuario("Ana", T.PAGO_DEUDAS))

    assert colas.inspeccionar_turno(planificador).turno.tipo_tramite is T.PAGO_DEUDAS
    assert colas.inspeccionar_turno(planificador).turno.tipo_tramite is T.PAGO_DEUDAS
    assert colas.posicion_ciclo(planificador.longitud_ciclo) == 0

    # Consultar 5 veces no debe avanzar el ciclo ni sacar a nadie.
    assert colas.instantanea().total_usuarios == 2
    assert colas.avanzar_turno(planificador).posicion_anterior == 0


def test_inspeccionar_con_colas_vacias_devuelve_none(colas, planificador):
    assert colas.inspeccionar_turno(planificador) is None
    assert colas.avanzar_turno(planificador) is None


# --------------------------------------------------------------- persistencia


def test_el_estado_sobrevive_a_reabrir_la_base(fabrica_sqlite, planificador):
    """Justifica eligiendo SQLite: la posicion del ciclo no se pierde."""
    primero = ColaTurnosSQLite(fabrica_sqlite)
    primero.encolar(usuario("Ana", T.PAGO_DEUDAS))
    primero.encolar(usuario("Luis", T.PAGO_DEUDAS))
    primero.avanzar_turno(planificador)  # posicion 0 -> 1
    primero.avanzar_turno(planificador)  # posicion 1 -> 2

    # Se "reinicia el servidor": objeto nuevo, misma base de datos.
    segundo = ColaTurnosSQLite(fabrica_sqlite)

    assert segundo.posicion_ciclo(planificador.longitud_ciclo) == 2
    assert segundo.instantanea().total_usuarios == 0


def test_la_posicion_se_normaliza_si_cambia_el_largo_del_ciclo(colas, planificador):
    """Si se reconfiguran los pesos, la posicion guardada se reinterpreta."""
    for numero in range(5):
        colas.encolar(usuario(f"pago-{numero}", T.PAGO_DEUDAS))
    for _ in range(3):
        colas.avanzar_turno(planificador)  # las tres posiciones de deuda

    assert colas.posicion_ciclo(6) == 3
    # Quedan dos usuarios de pago de deudas.
    assert colas.instantanea().total_usuarios == 2

    # Con el Round Robin puro el ciclo es de 3: la posicion 3 da la vuelta,
    # y ademas queda normalizada en 0 en lugar de apuntar fuera de rango.
    assert colas.posicion_ciclo(3) == 0
    # El turno sigue funcionando con el ciclo mas corto.
    assert colas.avanzar_turno(PoliticaRoundRobin(PESOS_ROUND_ROBIN_PURO)) is not None


# ------------------------------------------------------------------ retirar


def test_retirar_por_id_no_afecta_a_los_demas(colas, planificador):
    objetivo = colas.encolar(usuario("Ana", T.COMPRA_DE_CONTADO))
    colas.encolar(usuario("Luis", T.COMPRA_DE_CONTADO))

    retirado = colas.retirar(objetivo.id)

    assert retirado.usuario.nombre == "Ana"
    restantes = [u.usuario.nombre for u in colas.instantanea().colas[T.COMPRA_DE_CONTADO]]
    assert restantes == ["Luis"]


def test_retirar_un_id_inexistente_devuelve_none(colas):
    assert colas.retirar(999) is None


def test_reiniciar_vacia_las_colas_y_el_ciclo(colas, planificador):
    colas.encolar(usuario("Ana", T.PAGO_DEUDAS))
    colas.avanzar_turno(planificador)
    colas.encolar(usuario("Luis", T.PAGO_DEUDAS))

    colas.reiniciar()

    assert colas.instantanea().total_usuarios == 0
    assert colas.posicion_ciclo(planificador.longitud_ciclo) == 0


# ------------------------------------------------------------- reglas del DDL


def test_la_base_rechaza_un_tipo_de_tramite_invalido(fabrica_sqlite):
    """El CHECK del esquema hace de segunda linea de defensa."""
    with fabrica_sqlite.escritura() as conexion:
        with pytest.raises(sqlite3.IntegrityError):
            conexion.execute(
                "INSERT INTO usuarios (nombre, tipo_tramite, monto_transaccion, creado_en)"
                " VALUES ('Ana', 9, 100.0, '2026-01-01T00:00:00+00:00')"
            )


def test_la_base_rechaza_un_monto_negativo(fabrica_sqlite):
    with fabrica_sqlite.escritura() as conexion:
        with pytest.raises(sqlite3.IntegrityError):
            conexion.execute(
                "INSERT INTO usuarios (nombre, tipo_tramite, monto_transaccion, creado_en)"
                " VALUES ('Ana', 0, -1.0, '2026-01-01T00:00:00+00:00')"
            )


def test_crear_el_esquema_es_idempotente(fabrica_sqlite):
    # Si alguien lo ejecutara dos veces, no debe romperse nada.
    fabrica_sqlite.inicializar_esquema()
    fabrica_sqlite.inicializar_esquema()