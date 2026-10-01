"""Traduccion de los errores del dominio a codigos HTTP.

Es el unico punto del proyecto que sabe de las dos cosas a la vez: la
excepcion de negocio y su equivalente en la web. El dominio lanza
``ColaVaciaError`` sin saber que existe el 409.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from ..domain.exceptions import (
    ColaVaciaError,
    DatosInvalidosError,
    ErrorDelDominio,
    PoliticaDeRotacionInvalidaError,
    TipoDeTramiteInvalidoError,
    UsuarioNoEncontradoError,
)

# Los errores de validacion del transporte (Pydantic) ya salen como 422, asi
# que los de negocio se distinguen por el campo "codigo" que se agrega aqui.


def registrar_manejadores(app: FastAPI) -> None:
    """Registra un manejador por cada error de negocio."""
    app.add_exception_handler(ColaVaciaError, _manejador(409))
    app.add_exception_handler(UsuarioNoEncontradoError, _manejador(404))
    app.add_exception_handler(TipoDeTramiteInvalidoError, _manejador(422))
    app.add_exception_handler(DatosInvalidosError, _manejador(422))
    app.add_exception_handler(PoliticaDeRotacionInvalidaError, _manejador(500))
    # Red de seguridad para cualquier error de dominio que se agregue despues.
    app.add_exception_handler(ErrorDelDominio, _manejador(400))


def _manejador(estado: int):
    def manejar(_request: Request, exc: ErrorDelDominio) -> JSONResponse:
        # Se mantiene "detail" para que el frontend pueda tratar igual los
        # errores de FastAPI y los de negocio.
        return JSONResponse(
            status_code=estado,
            content={"detail": str(exc), "codigo": type(exc).__name__},
        )

    return manejar