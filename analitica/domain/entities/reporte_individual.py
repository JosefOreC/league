"""
Entidad de dominio: ReporteIndividual
Representa el reporte de desempeño de un equipo en un torneo.
No contiene decoradores ORM ni dependencias de infraestructura.
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ResultadoPartido:
    """Resultado de un partido para el equipo analizado."""
    partido_id: str
    ronda: int
    rival_id: str
    rival_nombre: str
    puntaje_equipo: float
    puntaje_rival: float
    ganador_id: Optional[str]
    es_victoria: bool
    fecha_programada: Optional[str]  # ISO string


@dataclass
class DetalleCriterio:
    """Estadísticas de un criterio de evaluación para el equipo."""
    criterio_id: str
    criterio_nombre: str
    peso: float
    promedio_equipo: float
    maximo_equipo: float
    minimo_equipo: float
    promedio_torneo: float          # Promedio global del torneo para el mismo criterio
    comparativa_vs_promedio: float  # (promedio_equipo - promedio_torneo) / promedio_torneo * 100


@dataclass
class EvolucionRonda:
    """Puntaje acumulado del equipo en cada ronda."""
    ronda: int
    puntaje_ronda: float
    puntaje_acumulado: float


@dataclass
class ReporteIndividual:
    """
    Reporte de desempeño individual de un equipo en el torneo.
    Todos los campos son calculados en tiempo de consulta — no persiste en BD.
    """
    torneo_id: str
    torneo_nombre: str
    equipo_id: str
    equipo_nombre: str
    categoria: str
    institucion_nombre: str
    posicion_final: Optional[int]
    medalla: Optional[str]
    puntaje_total_acumulado: float
    promedio_puntaje_torneo: float
    comparativa_vs_promedio_torneo: float   # % de desviación respecto al promedio global
    partidos: list[ResultadoPartido] = field(default_factory=list)
    detalle_criterios: list[DetalleCriterio] = field(default_factory=list)
    evolucion_por_ronda: list[EvolucionRonda] = field(default_factory=list)
    total_partidos_jugados: int = 0
    victorias: int = 0
    derrotas: int = 0
