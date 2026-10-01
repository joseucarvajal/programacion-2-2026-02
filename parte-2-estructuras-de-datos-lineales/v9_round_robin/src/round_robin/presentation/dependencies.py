"""Punto de composicion: aqui se decide que implementacion se usa.

Este archivo es el unico lugar del proyecto donde se concreta "SQLite de
archivo" y "pesos 3,2,1". Gracias a eso los tests pueden reemplazar el
repositorio con ``app.dependency_overrides`` sin tocar nada mas.
"""

from __future__ import annotations

from functools import lru_cache

from ..application.use_cases import (
    AtenderSiguienteUsuario,
    ConsultarConfiguracionRotacion,
    ConsultarEstadoDeColas,
    ConsultarSiguienteUsuario,
    RegistrarUsuarioEnCola,
    ReiniciarColas,
    RetirarUsuario,
)
from ..domain.plan import PESOS_POR_DEFECTO, PoliticaRoundRobin
from ..domain.plan.planificador import Planificador
from ..domain.ports import ColaTurnosPort
from ..infrastructure.config import Configuracion, parsear_ruta_sqlite
from ..infrastructure.persistence.sqlite import ColaTurnosSQLite, FabricaDeConexionSQLite


@lru_cache(maxsize=1)
def obtener_configuracion() -> Configuracion:
    return Configuracion.desde_entorno()


@lru_cache(maxsize=1)
def obtener_colas() -> ColaTurnosPort:
    """Repositorio real: SQLite, compartido por todos los workers."""
    return ColaTurnosSQLite(obtener_fabrica_sqlite())


@lru_cache(maxsize=1)
def obtener_planificador() -> Planificador:
    """Politica de rotacion, con los pesos del enunciado por defecto."""
    return PoliticaRoundRobin(obtener_configuracion().pesos_por_defecto or PESOS_POR_DEFECTO)


@lru_cache(maxsize=1)
def obtener_fabrica_sqlite() -> FabricaDeConexionSQLite:
    """Misma fabrica que usa el repositorio, para crear el esquema al arrancar."""
    ruta = parsear_ruta_sqlite(obtener_configuracion().ruta_base_datos)
    return FabricaDeConexionSQLite(ruta)


# --- Casos de uso (lo que consume cada endpoint) ---------------------------


@lru_cache(maxsize=1)
def obtener_registrar_usuario() -> RegistrarUsuarioEnCola:
    return RegistrarUsuarioEnCola(obtener_colas())


@lru_cache(maxsize=1)
def obtener_atender_siguiente() -> AtenderSiguienteUsuario:
    return AtenderSiguienteUsuario(obtener_colas(), obtener_planificador())


@lru_cache(maxsize=1)
def obtener_consultar_siguiente() -> ConsultarSiguienteUsuario:
    return ConsultarSiguienteUsuario(obtener_colas(), obtener_planificador())


@lru_cache(maxsize=1)
def obtener_consultar_estado() -> ConsultarEstadoDeColas:
    return ConsultarEstadoDeColas(obtener_colas(), obtener_planificador())


@lru_cache(maxsize=1)
def obtener_consultar_configuracion() -> ConsultarConfiguracionRotacion:
    return ConsultarConfiguracionRotacion(obtener_colas(), obtener_planificador())


@lru_cache(maxsize=1)
def obtener_retirar_usuario() -> RetirarUsuario:
    return RetirarUsuario(obtener_colas())


@lru_cache(maxsize=1)
def obtener_reiniciar_colas() -> ReiniciarColas:
    return ReiniciarColas(obtener_colas())


def limpiar_cache_dependencias() -> None:
    """Olvida los singletons. Se usa entre pruebas."""
    for proveedor in (
        obtener_configuracion,
        obtener_colas,
        obtener_planificador,
        obtener_fabrica_sqlite,
        obtener_registrar_usuario,
        obtener_atender_siguiente,
        obtener_consultar_siguiente,
        obtener_consultar_estado,
        obtener_consultar_configuracion,
        obtener_retirar_usuario,
        obtener_reiniciar_colas,
    ):
        proveedor.cache_clear()