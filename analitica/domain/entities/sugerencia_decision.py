from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class SugerenciaDecision:
    id: str
    torneo_id: str
    tipo: str               # REPROGRAMACION | AJUSTE_CRITERIO | APOYO_EQUIPO | OTRO
    descripcion: str
    accion_sugerida: str
    entidad_ref_id: str     # partido_id | criterio_id | equipo_id | ''
    severidad: str          # INFO | WARNING | ERROR
    estado: str             # PENDIENTE | ATENDIDA | DESCARTADA
    generado_en: str        # ISO 8601
