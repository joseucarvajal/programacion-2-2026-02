"""Gestion de conexiones a SQLite.

Dos conceptos importantes:

1. **Una conexion por operacion.** FastAPI ejecuta los endpoints sincronos en un
   grupo de hilos, y un objeto ``sqlite3.Connection`` creado en otro hilo lanza
   ``SQLite objects created in a thread can only be used in that same thread``.
   Por eso no hay una conexion global: cada operacion abre y cierra la suya.

2. **Dos tipos de transaccion.**
   ``escritura()`` usa ``BEGIN IMMEDIATE``, que toma el cerrojo de escritura de
   entrada. Es el equivalente multi-proceso del ``threading.Lock`` del
   repositorio en memoria, y es lo que garantiza que "avanzar un turno" sea
   atomico aunque corran varios workers de uvicorn.
   ``lectura()`` usa ``BEGIN DEFERRED``: en modo WAL da una vista consistente
   sin bloquear a los escritores, que es lo que necesita el frontend cuando
   consulta el estado cada segundo.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

ESQUEMA = Path(__file__).with_name("esquema.sql")


class FabricaDeConexionSQLite:
    """Crea conexiones configuradas contra un archivo SQLite."""

    def __init__(self, ruta: str) -> None:
        self._ruta = ruta
        parent = Path(ruta).expanduser().resolve().parent
        parent.mkdir(parents=True, exist_ok=True)

    @property
    def ruta(self) -> str:
        return self._ruta

    def conectar(self) -> sqlite3.Connection:
        conexion = sqlite3.connect(
            self._ruta,
            # Autocommit: las transacciones se controlan a mano, sin la
            # maquinaria implicita de BEGIN DEFERRED del modulo sqlite3.
            isolation_level=None,
            timeout=10.0,
        )
        conexion.row_factory = sqlite3.Row
        conexion.execute("PRAGMA busy_timeout = 5000")  # esperar turno, no fallar
        conexion.execute("PRAGMA journal_mode = WAL")  # lectores sin bloquear
        conexion.execute("PRAGMA foreign_keys = ON")
        return conexion

    @contextmanager
    def escritura(self) -> Iterator[sqlite3.Connection]:
        """Transaccion de escritura, atomica frente a otros procesos."""
        conexion = self.conectar()
        try:
            conexion.execute("BEGIN IMMEDIATE")
            yield conexion
            conexion.execute("COMMIT")
        except BaseException:
            _revertir(conexion)
            raise
        finally:
            conexion.close()

    @contextmanager
    def lectura(self) -> Iterator[sqlite3.Connection]:
        """Transaccion de solo lectura: no bloquea a los escritores."""
        conexion = self.conectar()
        try:
            conexion.execute("BEGIN DEFERRED")
            yield conexion
            conexion.execute("COMMIT")
        except BaseException:
            _revertir(conexion)
            raise
        finally:
            conexion.close()

    def inicializar_esquema(self) -> None:
        """Crea las tablas si no existen. Es idempotente."""
        conexion = self.conectar()
        try:
            conexion.executescript(ESQUEMA.read_text(encoding="utf-8"))
        finally:
            conexion.close()


def _revertir(conexion: sqlite3.Connection) -> None:
    """ROLLBACK, tolerando que la transaccion nunca haya arrancado."""
    try:
        conexion.execute("ROLLBACK")
    except sqlite3.Error:
        pass