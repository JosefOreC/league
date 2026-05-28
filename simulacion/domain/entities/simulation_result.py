"""
Agregado de dominio: SimulationResult — HU-SIM-02, HU-SIM-03, HU-SIM-04, HU-SIM-05.

Contiene el resultado completo de una ejecución de simulación:
  scores         → calificación por criterio           (HU-SIM-02)
  puntaje_total  → suma ponderada de scores            (HU-SIM-02)
  posicion       → posición estimada en el torneo      (HU-SIM-03)
  fortalezas     → criterios con mejor desempeño       (HU-SIM-04)
  debilidades    → criterios con peor desempeño        (HU-SIM-04)
  retroalimentacion → texto accionable en español      (HU-SIM-05)
"""
from dataclasses import dataclass, field
from typing import List, Optional

from simulacion.domain.entities.criterion_score import CriterionScore


@dataclass(frozen=True)
class PosicionEstimada:
    """HU-SIM-03 — Posición final estimada en el torneo."""
    posicion_estimada: int
    total_equipos: int
    percentil: float
    advertencia: Optional[str] = None


@dataclass(frozen=True)
class FortalezaDebilidad:
    """HU-SIM-04 — Entrada de fortaleza o debilidad identificada."""
    criterio_id: str
    nombre: str
    valor_normalizado: float
    motivo: str


@dataclass(frozen=True)
class Retroalimentacion:
    """HU-SIM-05 — Texto de retroalimentación en español (es-PE)."""
    resumen: str
    recomendaciones: List[str] = field(default_factory=list)
    sin_mejoras_criticas: bool = False


@dataclass(frozen=True)
class SimulationResult:
    """
    Resultado completo de la simulación (HU-SIM-02 a HU-SIM-05).

    Attributes:
        simulation_id:    UUID determinista derivado del input (reproducible).
        scores:           Lista de CriterionScore, uno por criterio del torneo.
        puntaje_total:    Σ(valor_normalizado_i × peso_i / 100), redondeado a 2 dec.
        posicion:         Posición estimada en el torneo.
        fortalezas:       Hasta 3 criterios con mayor valor_normalizado.
        debilidades:      Hasta 3 criterios con menor valor_normalizado.
        retroalimentacion: Texto accionable en español.
    """
    simulation_id: str
    scores: List[CriterionScore]
    puntaje_total: float
    posicion: PosicionEstimada
    fortalezas: List[FortalezaDebilidad]
    debilidades: List[FortalezaDebilidad]
    retroalimentacion: Retroalimentacion
