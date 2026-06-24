from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class EquipoPodio:
    equipo_id: str
    nombre: str
    institucion: str
    posicion_final: int
    puntaje: float
    medalla: str


@dataclass(frozen=True)
class MetricasResumen:
    """Datos numéricos reales extraídos del torneo para insertar en el texto."""
    torneo_nombre: str
    fecha_inicio: str
    fecha_fin: str
    sede: str
    total_equipos: int
    total_instituciones: int
    total_participantes: int
    podio: list                       # list[EquipoPodio] (hasta 3)
    criterio_determinante: str
    puntaje_promedio_global: float
    nivel_competencia: str            # ALTO | MEDIO | HOMOGENEO
    recomendaciones: list             # list[str]

    @property
    def campeon(self) -> Optional[EquipoPodio]:
        for e in self.podio:
            if e.posicion_final == 1:
                return e
        return self.podio[0] if self.podio else None


@dataclass(frozen=True)
class ResumenEjecutivo:
    id: str
    torneo_id: str
    resumen_texto: str
    tono: str                         # FORMAL | DIVULGATIVO | CELEBRATORIO
    version: int
    metricas_usadas: dict
    generado_en: str
