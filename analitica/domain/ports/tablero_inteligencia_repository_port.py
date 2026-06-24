"""
Puerto (interfaz) del repositorio de Tablero de Inteligencia.
El domain define el contrato; la infraestructura lo implementa.
No importa nada de application/ ni infrastructure/.
"""
from abc import ABC, abstractmethod
from typing import Optional
from ..entities.tablero_inteligencia import TableroInteligencia


class ITableroInteligenciaRepository(ABC):
    """
    Interfaz que todo repositorio concreto del tablero de inteligencia debe implementar.
    """

    @abstractmethod
    def obtener_tablero(self, torneo_id: str) -> Optional[TableroInteligencia]:
        """
        Ejecuta máximo 2 queries (métricas + alertas) y retorna el tablero completo.
        Retorna None si el torneo no existe.

        Tiempo de respuesta objetivo: < 1s.
        """
        ...

    @abstractmethod
    def obtener_estado_torneo(self, torneo_id: str) -> Optional[str]:
        """Retorna el estado del torneo o None si no existe."""
        ...
