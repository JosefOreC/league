"""
Entidad de dominio: AnalisisIntegral
Representa el resultado calculado del análisis integral de un torneo.
No contiene decoradores ORM ni dependencias de infraestructura.
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DistribucionCriterio:
    """Distribución de puntajes por criterio de evaluación."""
    criterio_id: str
    criterio_nombre: str
    peso: float
    promedio: float
    maximo: float
    minimo: float
    desviacion_estandar: float


@dataclass
class EquipoResumen:
    """Resumen de un equipo (máximo o mínimo puntaje)."""
    equipo_id: str
    nombre: str
    puntaje_total: float
    posicion_final: Optional[int] = None
    medalla: Optional[str] = None


@dataclass
class AnalisisIntegral:
    """
    Resultado del análisis integral de un torneo.
    Todos los campos son calculados en tiempo de consulta — no persiste en BD.
    """
    torneo_id: str
    torneo_nombre: str
    total_equipos: int
    total_partidos: int
    puntaje_promedio_global: float
    desviacion_estandar_global: float
    puntaje_maximo: float
    puntaje_minimo: float
    equipo_max: EquipoResumen
    equipo_min: EquipoResumen
    distribucion_criterios: list[DistribucionCriterio] = field(default_factory=list)
    ranking_final: list[dict] = field(default_factory=list)
    categoria_filtrada: Optional[str] = None
