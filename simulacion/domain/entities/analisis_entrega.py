from dataclasses import dataclass, field
from typing import List


@dataclass
class AnalisisEntregaEntity:
    reto_id: str
    participante_id: str
    torneo_id: str
    caso: str
    contenido_entrega: str
    calificaciones_por_criterio: List[dict]
    puntaje_total_simulado: float
    observacion_general: str = ''
