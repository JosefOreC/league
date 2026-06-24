"""
Entidad de dominio: PanelDocente
Representa el panel de retroalimentación pedagógica para el docente asesor de un equipo.
No contiene decoradores ORM ni dependencias de infraestructura.

Estado PRELIMINAR: torneo IN_PROGRESS con al menos 2 partidos FINISHED.
Estado DEFINITIVO:  torneo FINISHED con resultados DEFINITIVO.
"""
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class EstadoPanel(str, Enum):
    PRELIMINAR = "PRELIMINAR"
    DEFINITIVO = "DEFINITIVO"


class TipoRecomendacion(str, Enum):
    PRACTICA_DIRIGIDA = "PRACTICA_DIRIGIDA"   # percentil ≤ 25
    RECURSO = "RECURSO"                        # percentil 26–50
    METODOLOGIA = "METODOLOGIA"                # percentil > 50


@dataclass
class CriterioConPercentil:
    """
    Detalle de un criterio con posición percentil del equipo en el torneo.
    El percentil mide dónde se ubica el equipo respecto a todos los demás.
    """
    criterio_id: str
    criterio_nombre: str
    peso: float
    promedio_equipo: float
    promedio_torneo: float
    percentil: float        # 0–100: % de equipos con puntaje menor al de este equipo
    maximo_torneo: float
    minimo_torneo: float


@dataclass
class Recomendacion:
    """Recomendación pedagógica generada por el domain service."""
    criterio_id: str
    criterio_nombre: str
    tipo: TipoRecomendacion
    percentil: float
    descripcion: str        # Texto generado por el domain service
    acciones_sugeridas: list[str] = field(default_factory=list)


@dataclass
class PanelDocente:
    """
    Panel completo de retroalimentación para el docente asesor.
    Calculado en tiempo de consulta — no persiste en BD.
    """
    torneo_id: str
    torneo_nombre: str
    equipo_id: str
    equipo_nombre: str
    docente_asesor_id: str
    docente_nombre: str
    estado_panel: EstadoPanel
    advertencia: Optional[str]                          # Solo si PRELIMINAR
    posicion_final: Optional[int]
    medalla: Optional[str]
    puntaje_total_acumulado: float
    total_partidos_jugados: int
    criterios: list[CriterioConPercentil] = field(default_factory=list)
    recomendaciones: list[Recomendacion] = field(default_factory=list)
