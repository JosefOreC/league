from dataclasses import dataclass, field
from typing import List


@dataclass
class SimulacionResultadoEntity:
    tournament_id: str
    equipo_id: str
    entregable: str
    scores: List[dict]
    puntaje_total: float
    posicion_estimada: int
    total_equipos: int
    percentil: float
    advertencia_muestra: str = ''
    fortalezas: List[dict] = field(default_factory=list)
    debilidades: List[dict] = field(default_factory=list)
    retro_resumen: str = ''
    retro_recomendaciones: List[str] = field(default_factory=list)
    sin_mejoras_criticas: bool = False
