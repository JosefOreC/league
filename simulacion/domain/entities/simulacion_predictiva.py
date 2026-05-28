from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SimulacionPredictivaEntity:
    participante_id: int
    torneo_id: int
    tiempo_estimado: float
    complejidad_codigo: int
    colisiones_historicas: int
    telemetria_velocidad_prom: float
    telemetria_errores: int
    telemetria_json: dict = field(default_factory=dict)
    puntaje_estimado: Optional[float] = None
    tiempo_probable_fin: Optional[float] = None
    rmse_validacion: Optional[float] = None
    modelo_version: str = 'v1'
    es_oficial: bool = False
