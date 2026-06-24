"""
Puerto (interfaz) del repositorio de Análisis Integral.
El domain define el contrato; la infraestructura lo implementa.
No importa nada de application/ ni infrastructure/.
"""
from abc import ABC, abstractmethod
from typing import Optional
from ..entities.analisis_integral import AnalisisIntegral


class IAnalisisIntegralRepository(ABC):
    """
    Interfaz que todo repositorio concreto de análisis integral debe implementar.
    Las queries reales viven en infrastructure/repositories/analisis_integral_repository.py.
    """

    @abstractmethod
    def obtener_analisis(
        self,
        torneo_id: str,
        categoria: Optional[str] = None,
    ) -> Optional[AnalisisIntegral]:
        """
        Ejecuta la query principal (single roundtrip con CTEs) y retorna
        el análisis completo del torneo. Retorna None si no existen
        resultados con estado DEFINITIVO.
        """
        ...

    @abstractmethod
    def torneo_existe(self, torneo_id: str) -> bool:
        """Verifica si el torneo existe en la BD."""
        ...

    @abstractmethod
    def obtener_estado_torneo(self, torneo_id: str) -> Optional[str]:
        """
        Retorna el estado del torneo ('DRAFT' | 'IN_PROGRESS' | 'FINISHED')
        o None si no existe.
        """
        ...
