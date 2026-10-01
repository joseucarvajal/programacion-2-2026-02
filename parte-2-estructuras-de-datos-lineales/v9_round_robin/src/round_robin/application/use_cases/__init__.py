"""Casos de uso de la gestion de colas de la tienda.

Cada caso de uso es una clase pequena con un metodo ``execute()``, que recibe
sus dependencias por el constructor. No saben nada de HTTP ni de SQL: son
reutilizables desde un script, una linea de comandos o desde otro backend.
"""

from .atender_siguiente_usuario import AtenderSiguienteUsuario
from .configuracion_rotacion import ConsultarConfiguracionRotacion
from .consultar_estado_de_colas import ConsultarEstadoDeColas
from .consultar_siguiente_usuario import ConsultarSiguienteUsuario
from .registrar_usuario import RegistrarUsuarioEnCola
from .reiniciar_colas import ReiniciarColas
from .retirar_usuario import RetirarUsuario

__all__ = [
    "AtenderSiguienteUsuario",
    "ConsultarConfiguracionRotacion",
    "ConsultarEstadoDeColas",
    "ConsultarSiguienteUsuario",
    "RegistrarUsuarioEnCola",
    "ReiniciarColas",
    "RetirarUsuario",
]