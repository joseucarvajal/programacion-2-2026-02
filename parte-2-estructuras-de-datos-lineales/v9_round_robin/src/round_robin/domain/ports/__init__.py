"""Puertos del dominio: las interfaces que implementa la infraestructura."""

from .cola_turnos import ColaTurnosPort, EstadoDeColas, SiguienteEnCola, TurnoAtendido

__all__ = ["ColaTurnosPort", "EstadoDeColas", "SiguienteEnCola", "TurnoAtendido"]