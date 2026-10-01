"""Repositorio de las colas sobre SQLite.

Implementa ``ColaTurnosPort``. Todo el SQL vive aqui; el dominio no sabe que
esta base de datos existe.

Fidelidad de la cola
--------------------
Una cola es "los usuarios de este tipo de tramite, en orden de llegada". Eso se
logra con ``WHERE tipo_tramite = ? ORDER BY id LIMIT 1``: el indice
``(tipo_tramite, id)`` resuelve esa consulta sin ordenar nada en memoria.

Atomicidad
----------
``avanzar_turno`` hace las cuatro operaciones (leer posicion, calcular turno,
borrar usuario, guardar posicion) dentro de una sola transaccion ``IMMEDIATE``.
O sale todo o no sale nada, incluso con varios workers de uvicorn.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime

from ....domain.entities import Usuario, UsuarioRegistrado
from ....domain.enums import TipoTramite
from ....domain.plan import Planificador
from ....domain.ports import ColaTurnosPort, EstadoDeColas, SiguienteEnCola, TurnoAtendido
from .conexion import FabricaDeConexionSQLite

CLAVE_POSICION = "posicion_ciclo"

SELECT_USUARIO = (
    "SELECT id, nombre, tipo_tramite, monto_transaccion, creado_en FROM usuarios"
)


class ColaTurnosSQLite(ColaTurnosPort):
    """Almacen de colas con estado compartido entre procesos.

    A diferencia del repositorio en memoria, esta clase **no tiene estado**: el
    estado vive en el archivo de la base de datos. Por eso el mismo objeto puede
    compartirlo varios workers sin necesidad de bloqueos en memoria.
    """

    def __init__(self, fabrica: FabricaDeConexionSQLite) -> None:
        self._fabrica = fabrica

    # ------------------------------------------------------------------ lectura

    def posicion_ciclo(self, longitud_ciclo: int) -> int:
        with self._fabrica.lectura() as conexion:
            valor = self._leer_posicion(conexion)
        # Se normaliza al largo del ciclo: si se reconfiguran los pesos en
        # caliente, la posicion guardada puede quedar fuera de rango.
        return valor % longitud_ciclo if longitud_ciclo else 0

    def instantanea(self) -> EstadoDeColas:
        with self._fabrica.lectura() as conexion:
            posicion = self._leer_posicion(conexion)
            filas = conexion.execute(f"{SELECT_USUARIO} ORDER BY tipo_tramite, id").fetchall()

        colas: dict[TipoTramite, list[UsuarioRegistrado]] = {
            tipo: [] for tipo in TipoTramite
        }
        for fila in filas:
            colas[TipoTramite(fila["tipo_tramite"])].append(_a_registrado(fila))

        return EstadoDeColas(
            colas={tipo: tuple(usuarios) for tipo, usuarios in colas.items()},
            posicion_ciclo=posicion,
        )

    def inspeccionar_turno(self, planificador: Planificador) -> SiguienteEnCola | None:
        """Consulta el proximo turno sin mover nada.

        Notar que ni borra al usuario ni escribe la posicion: por eso el
        ciclo no avanza. Comparte la logica con ``avanzar_turno`` pero sin los
        dos ``DELETE``/``UPDATE``.
        """
        longitud = planificador.longitud_ciclo
        with self._fabrica.lectura() as conexion:
            posicion = self._leer_posicion(conexion) % longitud
            ocupados = self._tipos_ocupados(conexion)
            turno = planificador.planear(ocupados, posicion)
            if turno is None:
                return None
            fila = self._primero_de(conexion, turno.tipo_tramite)

        return SiguienteEnCola(turno=turno, usuario=_a_registrado(fila))

    # ---------------------------------------------------------------- escritura

    def encolar(self, usuario: Usuario) -> UsuarioRegistrado:
        with self._fabrica.escritura() as conexion:
            cursor = conexion.execute(
                "INSERT INTO usuarios (nombre, tipo_tramite, monto_transaccion, creado_en)"
                " VALUES (?, ?, ?, ?)",
                (
                    usuario.nombre,
                    int(usuario.tipo_tramite),
                    usuario.monto_transaccion,
                    usuario.creado_en.isoformat(),
                ),
            )
            nuevo_id = cursor.lastrowid
        return UsuarioRegistrado(id=nuevo_id, usuario=usuario)

    def avanzar_turno(self, planificador: Planificador) -> TurnoAtendido | None:
        longitud = planificador.longitud_ciclo

        with self._fabrica.escritura() as conexion:
            posicion = self._leer_posicion(conexion) % longitud
            ocupados = self._tipos_ocupados(conexion)
            turno = planificador.planear(ocupados, posicion)
            if turno is None:
                return None

            fila = self._primero_de(conexion, turno.tipo_tramite)
            conexion.execute("DELETE FROM usuarios WHERE id = ?", (fila["id"],))
            conexion.execute(
                "UPDATE estado SET valor = ? WHERE clave = ?",
                (turno.posicion_siguiente, CLAVE_POSICION),
            )
            usuario = _a_registrado(fila)

        # Todo lo anterior salio de la transaccion: si algo falla, no se
        # atendio a nadie y el ciclo no se movio.
        return TurnoAtendido(
            tipo_tramite=turno.tipo_tramite,
            posicion_anterior=posicion,
            posicion_siguiente=turno.posicion_siguiente,
            usuario=usuario,
        )

    def retirar(self, usuario_id: int) -> UsuarioRegistrado | None:
        with self._fabrica.escritura() as conexion:
            fila = conexion.execute(
                f"{SELECT_USUARIO} WHERE id = ?", (usuario_id,)
            ).fetchone()
            if fila is None:
                return None
            conexion.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
        return _a_registrado(fila)

    def reiniciar(self) -> None:
        with self._fabrica.escritura() as conexion:
            conexion.execute("DELETE FROM usuarios")
            conexion.execute(
                "UPDATE estado SET valor = 0 WHERE clave = ?", (CLAVE_POSICION,)
            )

    # ------------------------------------------------------------- internos

    @staticmethod
    def _leer_posicion(conexion: sqlite3.Connection) -> int:
        fila = conexion.execute(
            "SELECT valor FROM estado WHERE clave = ?", (CLAVE_POSICION,)
        ).fetchone()
        return int(fila["valor"]) if fila else 0

    @staticmethod
    def _tipos_ocupados(conexion: sqlite3.Connection) -> set[TipoTramite]:
        filas = conexion.execute("SELECT DISTINCT tipo_tramite FROM usuarios").fetchall()
        return {TipoTramite(fila["tipo_tramite"]) for fila in filas}

    @staticmethod
    def _primero_de(conexion: sqlite3.Connection, tipo: TipoTramite) -> sqlite3.Row:
        """El usuario mas antiguo de esa cola (orden de llegada por ``id``)."""
        fila = conexion.execute(
            f"{SELECT_USUARIO} WHERE tipo_tramite = ? ORDER BY id LIMIT 1",
            (int(tipo),),
        ).fetchone()
        if fila is None:  # pragma: no cover - la politica solo pide colas ocupadas
            raise LookupError(f"la cola de {tipo} se reporto ocupada pero esta vacia")
        return fila


def _a_registrado(fila: sqlite3.Row) -> UsuarioRegistrado:
    usuario = Usuario(
        nombre=fila["nombre"],
        tipo_tramite=TipoTramite(fila["tipo_tramite"]),
        monto_transaccion=float(fila["monto_transaccion"]),
        creado_en=datetime.fromisoformat(fila["creado_en"]),
    )
    return UsuarioRegistrado(id=int(fila["id"]), usuario=usuario)