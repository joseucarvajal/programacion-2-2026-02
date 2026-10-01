"""Pruebas de los casos de uso, sobre el repositorio en memoria.

Los casos de uso no saben si detras hay un deque o una tabla de SQLite, asi que
aqui se prueban rapido. La misma logica se vuelve a probar en
``tests/persistence/`` contra SQLite.
"""

from __future__ import annotations

import pytest

from round_robin.application.use_cases import (
    AtenderSiguienteUsuario,
    ConsultarConfiguracionRotacion,
    ConsultarEstadoDeColas,
    ConsultarSiguienteUsuario,
    RegistrarUsuarioEnCola,
    ReiniciarColas,
    RetirarUsuario,
)
from round_robin.domain.enums import TipoTramite
from round_robin.domain.exceptions import (
    ColaVaciaError,
    DatosInvalidosError,
    UsuarioNoEncontradoError,
)
from round_robin.domain.plan import PoliticaRoundRobin
from round_robin.domain.ports import ColaTurnosPort

T = TipoTramite


@pytest.fixture
def planificador() -> PoliticaRoundRobin:
    return PoliticaRoundRobin()


@pytest.fixture
def registrar(colas: ColaTurnosPort) -> RegistrarUsuarioEnCola:
    return RegistrarUsuarioEnCola(colas)


@pytest.fixture
def atender(colas, planificador) -> AtenderSiguienteUsuario:
    return AtenderSiguienteUsuario(colas, planificador)


@pytest.fixture
def consultar_siguiente(colas, planificador) -> ConsultarSiguienteUsuario:
    return ConsultarSiguienteUsuario(colas, planificador)


@pytest.fixture
def consultar_estado(colas, planificador) -> ConsultarEstadoDeColas:
    return ConsultarEstadoDeColas(colas, planificador)


@pytest.fixture
def retirar(colas) -> RetirarUsuario:
    return RetirarUsuario(colas)


@pytest.fixture
def reiniciar(colas) -> ReiniciarColas:
    return ReiniciarColas(colas)


def _llenar(registrar, distribution: dict[TipoTramite, int]) -> None:
    for tipo, cantidad in distribution.items():
        for numero in range(cantidad):
            registrar.execute(
                nombre=f"{tipo.name}-{numero}", tipo_tramite=tipo, monto_transaccion=100.0
            )


# ------------------------------------------------------------------ registro


def test_registrar_devuelve_el_usuario_con_id(registrar):
    usuario = registrar.execute("Ana Torres", T.PAGO_DEUDAS, 250000.0)
    assert usuario.id >= 1
    assert usuario.nombre == "Ana Torres"
    assert usuario.tipo_tramite is T.PAGO_DEUDAS


def test_registrar_normaliza_el_nombre(registrar):
    assert registrar.execute("   Ana   ", T.COMPRA_DE_CONTADO, 10).nombre == "Ana"


@pytest.mark.parametrize(
    "nombre, monto",
    [("", 100.0), ("   ", 100.0), ("Ana", -5.0)],
)
def test_registrar_rechaza_datos_invalidos(registrar, nombre, monto):
    with pytest.raises(DatosInvalidosError):
        registrar.execute(nombre, T.PAGO_DEUDAS, monto)


# ------------------------------------------------------------------- atención


def test_atender_sin_ningun_usuario_falla(atender):
    with pytest.raises(ColaVaciaError):
        atender.execute()


def test_atender_respeta_el_orden_de_llegada(registrar, atender, consultar_estado):
    _llenar(registrar, {T.PAGO_DEUDAS: 3, T.COMPRA_DE_CONTADO: 2})

    nombres = [atender.execute().usuario.nombre for _ in range(3)]

    # Las tres primeras posiciones del ciclo son de pago de deudas.
    assert nombres == ["PAGO_DEUDAS-0", "PAGO_DEUDAS-1", "PAGO_DEUDAS-2"]
    assert consultar_estado.execute().total_usuarios == 2


def test_atender_avanza_el_ciclo_y_lo_reporta(registrar, atender):
    _llenar(registrar, {T.PAGO_DEUDAS: 1, T.COMPRA_DE_CONTADO: 1, T.SOLICITUD_CREDITO: 1})

    primero = atender.execute()
    assert (primero.posicion_ciclo_anterior, primero.posicion_ciclo_siguiente) == (0, 1)
    assert primero.tipo_tramite is T.PAGO_DEUDAS

    # La cola de deudas ya se vacio, asi que el ciclo salta sus dos turnos
    # sobrantes: de la posicion 1 llega a la 4 (la primera de contado).
    segundo = atender.execute()
    assert (segundo.posicion_ciclo_anterior, segundo.posicion_ciclo_siguiente) == (1, 4)
    assert segundo.tipo_tramite is T.COMPRA_DE_CONTADO


def test_el_credito_termina_siendo_atendido(registrar, atender):
    """La prueba funcional del problema que se queria resolver."""
    _llenar(registrar, {T.PAGO_DEUDAS: 20, T.SOLICITUD_CREDITO: 1})

    atendidos = [atender.execute().tipo_tramite for _ in range(21)]

    assert atendidos.count(T.SOLICITUD_CREDITO) == 1
    # Aparece dentro de los primeros 6 turnos, no al final.
    assert T.SOLICITUD_CREDITO in atendidos[:6]


# ----------------------------------------------------------------- consultar


def test_consultar_siguiente_no_consume_el_turno(registrar, consultar_siguiente, atender):
    _llenar(registrar, {T.PAGO_DEUDAS: 2})

    visto = consultar_siguiente.execute()
    assert visto.usuario.nombre == "PAGO_DEUDAS-0"

    # Consultar dos veces mas no debe cambiar nada.
    assert consultar_siguiente.execute().usuario.nombre == "PAGO_DEUDAS-0"

    # Y el primer turno real sigue siendo el mismo usuario.
    assert atender.execute().usuario.nombre == "PAGO_DEUDAS-0"
    assert consultar_siguiente.execute().usuario.nombre == "PAGO_DEUDAS-1"


def test_consultar_siguiente_con_colas_vacias_falla(consultar_siguiente):
    with pytest.raises(ColaVaciaError):
        consultar_siguiente.execute()


def test_estado_devuelve_las_tres_colas_con_sus_totales(registrar, consultar_estado):
    _llenar(registrar, {T.PAGO_DEUDAS: 2, T.SOLICITUD_CREDITO: 1})

    estado = consultar_estado.execute()

    assert [cola.tipo_tramite for cola in estado.colas] == list(T)
    assert estado.total_usuarios == 3
    assert estado.total_montos == 300.0
    assert estado.longitud_ciclo == 6
    # Los pesos ordenan de mas a menos prioridad.
    assert [cola.peso for cola in estado.colas] == [3, 2, 1]


def test_configuracion_expone_el_ciclo(colas, planificador):
    config = ConsultarConfiguracionRotacion(colas, planificador).execute()

    assert config.politica == "round-robin-ponderado"
    assert config.longitud_ciclo == 6
    assert config.pesos == ((T.PAGO_DEUDAS, 3), (T.COMPRA_DE_CONTADO, 2), (T.SOLICITUD_CREDITO, 1))
    assert config.ciclo == (
        T.PAGO_DEUDAS,
        T.PAGO_DEUDAS,
        T.PAGO_DEUDAS,
        T.COMPRA_DE_CONTADO,
        T.COMPRA_DE_CONTADO,
        T.SOLICITUD_CREDITO,
    )


# --------------------------------------------------------------- adminustros


def test_retirar_saca_al_usuario_de_su_cola(registrar, retirar, consultar_estado):
    objetivo = registrar.execute("Ana", T.COMPRA_DE_CONTADO, 50.0)

    retirado = retirar.execute(objetivo.id)

    assert retirado.nombre == "Ana"
    assert consultar_estado.execute().total_usuarios == 0


def test_retirar_un_id_inexistente_falla(registrar, retirar):
    registrar.execute("Ana", T.COMPRA_DE_CONTADO, 50.0)
    with pytest.raises(UsuarioNoEncontradoError):
        retirar.execute(999)


def test_reiniciar_vacia_las_colas_y_el_ciclo(registrar, atender, consultar_estado, reiniciar):
    _llenar(registrar, {T.PAGO_DEUDAS: 3, T.COMPRA_DE_CONTADO: 1})
    atender.execute()
    atender.execute()

    reiniciar.execute()

    estado = consultar_estado.execute()
    assert estado.total_usuarios == 0
    assert estado.posicion_ciclo == 0