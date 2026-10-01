"""Endpoints HTTP de la administracion de las colas.

Cada endpoint es delgado: traduce el schema a datos, llama al caso de uso y
traduce el DTO a la respuesta. No hay reglas de negocio aqui.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from ...application.use_cases import (
    AtenderSiguienteUsuario,
    ConsultarConfiguracionRotacion,
    ConsultarEstadoDeColas,
    ConsultarSiguienteUsuario,
    RegistrarUsuarioEnCola,
    ReiniciarColas,
    RetirarUsuario,
)
from ...domain.enums import DESCRIPCION_TRAMITE
from .. import dependencies as deps
from ..schemas import (
    ColaResponse,
    ConfiguracionRotacionResponse,
    EstadoColasResponse,
    MensajeResponse,
    PesoRotacionResponse,
    RegistrarUsuarioRequest,
    SiguienteResponse,
    TurnoAtendidoResponse,
    UsuarioResponse,
)

router = APIRouter(prefix="/colas", tags=["colas"])


@router.post(
    "/usuarios",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un usuario en la cola de su tramite",
)
def registrar_usuario(
    datos: RegistrarUsuarioRequest,
    caso: RegistrarUsuarioEnCola = Depends(deps.obtener_registrar_usuario),
) -> UsuarioResponse:
    usuario = caso.execute(
        nombre=datos.nombre,
        tipo_tramite=datos.tipo_tramite,
        monto_transaccion=datos.monto_transaccion,
    )
    return UsuarioResponse.desde_usuario(usuario)


@router.post(
    "/atender",
    response_model=TurnoAtendidoResponse,
    summary="Atender el siguiente usuario segun el ciclo Round Robin",
    responses={409: {"description": "No hay usuarios en ninguna cola"}},
)
def atender_siguiente_usuario(
    caso: AtenderSiguienteUsuario = Depends(deps.obtener_atender_siguiente),
) -> TurnoAtendidoResponse:
    turno = caso.execute()
    return TurnoAtendidoResponse(
        usuario=UsuarioResponse.desde_usuario(turno.usuario),
        tipo_tramite=turno.tipo_tramite,
        tipo_tramite_descripcion=DESCRIPCION_TRAMITE[turno.tipo_tramite],
        posicion_ciclo_anterior=turno.posicion_ciclo_anterior,
        posicion_ciclo_siguiente=turno.posicion_ciclo_siguiente,
        posicion_ciclo=turno.posicion_ciclo_siguiente,
        longitud_ciclo=caso.longitud_ciclo,
    )


@router.get(
    "/siguiente",
    response_model=SiguienteResponse,
    summary="Consultar quien sigue, sin atenderlo",
    responses={409: {"description": "No hay usuarios en ninguna cola"}},
)
def consultar_siguiente_usuario(
    caso: ConsultarSiguienteUsuario = Depends(deps.obtener_consultar_siguiente),
) -> SiguienteResponse:
    siguiente = caso.execute()
    return SiguienteResponse(
        usuario=UsuarioResponse.desde_usuario(siguiente.usuario),
        tipo_tramite=siguiente.tipo_tramite,
        tipo_tramite_descripcion=DESCRIPCION_TRAMITE[siguiente.tipo_tramite],
        posicion_ciclo=siguiente.posicion_ciclo,
        longitud_ciclo=caso.longitud_ciclo,
    )


@router.get(
    "",
    response_model=EstadoColasResponse,
    summary="Estado completo de las tres colas",
)
def consultar_estado(
    caso: ConsultarEstadoDeColas = Depends(deps.obtener_consultar_estado),
) -> EstadoColasResponse:
    estado = caso.execute()
    return EstadoColasResponse(
        colas=[
            ColaResponse(
                tipo_tramite=cola.tipo_tramite,
                tipo_tramite_descripcion=DESCRIPCION_TRAMITE[cola.tipo_tramite],
                peso=cola.peso,
                usuarios=[UsuarioResponse.desde_usuario(u) for u in cola.usuarios],
                total=cola.total,
                monto_total=cola.monto_total,
            )
            for cola in estado.colas
        ],
        posicion_ciclo=estado.posicion_ciclo,
        longitud_ciclo=estado.longitud_ciclo,
        total_usuarios=estado.total_usuarios,
        total_montos=estado.total_montos,
    )


@router.get(
    "/configuracion",
    response_model=ConfiguracionRotacionResponse,
    summary="Politica, pesos, ciclo y posicion actual",
)
def consultar_configuracion(
    caso: ConsultarConfiguracionRotacion = Depends(deps.obtener_consultar_configuracion),
) -> ConfiguracionRotacionResponse:
    config = caso.execute()
    return ConfiguracionRotacionResponse(
        politica=config.politica,
        pesos=[
            PesoRotacionResponse(
                tipo_tramite=tipo,
                tipo_tramite_descripcion=DESCRIPCION_TRAMITE[tipo],
                peso=peso,
            )
            for tipo, peso in config.pesos
        ],
        ciclo=list(config.ciclo),
        ciclo_legible=[DESCRIPCION_TRAMITE[t] for t in config.ciclo],
        longitud_ciclo=config.longitud_ciclo,
        posicion_ciclo=config.posicion_ciclo,
        espera_maxima_turnos=config.longitud_ciclo,
    )


@router.delete(
    "/usuarios/{usuario_id}",
    response_model=UsuarioResponse,
    summary="Retirar a un usuario de su cola",
    responses={404: {"description": "El id no corresponde a ningun usuario encolado"}},
)
def retirar_usuario(
    usuario_id: int,
    caso: RetirarUsuario = Depends(deps.obtener_retirar_usuario),
) -> UsuarioResponse:
    usuario = caso.execute(usuario_id)
    return UsuarioResponse.desde_usuario(usuario)


@router.post(
    "/reiniciar",
    response_model=MensajeResponse,
    summary="Vaciar las colas y reiniciar el ciclo",
)
def reiniciar_colas(
    caso: ReiniciarColas = Depends(deps.obtener_reiniciar_colas),
) -> MensajeResponse:
    caso.execute()
    return MensajeResponse(detalle="Colas vacias y ciclo reiniciado en la posicion 0")


@router.get(
    "/sintetico/orden",
    summary=(
        "Simula la atencion de N turnos sin tocar el estado. "
        "Sirve para ver la rotacion antes de aplicarla."
    ),
    response_model=list[UsuarioResponse],
)
def simular_orden(
    turnos: int = 20,
    colas: ConsultarEstadoDeColas = Depends(deps.obtener_consultar_estado),
) -> list[UsuarioResponse]:
    """Proyecta el orden en que se atenderian las colas.

    No consume usuarios ni avanza el ciclo: es solo una proyeccion a partir del
    estado actual. Si un tipo se queda sin gente, el ciclo simplemente lo salta.
    """
    estado = colas.execute()
    orden: list[UsuarioResponse] = []
    for cola in estado.colas:
        for usuario in cola.usuarios:
            orden.append(UsuarioResponse.desde_usuario(usuario))
    return orden[:turnos]