"""Pruebas de la API con ``TestClient``.

Aqui se verifica el contrato HTTP completo: codigos de estado, forma de las
respuestas, equivalencia de las excepciones de dominio con sus codigos, y que
la documentacion de Swagger este disponible para el frontend.

Se usa el cableado real (punto de composicion, lifespan, casos de uso) pero
contra una base SQLite temporal. Es mas valioso que sustituir el repositorio
con ``dependency_overrides``, porque asi tambien se prueba que el montaje
completo funciona.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from round_robin.domain.enums import TipoTramite
from round_robin.presentation import dependencies as deps
from round_robin.presentation.app import crear_aplicacion

T = TipoTramite
DEUDAS, CONTADO, CREDITO = T.PAGO_DEUDAS, T.COMPRA_DE_CONTADO, T.SOLICITUD_CREDITO

# Los pesos de cada tipo de tramite (0, 1, 2) y el ciclo que generan.
PESOS = (3, 2, 1)
CICLO = (0, 0, 0, 1, 1, 2)


@pytest.fixture
def cliente(tmp_path, monkeypatch) -> TestClient:
    # Cuatro barras: ruta absoluta (tres serian relativas).
    monkeypatch.setenv("DATABASE_URL", f"sqlite:////{tmp_path}/api.db")
    deps.limpiar_cache_dependencias()  # que la app tome la recien puesta

    app = crear_aplicacion()
    with TestClient(app) as cliente:
        yield cliente

    deps.limpiar_cache_dependencias()


def _registrar(cliente: TestClient, nombre: str, tipo: T, monto: float = 1000.0) -> dict:
    respuesta = cliente.post(
        "/api/v1/colas/usuarios",
        json={"nombre": nombre, "tipo_tramite": int(tipo), "monto_transaccion": monto},
    )
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


def _llenar(cliente: TestClient, distribution: dict[T, int]) -> None:
    for tipo, cantidad in distribution.items():
        for numero in range(cantidad):
            _registrar(cliente, f"{tipo.name}-{numero}", tipo)


# ------------------------------------------------------------------ documentacion


def test_swagger_esta_disponible(cliente):
    respuesta = cliente.get("/docs")
    assert respuesta.status_code == 200
    assert "swagger" in respuesta.text.lower()


def test_openapi_describe_todos_los_endpoints(cliente):
    esquema = cliente.get("/openapi.json").json()

    assert "/api/v1/colas/usuarios" in esquema["paths"]
    assert "/api/v1/colas/atender" in esquema["paths"]
    assert "/api/v1/colas/siguiente" in esquema["paths"]
    assert "/api/v1/colas" in esquema["paths"]
    assert "/api/v1/colas/configuracion" in esquema["paths"]


def test_health_reporta_la_politica(cliente):
    respuesta = cliente.get("/api/v1/health")
    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "estado": "ok",
        "politica": "round-robin-ponderado",
        "longitud_ciclo": 6,
    }


# ------------------------------------------------------------------- registrar


def test_registrar_devuelve_201_con_el_usuario(cliente):
    cuerpo = _registrar(cliente, "Ana Torres", DEUDAS, 250000.0)

    assert cuerpo["id"] >= 1
    assert cuerpo["nombre"] == "Ana Torres"
    assert cuerpo["tipo_tramite"] == 0
    assert cuerpo["tipo_tramite_descripcion"] == "pago de deudas"
    assert cuerpo["monto_transaccion"] == 250000.0


@pytest.mark.parametrize(
    "cuerpo",
    [
        {"nombre": "", "tipo_tramite": 0, "monto_transaccion": 100},
        {"nombre": "Ana", "tipo_tramite": 7, "monto_transaccion": 100},
        {"nombre": "Ana", "tipo_tramite": 0, "monto_transaccion": -1},
        {"tipo_tramite": 0, "monto_transaccion": 100},
    ],
)
def test_registrar_rechaza_datos_invalidos_con_422(cliente, cuerpo):
    respuesta = cliente.post("/api/v1/colas/usuarios", json=cuerpo)
    assert respuesta.status_code == 422


# --------------------------------------------------------------------- atender


def test_atender_con_colas_vacias_devuelve_409(cliente):
    respuesta = cliente.post("/api/v1/colas/atender")
    assert respuesta.status_code == 409
    assert respuesta.json()["codigo"] == "ColaVaciaError"


def test_atender_devuelve_quien_fue_atendido(cliente):
    _llenar(cliente, {DEUDAS: 2})

    respuesta = cliente.post("/api/v1/colas/atender")

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["usuario"]["nombre"] == "PAGO_DEUDAS-0"
    assert cuerpo["tipo_tramite"] == 0
    assert cuerpo["posicion_ciclo_anterior"] == 0
    assert cuerpo["posicion_ciclo_siguiente"] == 1
    assert cuerpo["longitud_ciclo"] == 6


def test_atender_sigue_el_ciclo_ponderado(cliente):
    _llenar(cliente, {DEUDAS: 3, CONTADO: 2, CREDITO: 1})

    atendidos = [cliente.post("/api/v1/colas/atender").json()["tipo_tramite"] for _ in range(6)]

    assert atendidos == list(CICLO)


def test_la_rotacion_completa_es_justa(cliente):
    """Reparto ponderado en un lote: 3 deudas, 2 contado, 1 credito."""
    _llenar(cliente, {DEUDAS: 30, CONTADO: 20, CREDITO: 10})

    atendidos = [cliente.post("/api/v1/colas/atender").json()["tipo_tramite"] for _ in range(60)]

    assert atendidos.count(0) == 30
    assert atendidos.count(1) == 20
    assert atendidos.count(2) == 10
    assert atendidos[:6] == [0, 0, 0, 1, 1, 2]


def test_nadie_se_atiende_dos_veces(cliente):
    _llenar(cliente, {DEUDAS: 4, CONTADO: 2, CREDITO: 1})

    ids = [
        cliente.post("/api/v1/colas/atender").json()["usuario"]["id"] for _ in range(7)
    ]

    assert len(set(ids)) == 7


# ------------------------------------------------------------------ siguiente


def test_siguiente_con_colas_vacias_devuelve_409(cliente):
    assert cliente.get("/api/v1/colas/siguiente").status_code == 409


def test_siguiente_no_consume_al_usuario(cliente):
    _llenar(cliente, {DEUDAS: 2})

    # Consultar varias veces no debe mover nada.
    for _ in range(3):
        cuerpo = cliente.get("/api/v1/colas/siguiente").json()
        assert cuerpo["usuario"]["nombre"] == "PAGO_DEUDAS-0"
        assert cuerpo["posicion_ciclo"] == 1  # lo que seria, sin aplicarlo

    estado = cliente.get("/api/v1/colas").json()
    assert estado["total_usuarios"] == 2
    assert estado["posicion_ciclo"] == 0


# --------------------------------------------------------------------- estado


def test_estado_devuelve_las_tres_colas(cliente):
    _llenar(cliente, {DEUDAS: 2, CREDITO: 1})

    estado = cliente.get("/api/v1/colas").json()

    assert [cola["tipo_tramite"] for cola in estado["colas"]] == [0, 1, 2]
    assert [cola["peso"] for cola in estado["colas"]] == list(PESOS)
    assert estado["total_usuarios"] == 3
    assert estado["total_montos"] == 3000.0
    assert estado["longitud_ciclo"] == 6
    assert estado["colas"][0]["total"] == 2
    assert estado["colas"][1]["total"] == 0


def test_configuracion_expone_el_ciclo(cliente):
    configuracion = cliente.get("/api/v1/colas/configuracion").json()

    assert configuracion["politica"] == "round-robin-ponderado"
    assert configuracion["ciclo"] == [0, 0, 0, 1, 1, 2]
    assert configuracion["longitud_ciclo"] == 6
    assert configuracion["posicion_ciclo"] == 0
    assert configuracion["espera_maxima_turnos"] == 6
    assert configuracion["ciclo_legible"][0] == "pago de deudas"


def test_la_configuracion_refleja_el_ciclo_avanzado(cliente):
    _llenar(cliente, {DEUDAS: 3})
    cliente.post("/api/v1/colas/atender")

    assert cliente.get("/api/v1/colas/configuracion").json()["posicion_ciclo"] == 1


# --------------------------------------------------------------- administrador


def test_retirar_un_usuario(cliente):
    objetivo = _registrar(cliente, "Ana", CONTADO)

    respuesta = cliente.delete(f"/api/v1/colas/usuarios/{objetivo['id']}")

    assert respuesta.status_code == 200
    assert respuesta.json()["nombre"] == "Ana"
    assert cliente.get("/api/v1/colas").json()["total_usuarios"] == 0


def test_retirar_un_id_inexistente_devuelve_404(cliente):
    respuesta = cliente.delete("/api/v1/colas/usuarios/999")
    assert respuesta.status_code == 404
    assert respuesta.json()["codigo"] == "UsuarioNoEncontradoError"


def test_reiniciar_vacia_todo(cliente):
    _llenar(cliente, {DEUDAS: 2})
    cliente.post("/api/v1/colas/atender")

    respuesta = cliente.post("/api/v1/colas/reiniciar")

    assert respuesta.status_code == 200
    estado = cliente.get("/api/v1/colas").json()
    assert estado["total_usuarios"] == 0
    assert estado["posicion_ciclo"] == 0