from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CertificadoDigital:
    id: str
    torneo_id: str
    tipo_certificado: str           # PARTICIPACION | GANADOR | MENCION_ESPECIAL
    nombres_destinatario: str
    institucion: str
    codigo_verificacion: str
    generado_en: str                # ISO 8601
    participante_id: Optional[str] = None
    equipo_id: Optional[str] = None
    posicion_final: Optional[int] = None
    medalla: Optional[str] = None


@dataclass(frozen=True)
class DatosParticipante:
    participante_id: str
    nombres: str
    apellidos: str
    autorizacion_datos: bool
    equipo_id: str
    equipo_nombre: str
    institucion_nombre: str
    torneo_nombre: str
    torneo_fecha: str


@dataclass(frozen=True)
class DatosGanador:
    equipo_id: str
    equipo_nombre: str
    institucion_nombre: str
    torneo_nombre: str
    torneo_fecha: str
    posicion_final: int
    puntaje_total_acumulado: float
    medalla: str
    mencion_especial: str
    participantes: list            # list[tuple[str, str]] = [(nombres, apellidos), ...]
