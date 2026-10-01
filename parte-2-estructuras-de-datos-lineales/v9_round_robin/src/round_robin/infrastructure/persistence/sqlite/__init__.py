"""Adaptador de persistencia sobre SQLite."""

from .cola_turnos_sqlite import ColaTurnosSQLite
from .conexion import FabricaDeConexionSQLite

__all__ = ["ColaTurnosSQLite", "FabricaDeConexionSQLite"]