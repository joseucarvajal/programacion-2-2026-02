"""Repositorio de las colas en memoria, con ``deque`` y ``threading.Lock``.

Existe por dos motivos:

1. Los tests de los casos de uso corren al instante, sin tocar el disco.
2. Demuestra en clase que el puerto es realmente intercambiable: misma
   interfaz ``ColaTurnosPort``, dos almacenes distintos (memoria y SQLite).

Sus limitaciones son deliberadas y son las que justifican el SQLite:

* El ``threading.Lock`` solo protege **dentro de un mismo proceso**. Con varios
  workers de uvicorn cada uno tendria su propio deque y su propio ciclo.
* Nada sobrevive a un reinicio.
* Retirar un usuario exige recorrer el deque entero (O(n)), porque un ``deque``
  no permite borrar por posicion de forma eficiente.
"""

from __future__ import annotations

import threading
from collections import deque

from ...domain.entities import Usuario, UsuarioRegistrado
from ...domain.enums import TipoTramite
from ...domain.plan import Planificador
from ...domain.ports import ColaTurnosPort, EstadoDeColas, SiguienteEnCola, TurnoAtendido


class ColaTurnosEnMemoria(ColaTurnosPort):
    """Almacen de colas en memoria, con el estado protegido por un lock."""

    def __init__(self) -> None:
        self._colas: dict[TipoTramite, deque[UsuarioRegistrado]] = {
            tipo: deque() for tipo in TipoTramite
        }
        self._siguiente_id = 1
        self._posicion = 0
        self._lock = threading.Lock()

    # ------------------------------------------------------------------ lectura

    def posicion_ciclo(self, longitud_ciclo: int) -> int:
        with self._lock:
            return self._posicion % longitud_ciclo if longitud_ciclo else 0

    def instantanea(self) -> EstadoDeColas:
        with self._lock:
            colas = {tipo: tuple(cola) for tipo, cola in self._colas.items()}
            posicion = self._posicion
        return EstadoDeColas(colas=colas, posicion_ciclo=posicion)

    def inspeccionar_turno(self, planificador: Planificador) -> SiguienteEnCola | None:
        with self._lock:
            longitud = planificador.longitud_ciclo
            posicion = self._posicion % longitud
            turno = planificador.planear(self._tipos_ocupados(), posicion)
            if turno is None:
                return None
            return SiguienteEnCola(turno=turno, usuario=self._colas[turno.tipo_tramite][0])

    # ---------------------------------------------------------------- escritura

    def encolar(self, usuario: Usuario) -> UsuarioRegistrado:
        with self._lock:
            registrado = UsuarioRegistrado(id=self._siguiente_id, usuario=usuario)
            self._siguiente_id += 1
            self._colas[usuario.tipo_tramite].append(registrado)
            return registrado

    def avanzar_turno(self, planificador: Planificador) -> TurnoAtendido | None:
        # El lock cubre planear + sacar + avanzar como una sola operacion: es el
        # equivalente en memoria de la transaccion IMMEDIATE de SQLite.
        with self._lock:
            longitud = planificador.longitud_ciclo
            posicion = self._posicion % longitud
            turno = planificador.planear(self._tipos_ocupados(), posicion)
            if turno is None:
                return None

            usuario = self._colas[turno.tipo_tramite].popleft()
            self._posicion = turno.posicion_siguiente

        return TurnoAtendido(
            tipo_tramite=turno.tipo_tramite,
            posicion_anterior=posicion,
            posicion_siguiente=turno.posicion_siguiente,
            usuario=usuario,
        )

    def retirar(self, usuario_id: int) -> UsuarioRegistrado | None:
        with self._lock:
            for cola in self._colas.values():
                for registrado in cola:
                    if registrado.id == usuario_id:
                        cola.remove(registrado)  # O(n): el precio de usar deque
                        return registrado
        return None

    def reiniciar(self) -> None:
        with self._lock:
            for cola in self._colas.values():
                cola.clear()
            self._posicion = 0

    # ------------------------------------------------------------- internos

    def _tipos_ocupados(self) -> set[TipoTramite]:
        return {tipo for tipo, cola in self._colas.items() if cola}