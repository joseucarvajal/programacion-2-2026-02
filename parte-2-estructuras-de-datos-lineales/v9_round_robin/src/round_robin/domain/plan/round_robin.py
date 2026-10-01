"""Politica Round Robin, con ponderacion opcional.

Esta es la respuesta al problema que dej anotado en la version de consola
``v82_colas_con_prioridad``:

    PROBLEMA: la prioridad estricta deja desatendidas las colas de menor
              prioridad -> inanicion (starvation).
    SOLUCION: Round Robin. Se alternan los turnos entre las colas.

Las dos variantes del enunciado se implementan con el **mismo** codigo:

* Round Robin puro      -> pesos (1, 1, 1) -> ciclo (deudas, contado, credito)
* Round Robin ponderado -> pesos (3, 2, 1) -> ciclo (deudas, deudas, deudas,
                                                     contado, contado, credito)

La ponderacion no agrupa los turnos de una cola en bloques, porque eso volveria
a introducir inanicion en las colas del final. Los turnos se intercalan dentro
del ciclo y el ciclo se repite.
"""

from __future__ import annotations

from collections.abc import Collection, Mapping
from types import MappingProxyType

from ..enums import TipoTramite
from ..exceptions import PoliticaDeRotacionInvalidaError
from .planificador import Planificador, Turno

#: Pesos del enunciado: 3 atenciones de pago de deudas, 2 de contado y
#: 1 de solicitud de credito por vuelta completa del ciclo.
PESOS_POR_DEFECTO: Mapping[TipoTramite, int] = MappingProxyType(
    {
        TipoTramite.PAGO_DEUDAS: 3,
        TipoTramite.COMPRA_DE_CONTADO: 2,
        TipoTramite.SOLICITUD_CREDITO: 1,
    }
)

#: Round Robin sin ponderar: un turno por cola.
PESOS_ROUND_ROBIN_PURO: Mapping[TipoTramite, int] = MappingProxyType(
    {tipo: 1 for tipo in TipoTramite}
)


def generar_ciclo(pesos: Mapping[TipoTramite, int]) -> tuple[TipoTramite, ...]:
    """Construye la secuencia de turnos a partir de los pesos.

    Args:
        pesos: cuantas turnos le tocan a cada tipo de tramite.

    Returns:
        El ciclo, con cada tipo repetido segun su peso.

    Raises:
        PoliticaDeRotacionInvalidaError: si falta algun tipo, sobran tipos
            desconocidos o algun peso es menor que 1 (un peso 0 haria que esa
            cola nunca se atendiera, que es justamente inanicion).
    """
    faltantes = set(TipoTramite) - set(pesos)
    sobrantes = set(pesos) - set(TipoTramite)

    if faltantes:
        raise PoliticaDeRotacionInvalidaError(
            f"faltan pesos para: {', '.join(sorted(str(t) for t in faltantes))}"
        )
    if sobrantes:
        raise PoliticaDeRotacionInvalidaError(
            f"tipos de tramite desconocidos: {', '.join(sorted(str(t) for t in sobrantes))}"
        )

    invalidos = {tipo: peso for tipo, peso in pesos.items() if peso < 1}
    if invalidos:
        detalle = ", ".join(f"{tipo}={peso}" for tipo, peso in sorted(invalidos.items()))
        raise PoliticaDeRotacionInvalidaError(
            f"los pesos deben ser mayores o iguales a 1: {detalle}"
        )

    return tuple(
        tipo
        for tipo in sorted(pesos, key=int)  # se ordena por valor: 0, 1, 2
        for _ in range(pesos[tipo])
    )


class PoliticaRoundRobin(Planificador):
    """Rotacion de turnos con ponderacion.

    Sin estado: recibe los tipos que tienen gente y la posicion del ciclo, y
    devuelve el turno. El ciclo tiene siempre el mismo numero de posiciones,
    asi que planear es O(1) respecto al numero de usuarios.

    Invariante de no inanicion: si un tipo de tramite tiene usuarios en cola,
    se atiende a alguno de ellos en menos de ``longitud_ciclo`` turnos, sin
    importar cuantos usuarios haya en las otras colas.
    """

    def __init__(self, pesos: Mapping[TipoTramite, int] = PESOS_POR_DEFECTO) -> None:
        self._pesos = dict(pesos)
        self._ciclo = generar_ciclo(self._pesos)

    @property
    def nombre(self) -> str:
        return "round-robin-ponderado" if self._es_ponderada else "round-robin"

    @property
    def pesos(self) -> dict[TipoTramite, int]:
        return dict(self._pesos)

    @property
    def ciclo(self) -> tuple[TipoTramite, ...]:
        return self._ciclo

    def __repr__(self) -> str:
        return f"PoliticaRoundRobin(ciclo={self._ciclo})"

    @property
    def _es_ponderada(self) -> bool:
        return len(set(self._pesos.values())) > 1

    def planear(
        self,
        tipos_ocupados: Collection[TipoTramite],
        posicion_actual: int,
    ) -> Turno | None:
        if not tipos_ocupados:
            return None

        longitud = len(self._ciclo)
        posicion = posicion_actual % longitud

        # El recorrido esta acotado por el largo del ciclo: asi se saltan las
        # colas vacias y, si estan todas vacias, se sale sin ciclo infinito.
        for _ in range(longitud):
            tipo = self._ciclo[posicion]
            posicion = (posicion + 1) % longitud
            if tipo in tipos_ocupados:
                return Turno(tipo, posicion)

        return None  # pragma: no cover - solo si tipos_ocupados no coincide con el ciclo