"""Errores del dominio.

La capa de presentacion es la unica que traduce estas excepciones a codigos
HTTP. El dominio no sabe que existe HTTP.
"""

from __future__ import annotations


class ErrorDelDominio(Exception):
    """Base de todos los errores de negocio."""


class DatosInvalidosError(ErrorDelDominio):
    """Los datos de entrada no cumplen las reglas del negocio."""


class TipoDeTramiteInvalidoError(ErrorDelDominio):
    """El tipo de tramite no corresponde a ningun tipo conocido."""


class ColaVaciaError(ErrorDelDominio):
    """No hay ningun usuario encolado, no hay turno que atender ni consultar."""


class UsuarioNoEncontradoError(ErrorDelDominio):
    """El id indicado no corresponde a ningun usuario encolado."""


class PoliticaDeRotacionInvalidaError(ErrorDelDominio):
    """La configuracion de pesos no permite construir un ciclo de rotacion."""