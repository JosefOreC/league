from abc import ABC, abstractmethod
from typing import Optional
from ..entities.resumen_ejecutivo import ResumenEjecutivo, MetricasResumen


class IResumenEjecutivoRepository(ABC):

    @abstractmethod
    def obtener_estado_torneo(self, torneo_id: str) -> Optional[str]:
        """Retorna el state del torneo o None si no existe."""
        ...

    @abstractmethod
    def existen_resultados_definitivos(self, torneo_id: str) -> bool:
        """True si hay al menos un MatchResult con estado_resultado='DEFINITIVE'."""
        ...

    @abstractmethod
    def obtener_metricas(self, torneo_id: str) -> Optional[MetricasResumen]:
        """
        Recopila las métricas reales del torneo (equipos, instituciones,
        participantes, podio, criterio determinante, nivel de competencia).
        Las recomendaciones se inyectan aparte por el use case.
        Retorna None si no hay datos suficientes.
        """
        ...

    @abstractmethod
    def siguiente_version(self, torneo_id: str) -> int:
        """Retorna el siguiente número de versión (max actual + 1, o 1 si no existe)."""
        ...

    @abstractmethod
    def guardar(
        self,
        torneo_id: str,
        resumen_texto: str,
        tono: str,
        version: int,
        metricas_usadas: dict,
    ) -> ResumenEjecutivo:
        """Persiste el resumen como nueva versión (conserva las anteriores)."""
        ...
