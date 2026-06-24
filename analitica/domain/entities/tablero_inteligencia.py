"""
Entidad de dominio: TableroInteligencia
Representa el tablero en tiempo real del organizador.
Funciona en estado IN_PROGRESS Y FINISHED — no es exclusivo de torneos finalizados.
No contiene decoradores ORM ni dependencias de infraestructura.
"""
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class SeveridadAlerta(str, Enum):
    INFO = "INFO"
    ADVERTENCIA = "ADVERTENCIA"
    ERROR = "ERROR"


class TipoAlerta(str, Enum):
    PARTIDO_RETRASADO = "PARTIDO_RETRASADO"
    CAMBIO_TOP3 = "CAMBIO_TOP3"
    SIN_RESULTADOS = "SIN_RESULTADOS"


@dataclass
class AlertaActiva:
    """Alerta generada por el sistema de inteligencia del torneo."""
    tipo: TipoAlerta
    severidad: SeveridadAlerta
    mensaje: str
    entidad_ref_id: Optional[str] = None    # ID del partido o equipo afectado
    minutos_retraso: Optional[int] = None   # Solo para PARTIDO_RETRASADO


@dataclass
class EstadoEquipoTablero:
    """Snapshot del estado de un equipo en el tablero."""
    equipo_id: str
    equipo_nombre: str
    posicion_actual: int
    puntaje_acumulado: float
    partidos_jugados: int
    victorias: int
    medalla: Optional[str] = None           # Solo si torneo está FINISHED


@dataclass
class PartidoEnCurso:
    """Partido pendiente o en progreso."""
    partido_id: str
    ronda: int
    equipo_local_id: str
    equipo_local_nombre: str
    equipo_visitante_id: Optional[str]
    equipo_visitante_nombre: Optional[str]
    estado: str
    fecha_programada: Optional[str]         # ISO string
    minutos_retraso: Optional[int] = None   # > 0 si está retrasado


@dataclass
class TableroInteligencia:
    """
    Tablero de inteligencia del organizador.
    Calculado en tiempo de consulta — no persiste en BD.
    Disponible en IN_PROGRESS y FINISHED.
    """
    torneo_id: str
    torneo_nombre: str
    estado_torneo: str
    total_equipos: int
    total_partidos: int
    partidos_finalizados: int
    partidos_pendientes: int
    partidos_en_progreso: int
    porcentaje_avance: float                # partidos_finalizados / total_partidos * 100
    top_3: list[EstadoEquipoTablero] = field(default_factory=list)
    partidos_proximos: list[PartidoEnCurso] = field(default_factory=list)
    alertas_activas: list[AlertaActiva] = field(default_factory=list)
