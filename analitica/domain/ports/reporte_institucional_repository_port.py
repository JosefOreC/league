from abc import ABC, abstractmethod
from typing import Optional
from ..entities.reporte_institucional import ReporteInstitucional, ReporteInstitucionalHistorico


class IReporteInstitucionalRepository(ABC):

    @abstractmethod
    def obtener_estado_torneo(self, torneo_id: str) -> Optional[str]:
        """Retorna el state del torneo o None si no existe."""
        ...

    @abstractmethod
    def institucion_existe(self, inst_id: str) -> bool:
        """True si la institución existe en la BD."""
        ...

    @abstractmethod
    def obtener_reporte_torneo(
        self, inst_id: str, torneo_id: str
    ) -> Optional[ReporteInstitucional]:
        """
        Query principal con JOIN.
        Retorna None si la institución no tiene equipos APROBADO en el torneo.
        """
        ...

    @abstractmethod
    def obtener_reporte_historico(
        self, inst_id: str
    ) -> Optional[ReporteInstitucionalHistorico]:
        """
        Query con JOIN sobre todos los torneos finalized donde participó la institución.
        Retorna None si no hay torneos finalizados con participación.
        """
        ...
