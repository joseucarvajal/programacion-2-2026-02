"""Aplicacion FastAPI. Interfaz de la tienda con rotacion Round Robin.

Se resuelve en cuatro capas:

    presentacion/  <- HTTP: routers, schemas, traduccion de errores
    application/   <- casos de uso: orquestan, no calculan
    domain/        <- entidades, politica de rotacion y puertos (puro)
    infrastructure/<- SQLite y configuracion (adaptadores)

La documentacion interactiva queda en /docs y el esquema OpenAPI en
/openapi.json, que es el contrato con el futuro frontend.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import dependencies as deps
from .errors import registrar_manejadores
from .routers.colas import router as router_colas
from .schemas import HealthResponse

DESCRIPCION_LARGA = """
API de las colas de atencion de una tienda.

La tienda tiene tres colas segun el tipo de tramite:

| `tipo_tramite` | Tramite                   | Peso |
|----------------|---------------------------|------|
| `0`            | Pago de deudas            | 3    |
| `1`            | Compra de contado         | 2    |
| `2`            | Solicitud de credito      | 1    |

Los pesos producen el ciclo de rotacion
`(deudas, deudas, deudas, contado, contado, credito)`.

Consecuencia: **ningun usuario espera mas de 6 turnos**, aunque no deje de
llegar gente con tramites de mayor prioridad. Ese es el problema de inanicion
que tenía la version de consola con prioridad estricta.
"""


@asynccontextmanager
async def ciclo_de_vida(_app: FastAPI) -> AsyncIterator[None]:
    """Crea el esquema al arrancar, antes de recibir la primera peticion."""
    deps.obtener_fabrica_sqlite().inicializar_esquema()
    yield


def crear_aplicacion() -> FastAPI:
    """Fabrica de la aplicacion (patron habitual en FastAPI)."""
    configuracion = deps.obtener_configuracion()

    app = FastAPI(
        title=configuracion.titulo,
        description=DESCRIPCION_LARGA,
        version=configuracion.version,
        lifespan=ciclo_de_vida,
        openapi_tags=[
            {"name": "colas", "description": "Administracion de las colas de la tienda."},
        ],
    )

    # El frontend va en otro origen durante el desarrollo.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(configuracion.cors_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    registrar_manejadores(app)
    app.include_router(router_colas, prefix="/api/v1")

    @app.get("/api/v1/health", response_model=HealthResponse, tags=["salud"])
    def health() -> HealthResponse:
        planificador = deps.obtener_planificador()
        return HealthResponse(
            estado="ok",
            politica=planificador.nombre,
            longitud_ciclo=planificador.longitud_ciclo,
        )

    return app


app = crear_aplicacion()