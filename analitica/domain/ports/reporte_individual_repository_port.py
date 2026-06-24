"""
Puerto (interfaz) del repositorio de Reporte Individual.
El domain define el contrato; la infraestructura lo implementa.
No importa nada de application/ ni infrastructure/.
"""
from abc import ABC, abstractmethod
from typing import Optional
from ..entities.reporte_individual import ReporteIndividual


class IReporteIndividualRepository(ABC):
    """
    Interfaz que todo repositorio concreto de reporte individual debe implementar.
    """

    @abstractmethod
    def obtener_reporte(
        self,
        torneo_id: str,
        equipo_id: str,
    ) -> Optional[ReporteIndividual]:
        """
        Ejecuta la query principal y retorna el reporte completo del equipo.
        Retorna None si el equipo no tiene resultados DEFINITIVO en el torneo.
        """
        ...

    @abstractmethod
    def obtener_estado_torneo(self, torneo_id: str) -> Optional[str]:
        """Retorna el estado del torneo o None si no existe."""
        ...

    @abstractmethod
    def equipo_pertenece_a_torneo(self, equipo_id: str, torneo_id: str) -> bool:
        """Verifica si el equipo está inscrito en el torneo."""
        ...

    @abstractmethod
    def obtener_representante_y_docente(
        self, equipo_id: str
    ) -> Optional[tuple[str, str]]:
        """
        Retorna (representante_id, docente_asesor_id) del equipo.
        Retorna None si el equipo no existe.
        """
        ...
