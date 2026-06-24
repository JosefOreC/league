from abc import ABC, abstractmethod
from typing import Optional
from ..entities.sugerencia_decision import SugerenciaDecision


class ISugerenciasRepository(ABC):

    @abstractmethod
    def obtener_estado_torneo(self, torneo_id: str) -> Optional[str]:
        """Retorna el state del torneo o None si no existe."""
        ...

    @abstractmethod
    def analizar_retrasos(self, torneo_id: str) -> list[dict]:
        """
        Retorna lista de dicts con info sobre partidos PENDING
        con fecha_programada vencida > 20 minutos.
        Formato: [{"total": int, "partido_ids": list[str]}]
        """
        ...

    @abstractmethod
    def analizar_criterios(self, torneo_id: str) -> list[dict]:
        """
        Retorna criterios con desviación estándar > 40 o < 2
        sobre valor_normalizado de resultados DEFINITIVE.
        Formato: [{"criterio_id": str, "criterio_nombre": str, "desv_est": float}]
        """
        ...

    @abstractmethod
    def analizar_equipos_bajo_rendimiento(self, torneo_id: str) -> list[dict]:
        """
        Retorna equipos en el percentil <= 10 del torneo (por puntaje_total_acumulado).
        Formato: [{"equipo_id": str, "equipo_nombre": str,
                   "puntaje": float, "criterios_debiles": list[str]}]
        """
        ...

    @abstractmethod
    def upsert_sugerencia(
        self,
        torneo_id: str,
        tipo: str,
        descripcion: str,
        accion_sugerida: str,
        entidad_ref_id: str,
        severidad: str,
    ) -> SugerenciaDecision:
        """
        Crea la sugerencia si no existe (por torneo_id+tipo+entidad_ref_id).
        Si existe como PENDIENTE actualiza la descripcion.
        Si existe como ATENDIDA o DESCARTADA no modifica nada.
        Retorna la entidad resultante.
        """
        ...

    @abstractmethod
    def obtener_pendientes(self, torneo_id: str) -> list[SugerenciaDecision]:
        """Retorna todas las sugerencias PENDIENTE del torneo."""
        ...
