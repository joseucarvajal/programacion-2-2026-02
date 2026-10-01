"""Pruebas de la politica de rotacion.

La politica es pura y no toca infraestructura, asi que estas pruebas son
rapidas y no necesitan ningun dato de entrada.
"""

from __future__ import annotations

from itertools import combinations_with_replacement

import pytest

from round_robin.domain.enums import TipoTramite
from round_robin.domain.exceptions import PoliticaDeRotacionInvalidaError
from round_robin.domain.plan import (
    PESOS_POR_DEFECTO,
    PESOS_ROUND_ROBIN_PURO,
    PoliticaRoundRobin,
    generar_ciclo,
)

T = TipoTramite
DEUDAS, CONTADO, CREDITO = T.PAGO_DEUDAS, T.COMPRA_DE_CONTADO, T.SOLICITUD_CREDITO


# ---------------------------------------------------------------- generacion


def test_ciclo_ponderado_intercala_en_vez_de_agrupar():
    """(3,2,1) no debe ser 'tres deudas, dos contado, un credito' seguidos.

    Si agrupara, las colas del final volverian a sufrir inanicion, que es
    justamente el problema que se quiere resolver.
    """
    assert PoliticaRoundRobin().ciclo == (DEUDAS, DEUDAS, DEUDAS, CONTADO, CONTADO, CREDITO)


def test_round_robin_puro_es_la_misma_politica_con_pesos_iguales():
    pura = PoliticaRoundRobin(PESOS_ROUND_ROBIN_PURO)
    assert pura.ciclo == (DEUDAS, CONTADO, CREDITO)
    assert pura.longitud_ciclo == 3


def test_el_ciclo_respeta_los_pesos():
    politica = PoliticaRoundRobin()
    for tipo, peso in PESOS_POR_DEFECTO.items():
        assert politica.ciclo.count(tipo) == peso


@pytest.mark.parametrize(
    "pesos",
    [
        {DEUDAS: 3, CONTADO: 2},  # falta el credito
        {DEUDAS: 3, CONTADO: 2, CREDITO: 0},  # peso 0 = inanicion garantizada
        {DEUDAS: 3, CONTADO: 2, CREDITO: 1, "otro": 1},  # tipo desconocido
    ],
)
def test_pesos_invalidos_se_rechazan(pesos):
    with pytest.raises(PoliticaDeRotacionInvalidaError):
        generar_ciclo(pesos)


# ------------------------------------------------------------------ planear


def _secuencia(politica, ocupados, turnos, posicion_inicial=0):
    """Corre la rotacion ``turnos`` veces y devuelve los tipos atendidos."""
    vistos, posicion = [], posicion_inicial
    for _ in range(turnos):
        turno = politica.planear(set(ocupados), posicion)
        if turno is None:
            break
        vistos.append(turno.tipo_tramite)
        posicion = turno.posicion_siguiente
    return vistos


def test_secuencia_ponderada_con_las_tres_colas_ocupadas():
    esperada = [DEUDAS, DEUDAS, DEUDAS, CONTADO, CONTADO, CREDITO] * 2
    assert _secuencia(PoliticaRoundRobin(), (DEUDAS, CONTADO, CREDITO), 12) == esperada


def test_secuencia_pura_alterna_las_tres_colas():
    assert _secuencia(
        PoliticaRoundRobin(PESOS_ROUND_ROBIN_PURO), (DEUDAS, CONTADO, CREDITO), 6
    ) == [DEUDAS, CONTADO, CREDITO] * 2


def test_el_credito_no_puede_quedarse_esperando_entre_tantos_de_deudas():
    """El caso concreto de inanicion que se quiere eliminar."""
    politica = PoliticaRoundRobin()
    # Solo deuda y credito, y la deuda nunca se queda vacia.
    atendidos = _secuencia(politica, (DEUDAS, CREDITO), 12)
    assert CREDITO in atendidos
    #Aparece una vez por vuelta del ciclo.
    assert atendidos.count(CREDITO) == 3


def test_las_colas_vacias_se_saltan():
    atendidos = _secuencia(PoliticaRoundRobin(), (DEUDAS, CREDITO), 12)
    # El contado no tiene gente: sus dos turnos del ciclo se desperdician y el
    # credito aparece una vez por vuelta.
    assert CONTADO not in atendidos
    assert atendidos == [DEUDAS, DEUDAS, DEUDAS, CREDITO] * 3


def test_solo_una_cola_ocupada_sigue_rotando():
    assert _secuencia(PoliticaRoundRobin(), (CREDITO,), 4) == [CREDITO] * 4


def test_sin_colas_ocupadas_no_hay_turno():
    assert PoliticaRoundRobin().planear(set(), 0) is None


def test_la_posicion_del_ciclo_se_respeta():
    """Empezar en otra posicion del ciclo cambia el orden, no la periodicidad."""
    politica = PoliticaRoundRobin()
    # Desde la posicion 4 (que es un turno de contado) el ciclo sigue igual.
    assert _secuencia(politica, (DEUDAS, CONTADO, CREDITO), 6, posicion_inicial=4) == [
        CONTADO,
        CREDITO,
        DEUDAS,
        DEUDAS,
        DEUDAS,
        CONTADO,
    ]


# ------------------------------------------------- invariante de no inanicion


def test_no_hay_inanicion_en_ninguna_combinacion_posible():
    """La garantia formal: si un tipo tiene gente, se atiende en menos de
    una vuelta completa del ciclo.

    Se recorren todos los subconjuntos posibles de colas ocupadas y todas las
    posiciones de inicio. No hace falta variar cuantos usuarios hay en cada
    cola: la politica no mira la cantidad, solo si la cola tiene alguno.
    """
    politica = PoliticaRoundRobin()
    longitud = len(politica.ciclo)

    for cantidad in range(len(TipoTramite) + 1):
        for ocupados in combinations_with_replacement(TipoTramite, cantidad):
            for posicion_inicial in range(longitud):
                atendidos = _secuencia(politica, ocupados, longitud, posicion_inicial)
                for tipo in ocupados:
                    assert tipo in atendidos, (
                        f"inanicion: {tipo} no se atendio en {longitud} turnos "
                        f"(ocupados={ocupados}, posicion={posicion_inicial})"
                    )
                if not ocupados:
                    assert atendidos == []