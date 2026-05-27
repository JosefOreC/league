"""
Entidades de dominio para HU-SIM-01 — Contexto de simulación del torneo.
Estas dataclasses son objetos de valor puros (sin ORM) que circulan entre
capas de aplicación e infraestructura siguiendo la arquitectura hexagonal.
"""
from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class TournamentInfo:
    """Información básica del torneo relevante para la simulación."""
    id: str
    name: str
    state: str
    category: str


@dataclass(frozen=True)
class TeamInfo:
    """Información básica del equipo del representante en el torneo."""
    id: str
    name: str
    nivel_tecnico_declarado: str
    participants_count: int


@dataclass(frozen=True)
class CriterioInfo:
    """Criterio de evaluación del torneo con su peso y rango de calificación."""
    id: str
    name: str
    description: str
    peso: float
    min_qualification: float
    max_qualification: float


@dataclass(frozen=True)
class SimulationContext:
    """
    Agregado de dominio para HU-SIM-01.
    Contiene todo el contexto necesario para que el motor de simulación
    opere sin acceder directamente a la base de datos.
    """
    tournament: TournamentInfo
    team: TeamInfo
    criterios: List[CriterioInfo] = field(default_factory=list)
