from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class PosicionEquipo:
    equipo_id: str
    nombre_equipo: str
    posicion_final: int
    puntaje_acumulado: float


@dataclass(frozen=True)
class ReporteInstitucional:
    institucion_id: str
    nombre_institucion: str
    tipo: str                           # PUBLICA | PRIVADA | CONCERTADA
    torneo_id: str
    total_equipos_participantes: int
    posiciones_obtenidas: list
    puntaje_promedio_institucional: float
    mejor_posicion_lograda: int
    criterio_mas_destacado: str


@dataclass(frozen=True)
class EntradaHistorico:
    torneo_id: str
    nombre_torneo: str
    fecha: str
    equipos: int
    puntaje_promedio: float
    mejor_posicion: int


@dataclass(frozen=True)
class ReporteInstitucionalHistorico:
    institucion_id: str
    nombre_institucion: str
    tipo: str
    evolucion: list
