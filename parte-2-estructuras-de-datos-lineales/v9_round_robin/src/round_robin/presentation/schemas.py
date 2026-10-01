"""Modelos de la API. El **unico** lugar donde aparece Pydantic.

El dominio y los casos de uso no saben que existen estas clases; los routers
traducen de schema a DTO y de vuelta.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from ..domain.enums import DESCRIPCION_TRAMITE, TipoTramite

DESCRIPCIONES_SEGUN_TIPO: dict[TipoTramite, str] = {
    TipoTramite.PAGO_DEUDAS: "Pago de deudas (mayor prioridad)",
    TipoTramite.COMPRA_DE_CONTADO: "Compra de contado",
    TipoTramite.SOLICITUD_CREDITO: "Solicitud de credito (se fia)",
}


class RegistrarUsuarioRequest(BaseModel):
    """Datos para dar de alta a un usuario en la cola."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"nombre": "Ana Torres", "tipo_tramite": 0, "monto_transaccion": 250000.0}
            ]
        }
    )

    nombre: str = Field(min_length=1, max_length=120, examples=["Ana Torres"])
    # El dominio ya es un IntEnum (0, 1, 2), asi que Swagger muestra sola los
    # valores permitidos. Solo hace falta documentarlos.
    tipo_tramite: TipoTramite = Field(
        description=" | ".join(
            f"{int(tipo)}: {texto}" for tipo, texto in DESCRIPCIONES_SEGUN_TIPO.items()
        ),
        examples=[0],
    )
    monto_transaccion: float = Field(ge=0, examples=[250000.0])


class UsuarioResponse(BaseModel):
    """Usuario encolado, tal como lo devuelve la API."""

    id: int = Field(description="Identificador unico, tambien es el orden de llegada")
    nombre: str
    tipo_tramite: TipoTramite
    tipo_tramite_descripcion: str
    monto_transaccion: float
    creado_en: datetime

    @classmethod
    def desde_usuario(cls, usuario) -> UsuarioResponse:
        return cls(
            id=usuario.id,
            nombre=usuario.nombre,
            tipo_tramite=usuario.tipo_tramite,
            tipo_tramite_descripcion=DESCRIPCION_TRAMITE[usuario.tipo_tramite],
            monto_transaccion=usuario.monto_transaccion,
            creado_en=usuario.creado_en,
        )


class TurnoAtendidoResponse(BaseModel):
    """Resultado de ejecutar un turno: el usuario ya salio de la cola."""

    usuario: UsuarioResponse
    tipo_tramite: TipoTramite
    tipo_tramite_descripcion: str
    posicion_ciclo_anterior: int
    posicion_ciclo_siguiente: int
    posicion_ciclo: int = Field(description="Posicion actual del ciclo tras el turno")
    longitud_ciclo: int


class SiguienteResponse(BaseModel):
    """Consulta del proximo turno. El usuario sigue esperando."""

    usuario: UsuarioResponse
    tipo_tramite: TipoTramite
    tipo_tramite_descripcion: str
    posicion_ciclo: int = Field(description="Posicion que tendria el ciclo si se atendiera")
    longitud_ciclo: int


class ColaResponse(BaseModel):
    """Una de las tres colas."""

    tipo_tramite: TipoTramite
    tipo_tramite_descripcion: str
    peso: int = Field(description="Turnos por vuelta del ciclo segun la ponderacion")
    usuarios: list[UsuarioResponse]
    total: int
    monto_total: float


class EstadoColasResponse(BaseModel):
    """Fotografia completa de la tienda."""

    colas: list[ColaResponse]
    posicion_ciclo: int
    longitud_ciclo: int
    total_usuarios: int
    total_montos: float


class PesoRotacionResponse(BaseModel):
    tipo_tramite: TipoTramite
    tipo_tramite_descripcion: str
    peso: int


class ConfiguracionRotacionResponse(BaseModel):
    """Como esta configurada la rotacion ahora mismo."""

    politica: str
    pesos: list[PesoRotacionResponse]
    ciclo: list[TipoTramite]
    ciclo_legible: list[str] = Field(
        description="El ciclo escrito con nombres, util para mostrarlo en la interfaz"
    )
    longitud_ciclo: int
    posicion_ciclo: int
    espera_maxima_turnos: int = Field(
        description=(
            "Turnos que puede esperar como maximo un usuario antes de ser "
            "atendido. Es la garantia de que no hay inanicion."
        )
    )


class MensajeResponse(BaseModel):
    detalle: str


class HealthResponse(BaseModel):
    estado: str
    politica: str
    longitud_ciclo: int